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

from .adf import substitute_markers, substitute_media
from .attachments import upload_diagrams
from .env import get_confluence, load_credentials
from .mermaid import extract_mermaid, render_diagrams
from .patterns import HEADING_RE, strip_ignored_sections
from .rest_publish import adf_body_size, create_page_adf, get_page_version, update_page_adf

_CONVERTER_SCRIPT = Path(__file__).resolve().parents[3] / "map-markdown-adf" / "scripts" / "map_markdown_adf.py"


def resolve_title(md_text: str, explicit: str | None) -> str:
    """Explicit title wins; else the first '#' heading; else a ValueError naming --title."""
    if explicit:
        return explicit
    match = HEADING_RE.search(md_text)
    if match:
        return match.group(2).strip()
    raise ValueError("no title resolved: pass --title or add a '#' heading to the Markdown")


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


def try_load_credentials(root: str) -> dict[str, str] | None:
    """Non-fatal probe: `None` when `.atlassian` is missing/incomplete, never raises."""
    try:
        return load_credentials(root)
    except SystemExit:
        return None


def _diagram_note_node(name: str) -> dict:
    return {
        "type": "paragraph",
        "content": [
            {
                "type": "text",
                "text": f"[Diagram '{name}' not rendered: ATLASSIAN_API_TOKEN is not configured]",
            }
        ],
    }


def substitute_diagram_notes(adf: dict, diagrams: list[dict]) -> tuple[dict, int]:
    """Replace every marker paragraph with a note naming the missing token prerequisite."""
    names_by_index = {str(d["index"]): d["name"] for d in diagrams}
    return substitute_markers(adf, lambda index: _diagram_note_node(names_by_index[index]))


def _publish_with_diagrams(
    base_adf: dict,
    diagrams: list[dict],
    credentials: dict[str, str],
    page_id: str | None,
    space_id: str | None,
    title: str,
    assets_dir: str,
    mermaid_bg: str,
) -> tuple[dict, dict]:
    confluence = get_confluence(credentials)

    if page_id:
        target_page_id = page_id
    else:
        placeholder_adf = copy.deepcopy(base_adf)
        substitute_diagram_notes(placeholder_adf, diagrams)
        created = create_page_adf(confluence, space_id, title, placeholder_adf)
        target_page_id = created["id"]

    render_diagrams(diagrams, assets_dir, background=mermaid_bg)
    filename_to_file_id = upload_diagrams(confluence, target_page_id, diagrams)
    media_ids_by_index = {str(d["index"]): filename_to_file_id[d["filename"]] for d in diagrams}
    final_adf, _ = substitute_media(base_adf, media_ids_by_index, target_page_id)

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
    threshold_bytes: int,
) -> tuple[dict, dict]:
    size_bytes = adf_body_size(base_adf)

    if size_bytes <= threshold_bytes:
        result = {
            "method": "mcp",
            "sizeBytes": size_bytes,
            "pageId": page_id,
            "spaceId": space_id,
            "title": title,
            "diagramsRendered": 0,
        }
        return result, base_adf

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
        "sizeBytes": size_bytes,
        "diagrams": 0,
        "attachments": 0,
    }
    return result, base_adf


def _publish_without_credentials(
    base_adf: dict,
    diagrams: list[dict],
    page_id: str | None,
    space_id: str | None,
    title: str,
) -> tuple[dict, dict]:
    result = {
        "method": "mcp",
        "pageId": page_id,
        "spaceId": space_id,
        "title": title,
        "diagramsRendered": 0,
    }
    if diagrams:
        final_adf, _ = substitute_diagram_notes(base_adf, diagrams)
        result["missingPrerequisite"] = "ATLASSIAN_API_TOKEN"
    else:
        final_adf = base_adf
    result["sizeBytes"] = adf_body_size(final_adf)
    return result, final_adf


def publish(
    md_path: str,
    root: str,
    page_id: str | None,
    space_id: str | None,
    title: str | None,
    assets_dir: str,
    out_path: str,
    threshold_bytes: int,
    mermaid_bg: str = "white",
) -> dict:
    """Run extract -> md-to-adf -> create/attach -> substitute -> publish end to end.

    Forces a REST publish whenever diagrams are present and credentials are configured
    — attachment upload already needs the REST client, so publishing over it too is
    free regardless of `threshold_bytes`. Always writes the final ADF to `out_path`,
    pretty-printed (`json.dump(..., indent=2)`) so it stays readable through
    line-truncating file readers.
    """
    md_text = Path(md_path).read_text(encoding="utf-8")
    resolved_title = resolve_title(md_text, title)
    processed = strip_ignored_sections(md_text)
    processed, diagrams = extract_mermaid(processed)
    base_adf = convert_markdown_to_adf(processed)

    credentials = try_load_credentials(root)

    if credentials and diagrams:
        result, final_adf = _publish_with_diagrams(
            base_adf, diagrams, credentials, page_id, space_id, resolved_title, assets_dir, mermaid_bg
        )
    elif credentials:
        result, final_adf = _publish_text_only(
            base_adf, credentials, page_id, space_id, resolved_title, threshold_bytes
        )
    else:
        result, final_adf = _publish_without_credentials(base_adf, diagrams, page_id, space_id, resolved_title)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_adf, f, indent=2)
        f.write("\n")
    result["adfPath"] = out_path
    return result
