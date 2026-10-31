"""Full publish pipeline: extract -> md-to-adf -> create/attach -> substitute -> publish,
run end to end by `run` (see cli.py). Diagram conversion lives in the sibling
`map-markdown-adf` skill; Concept 0009 forbids importing its code across skill folders,
so `convert_markdown_to_adf` shells out to its CLI as a subprocess instead of importing
`converter.*` directly.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from atlassian.errors import ApiError
from requests.exceptions import RequestException

from . import comment_guard
from .adf import attachment_node, drawio_node, media_node, substitute_drawio, substitute_markers
from .attachments import upload_diagrams, upload_files
from .custom_content import upsert_diagram
from .env import (
    get_confluence,
    load_credentials,
    load_drawio_extension_key,
    load_renderer,
    load_swimlane_drawio_enabled,
    site_url,
)
from .local_media import extract_local_media
from .mermaid import extract_mermaid, render_diagrams
from .patterns import HEADING_RE, strip_ignored_sections
from .rest_publish import adf_body_size, create_page_adf, get_page_version, update_page_adf
from . import renderers

_CONVERTER_SCRIPT = Path(__file__).resolve().parents[3] / "map-markdown-adf" / "scripts" / "map_markdown_adf.py"


def resolve_title(md_text: str, explicit: str | None) -> str:
    """Explicit title wins; else the first '#' heading; else a ValueError naming --title."""
    if explicit:
        return explicit
    match = HEADING_RE.search(md_text)
    if match:
        return match.group(2).strip()
    raise ValueError("no title resolved: pass --title or add a '#' heading to the Markdown")


def strip_title_heading(adf: dict) -> dict:
    """Drop a leading level-1 heading: Confluence renders the page title itself, so keeping
    it would show the title twice. `fetch-page` re-adds it as `# <title>` on the way back."""
    content = adf.get("content", [])
    if content and content[0].get("type") == "heading" and content[0].get("attrs", {}).get("level") == 1:
        content = content[1:] or [{"type": "paragraph", "content": []}]
        return {**adf, "content": content}
    return adf


def convert_markdown_to_adf(processed_md: str) -> dict:
    """Convert Markdown to ADF via the sibling `map-markdown-adf` skill's CLI, as a
    subprocess — Concept 0009 forbids importing its `converter.*` code directly.
    """
    try:
        result = subprocess.run(
            [sys.executable, str(_CONVERTER_SCRIPT), "md-to-adf"],
            input=processed_md,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"map-markdown-adf md-to-adf failed: {e.stderr.strip()}") from e
    return json.loads(result.stdout)


def _diagram_note_node(name: str) -> dict:
    return {
        "type": "paragraph",
        "content": [
            {
                "type": "text",
                "text": f"[Diagram '{name}' upload pending]",
            }
        ],
    }


def substitute_diagram_notes(
    adf: dict, diagrams: list[dict], local_media: list[dict] | None = None
) -> tuple[dict, int]:
    """Replace every marker paragraph with a placeholder note until its upload lands."""
    names_by_index = {str(d["index"]): d["name"] for d in diagrams}
    if local_media:
        names_by_index.update({str(m["index"]): m["filename"] for m in local_media})
    return substitute_markers(adf, lambda index: _diagram_note_node(names_by_index[index]))


def _drawio_nodes_by_index(
    confluence, page_id: str, diagrams: list[dict], extension_key: str, base_url: str
) -> dict[str, dict]:
    """Register each rendered diagram as custom content and build its macro node.

    Runs after the attachments are uploaded — the macro points at a `.drawio` file that has
    to already be on the page for the app to have anything to open. Skips diagrams Draw.io
    could not import: those fell back to a PNG and have no custom content to register.
    """
    nodes: dict[str, dict] = {}
    for d in diagrams:
        if d["renderer"] != renderers.DRAWIO:
            continue
        content = upsert_diagram(confluence, page_id, d["diagram_name"], d["search"])
        nodes[str(d["index"])] = drawio_node(
            extension_key=extension_key,
            page_id=page_id,
            cust_content_id=content["id"],
            diagram_name=d["diagram_name"],
            width=d["width"],
            height=d["height"],
            base_url=base_url,
            revision=content["revision"],
        )
    return nodes


def _publish_with_diagrams(
    base_adf: dict,
    diagrams: list[dict],
    local_media: list[dict],
    credentials: dict[str, str],
    page_id: str | None,
    space_id: str | None,
    title: str,
    assets_dir: str,
    mermaid_bg: str,
    renderer: str,
    drawio_extension_key: str | None,
    swimlane_drawio_enabled: bool,
) -> tuple[dict, dict]:
    confluence = get_confluence(credentials)

    if page_id:
        target_page_id = page_id
    else:
        placeholder_adf = copy.deepcopy(base_adf)
        substitute_diagram_notes(placeholder_adf, diagrams, local_media)
        created = create_page_adf(confluence, space_id, title, placeholder_adf)
        target_page_id = created["id"]

    if diagrams:
        render_diagrams(
            diagrams,
            assets_dir,
            background=mermaid_bg,
            renderer=renderer,
            swimlane_drawio_enabled=swimlane_drawio_enabled,
        )
    filename_to_file_id = upload_diagrams(confluence, target_page_id, diagrams)
    filename_to_file_id.update(
        upload_files(
            confluence,
            target_page_id,
            [{"path": m["path"], "filename": m["filename"]} for m in local_media],
        )
    )

    local_media_nodes = {
        str(m["index"]): (
            media_node(
                filename_to_file_id[m["filename"]],
                target_page_id,
                alt=m["filename"],
                width_height=(m["width"], m["height"]) if "width" in m else None,
            )
            if m["is_image"]
            else attachment_node(filename_to_file_id[m["filename"]], target_page_id)
        )
        for m in local_media
    }

    if renderer == renderers.DRAWIO:
        nodes_by_index = _drawio_nodes_by_index(
            confluence, target_page_id, diagrams, drawio_extension_key, f"{site_url(credentials)}/wiki"
        )
        for d in diagrams:
            if d["renderer"] != renderers.DRAWIO:
                nodes_by_index[str(d["index"])] = media_node(
                    filename_to_file_id[d["filename"]], target_page_id
                )
    else:
        nodes_by_index = {
            str(d["index"]): media_node(filename_to_file_id[d["filename"]], target_page_id) for d in diagrams
        }
    nodes_by_index.update(local_media_nodes)
    final_adf, _ = substitute_drawio(base_adf, nodes_by_index)

    version = get_page_version(confluence, target_page_id)
    update_page_adf(confluence, target_page_id, title, final_adf, version)

    result = {
        "method": "rest",
        "pageId": target_page_id,
        "title": title,
        "sizeBytes": adf_body_size(final_adf),
        "diagrams": len(diagrams),
        "attachments": len(filename_to_file_id),
    }
    return result, final_adf


def _publish_text_only(
    base_adf: dict,
    credentials: dict[str, str],
    page_id: str | None,
    space_id: str | None,
    title: str,
) -> tuple[dict, dict]:
    confluence = get_confluence(credentials)
    if page_id:
        version = get_page_version(confluence, page_id)
        update_page_adf(confluence, page_id, title, base_adf, version)
        target_page_id = page_id
    else:
        created = create_page_adf(confluence, space_id, title, base_adf)
        target_page_id = created["id"]

    result = {
        "method": "rest",
        "pageId": target_page_id,
        "title": title,
        "sizeBytes": adf_body_size(base_adf),
        "diagrams": 0,
        "attachments": 0,
    }
    return result, base_adf


_GUARD_ERRORS = (RequestException, ApiError, ValueError)


def _plan_comment_guard(credentials: dict[str, str], page_id: str | None, final_adf: dict) -> tuple[dict | None, dict]:
    """Read which open inline comments this update will detach; never blocks the publish."""
    if not page_id:
        return None, {}
    try:
        return comment_guard.plan(get_confluence(credentials), page_id, final_adf), {}
    except _GUARD_ERRORS as exception:
        return None, {"commentGuard": f"failed ({type(exception).__name__})"}


def _apply_comment_guard(guard: dict, credentials: dict[str, str], page_id: str) -> dict:
    """After the publish: post one notice listing the comments the update detached."""
    keys: dict = {}
    if guard["unknownIds"]:
        keys["unknownCommentIds"] = guard["unknownIds"]
    if not guard["orphaned"]:
        return keys
    keys["orphanedComments"] = [{k: c[k] for k in ("id", "markerRef", "selection")} for c in guard["orphaned"]]
    storage = comment_guard.notice_storage(guard["orphaned"], f"{site_url(credentials)}/wiki")
    try:
        keys["orphanNoticeCommentId"] = comment_guard.post_notice(get_confluence(credentials), page_id, storage)
    except _GUARD_ERRORS as exception:
        keys["commentGuard"] = f"notice failed ({type(exception).__name__})"
    return keys


def publish(
    md_path: str,
    config_path: str,
    page_id: str | None,
    space_id: str | None,
    title: str | None,
    assets_dir: str,
    out_path: str,
    mermaid_bg: str = "white",
) -> dict:
    """Run extract -> md-to-adf -> create/attach -> substitute -> publish end to end, always
    over REST. Credentials are mandatory; a missing key raises `SystemExit` naming it before
    any page is touched. Always writes the final ADF to `out_path`, pretty-printed
    (`json.dump(..., indent=2)`) so it stays readable through line-truncating file readers.
    """
    renderer = load_renderer(config_path)
    swimlane_drawio_enabled = load_swimlane_drawio_enabled(config_path)

    md_text = Path(md_path).read_text(encoding="utf-8")
    resolved_title = resolve_title(md_text, title)
    processed = strip_ignored_sections(md_text)
    processed, diagrams = extract_mermaid(processed)
    processed, local_media = extract_local_media(processed, Path(md_path).parent, start_index=len(diagrams))
    base_adf = strip_title_heading(convert_markdown_to_adf(processed))

    # A page with only local attachments and no mermaid fence must not be blocked by an
    # unrelated/unusable diagramRenderer setting.
    drawio_extension_key = None
    if diagrams:
        unavailable = renderers.unavailable_reason(renderer)
        if unavailable:
            raise RuntimeError(unavailable)
        # Resolved up front so a missing key fails before any page is created or updated.
        drawio_extension_key = load_drawio_extension_key(config_path) if renderer == renderers.DRAWIO else None

    credentials = load_credentials(config_path)
    guard, guard_keys = _plan_comment_guard(credentials, page_id, base_adf)

    if diagrams or local_media:
        result, final_adf = _publish_with_diagrams(
            base_adf,
            diagrams,
            local_media,
            credentials,
            page_id,
            space_id,
            resolved_title,
            assets_dir,
            mermaid_bg,
            renderer,
            drawio_extension_key,
            swimlane_drawio_enabled,
        )
    else:
        result, final_adf = _publish_text_only(base_adf, credentials, page_id, space_id, resolved_title)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_adf, f, indent=2)
        f.write("\n")
    result["renderer"] = renderer
    result["adfPath"] = out_path
    result.update(guard_keys)
    if guard is not None:
        result.update(_apply_comment_guard(guard, credentials, page_id))
    return result
