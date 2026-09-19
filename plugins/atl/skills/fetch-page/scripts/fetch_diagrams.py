"""Cache a fetched page's attachments to disk and resolve its diagram/attachment placeholders
(I/O: Confluence REST via `atlassian-python-api` — the one thing the Atlassian MCP does not
expose for attachment content).

`/map-markdown-adf`'s `adf-to-md` turns every Draw.io macro into a `<!-- adf:diagram
drawio="<name>" -->` placeholder, and every `media`/`mediaSingle`/`mediaGroup` node into a
neutral `<!-- adf:attachment media-id="<id>" alt="<alt>" -->` placeholder (see its SKILL.md's
mapping table). This module classifies and resolves each one:
1. A `{name}.source.mmd` sidecar exists (a `/publish-page`-rendered diagram, drawio-macro or
   media-based) -> inline the verbatim ```mermaid fence (see publish-page's "Round-trip
   sidecar" section).
2. No sidecar, the file looks like an image -> a Markdown image reference.
3. No sidecar, not an image -> a plain Markdown link.
Rules 2 and 3 point at the copy `save_attachments` cached under the page's `.tmp/` assets dir.

Every failure mode degrades to a one-line note instead of raising — a missing sidecar/attachment
(the page predates the sidecar, or was never republished) or a missing token never fails the
rest of the fetch.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import quote

from atlassian import Confluence

from env import get_confluence, load_credentials

_DRAWIO_PLACEHOLDER_RE = re.compile(r'<!-- adf:diagram drawio="([^"]*)" -->')
_ATTACHMENT_PLACEHOLDER_RE = re.compile(r'<!-- adf:attachment media-id="([^"]*)" alt="([^"]*)" -->')
_ANY_PLACEHOLDER_RE = re.compile(r"<!-- adf:(diagram|attachment) ")

NO_TOKEN_NOTE = "<!-- adf:diagram source unavailable: set ATLASSIAN_API_TOKEN to restore it -->"

_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp")


def _looks_like_image(name: str) -> bool:
    return name.lower().endswith(_IMAGE_EXTENSIONS)


def has_diagram_placeholder(markdown: str) -> bool:
    return bool(_ANY_PLACEHOLDER_RE.search(markdown))


def find_attachment_reference_nodes(node: object) -> list[dict]:
    """Recursively scan a raw ADF (sub)tree for nodes that reference an attached file: a
    generic-file `media` node, an image `media` node (its `alt` names an image file), or a
    Draw.io `extension` macro. Pure/offline, no REST — used only to decide whether it's worth
    touching Confluence attachments at all.
    """
    found: list[dict] = []
    if isinstance(node, dict):
        node_type = node.get("type")
        attrs = node.get("attrs") or {}
        if node_type == "media":
            if attrs.get("type") == "file" or _looks_like_image(attrs.get("alt", "")):
                found.append(node)
        elif node_type == "extension" and "drawio" in attrs.get("extensionKey", ""):
            found.append(node)
        for value in node.values():
            found.extend(find_attachment_reference_nodes(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(find_attachment_reference_nodes(item))
    return found


def has_attachment_reference(body: dict) -> bool:
    return bool(find_attachment_reference_nodes(body))


def _sidecar_title(diagram_filename: str) -> str:
    """`{name}.drawio` / `{name}.png` -> `{name}.source.mmd`."""
    stem = diagram_filename.rsplit(".", 1)[0]
    return f"{stem}.source.mmd"


def list_attachments(confluence: Confluence, page_id: str) -> list[dict]:
    resp = confluence.get_attachments_from_content(page_id, limit=200, expand="extensions.fileId")
    return resp.get("results", [])


def _find_by_title(attachments: list[dict], title: str) -> dict | None:
    return next((a for a in attachments if a.get("title") == title), None)


def _find_by_file_id(attachments: list[dict], file_id: str) -> dict | None:
    return next((a for a in attachments if a.get("extensions", {}).get("fileId") == file_id), None)


def download_attachment_bytes(confluence: Confluence, attachment: dict) -> bytes:
    """Like `_download_text` but always bytes, so binary attachments (`.png`, `.drawio`) aren't
    corrupted by a text decode."""
    content = confluence.get(attachment["_links"]["download"], not_json_response=True)
    return content if isinstance(content, bytes) else content.encode("utf-8")


def _download_text(confluence: Confluence, attachment: dict) -> str:
    content = confluence.get(attachment["_links"]["download"], not_json_response=True)
    return content.decode("utf-8") if isinstance(content, bytes) else content


def save_attachments(confluence: Confluence, page_id: str, assets_dir: str) -> dict[str, bytes]:
    """Download every attachment on the page once and cache it under `assets_dir` (created only
    when the page actually has attachments), returning `{title: bytes}` so callers can resolve
    placeholders from memory instead of a second network round-trip.
    """
    attachments = list_attachments(confluence, page_id)
    if not attachments:
        return {}
    Path(assets_dir).mkdir(parents=True, exist_ok=True)
    downloaded: dict[str, bytes] = {}
    for attachment in attachments:
        content = download_attachment_bytes(confluence, attachment)
        downloaded[attachment["title"]] = content
        (Path(assets_dir) / attachment["title"]).write_bytes(content)
    return downloaded


def _relative_link(assets_dir_name: str, filename: str) -> str:
    """Percent-encoded path relative to the Markdown file's own directory, e.g.
    `page.md.tmp/Screenshot%202026-02-10%20113535.png`."""
    return f"{assets_dir_name}/{quote(filename)}"


def _missing_sidecar_note(sidecar_title: str) -> str:
    return (
        f'<!-- adf:diagram source unavailable: "{sidecar_title}" not attached to this page; '
        "republish with /publish-page to enable round-trip -->"
    )


def _fence(source: str) -> str:
    return f"```mermaid\n{source.rstrip(chr(10))}\n```"


def restore_diagrams(
    confluence: Confluence,
    page_id: str,
    markdown: str,
    downloaded: dict[str, bytes],
    assets_dir_name: str,
) -> str:
    """Substitute every `<!-- adf:diagram ... -->` / `<!-- adf:attachment ... -->` placeholder:
    a mermaid fence when a `{name}.source.mmd` sidecar exists, else a Markdown image or a plain
    link into `assets_dir_name`. Reuses `downloaded` (from `save_attachments`) instead of
    re-fetching bytes already in hand; only falls back to a fresh download when a title isn't in
    it (e.g. a caller that didn't run `save_attachments` first).
    """
    if not has_diagram_placeholder(markdown):
        return markdown

    attachments = list_attachments(confluence, page_id)

    def _sidecar_text(sidecar_title: str) -> str | None:
        content = downloaded.get(sidecar_title)
        if content is not None:
            return content.decode("utf-8") if isinstance(content, bytes) else content
        sidecar = _find_by_title(attachments, sidecar_title)
        if sidecar is None:
            return None
        return _download_text(confluence, sidecar)

    def _replace_drawio(match: re.Match) -> str:
        sidecar_title = _sidecar_title(match.group(1))
        text = _sidecar_text(sidecar_title)
        if text is None:
            return _missing_sidecar_note(sidecar_title)
        return _fence(text)

    def _replace_attachment(match: re.Match) -> str:
        media_id, alt = match.group(1), match.group(2)
        attachment = _find_by_file_id(attachments, media_id)
        if attachment is None:
            return f'<!-- adf:diagram source unavailable: attachment for media-id="{media_id}" not found -->'
        filename = attachment["title"]
        sidecar_title = _sidecar_title(filename)
        text = _sidecar_text(sidecar_title)
        if text is not None:
            return _fence(text)
        link = _relative_link(assets_dir_name, filename)
        if _looks_like_image(filename) or _looks_like_image(alt):
            return f"![{alt or filename}]({link})"
        return f"[{filename}]({link})"

    markdown = _DRAWIO_PLACEHOLDER_RE.sub(_replace_drawio, markdown)
    markdown = _ATTACHMENT_PLACEHOLDER_RE.sub(_replace_attachment, markdown)
    return markdown


def restore_diagrams_without_credentials(markdown: str) -> str:
    """Degraded mode: no token configured, so every placeholder gets a note instead of a fence."""
    markdown = _DRAWIO_PLACEHOLDER_RE.sub(NO_TOKEN_NOTE, markdown)
    markdown = _ATTACHMENT_PLACEHOLDER_RE.sub(NO_TOKEN_NOTE, markdown)
    return markdown


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Restore mermaid fences from a fetched page's diagram placeholders."
    )
    parser.add_argument("--page-id", required=True, help="Confluence pageId the Markdown was fetched from")
    parser.add_argument("--root", required=True, help="Harness Repo Path to bound the `.atlassian` search to")
    parser.add_argument("--assets-dir", required=True, help="Directory to cache this page's attachments into")
    args = parser.parse_args()

    markdown = sys.stdin.read()
    if not has_diagram_placeholder(markdown):
        sys.stdout.write(markdown)
        return

    credentials = load_credentials(args.root)
    if credentials is None:
        sys.stdout.write(restore_diagrams_without_credentials(markdown))
        return

    confluence = get_confluence(credentials)
    downloaded = save_attachments(confluence, args.page_id, args.assets_dir)
    sys.stdout.write(
        restore_diagrams(confluence, args.page_id, markdown, downloaded, Path(args.assets_dir).name)
    )


if __name__ == "__main__":
    main()
