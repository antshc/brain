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
Rules 2 and 3 point at the copy `fetch_attachment_snapshot`/`publish_attachment_cache` cached
under the page's `.tmp/` assets dir.

Attachment metadata and bytes are fetched exactly once per assembly, via
`fetch_attachment_snapshot`, and reused by both cache publication and placeholder resolution.
Cache publication is atomic (`publish_attachment_cache`): every download and disk write happens
into a staging directory first, and only a fully-written staging directory ever replaces the
live cache, so a failed refresh never leaves a partial cache and never damages a prior complete
one. Every failure mode raises `AttachmentRetrievalError` carrying only a safe exception
category (its class name) — never the original exception text, which may hold a signed media
URL or an auth token; callers degrade to a one-line note instead of failing the whole fetch.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

from atlassian import Confluence
from requests.exceptions import RequestException

from env import get_confluence, load_credentials

_DRAWIO_PLACEHOLDER_RE = re.compile(r'<!-- adf:diagram drawio="([^"]*)" -->')
_ATTACHMENT_PLACEHOLDER_RE = re.compile(
    r'<!-- adf:attachment media-id="([^"]*)" alt="([^"]*)"(?: width="(\d+)" height="(\d+)")? -->'
)
_ANY_PLACEHOLDER_RE = re.compile(r"<!-- adf:(diagram|attachment) ")

NO_TOKEN_NOTE = "<!-- adf:diagram source unavailable: set ATLASSIAN_API_TOKEN to restore it -->"
SKIPPED_NOTE = "<!-- adf:diagram source unavailable: attachment retrieval skipped (--attachments skip) -->"

_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp")


class AttachmentRetrievalError(Exception):
    """Listing, downloading, or cache-publishing page attachments failed. The message is always
    a short, safe category (an exception class name, or a fixed reason string) — never the
    original exception text, which may carry a signed media URL, a query token, or other
    credential-like material.
    """


@dataclass(frozen=True)
class AttachmentSnapshot:
    """Every attachment on the page, listed and downloaded exactly once."""

    attachments: list[dict]
    downloaded: dict[str, bytes]


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


def _find_by_file_id(attachments: list[dict], file_id: str) -> dict | None:
    return next((a for a in attachments if a.get("extensions", {}).get("fileId") == file_id), None)


def download_attachment_bytes(confluence: Confluence, attachment: dict) -> bytes:
    """Always bytes, so binary attachments (`.png`, `.drawio`) aren't corrupted by a text decode."""
    content = confluence.get(attachment["_links"]["download"], not_json_response=True)
    return content if isinstance(content, bytes) else content.encode("utf-8")


def fetch_attachment_snapshot(confluence: Confluence, page_id: str) -> AttachmentSnapshot:
    """List every attachment on the page and download every attachment's bytes, once. Any TLS,
    timeout, HTTP, or connection failure raises `AttachmentRetrievalError` naming only the
    exception's class.
    """
    try:
        attachments = list_attachments(confluence, page_id)
        downloaded = {a["title"]: download_attachment_bytes(confluence, a) for a in attachments}
    except RequestException as exception:
        raise AttachmentRetrievalError(type(exception).__name__) from None
    return AttachmentSnapshot(attachments=attachments, downloaded=downloaded)


def _publish_staged_directory(staging_path: Path, target_path: Path) -> None:
    """Atomically swap `staging_path` in as `target_path`. A prior `target_path` is renamed aside
    first and only removed once the swap succeeds; any failure restores it.
    """
    backup_path: Path | None = None
    if target_path.exists():
        backup_path = target_path.parent / f"{target_path.name}.bak-{uuid4().hex}"
        target_path.rename(backup_path)
    try:
        staging_path.rename(target_path)
    except OSError:
        if backup_path is not None:
            backup_path.rename(target_path)
        raise
    else:
        if backup_path is not None:
            shutil.rmtree(backup_path, ignore_errors=True)


def publish_attachment_cache(snapshot: AttachmentSnapshot, assets_dir: str) -> None:
    """Write every already-downloaded attachment into a sibling staging directory, then publish
    it in place of `assets_dir` only once every file is written. On any failure the staging
    directory is removed and `assets_dir` (a prior complete cache, if any) is left untouched.
    """
    if not snapshot.attachments:
        return
    assets_path = Path(assets_dir)
    staging_path = assets_path.parent / f"{assets_path.name}.staging-{uuid4().hex}"
    try:
        staging_path.mkdir(parents=True, exist_ok=True)
        for title, content in snapshot.downloaded.items():
            (staging_path / title).write_bytes(content)
        _publish_staged_directory(staging_path, assets_path)
    except OSError as exception:
        shutil.rmtree(staging_path, ignore_errors=True)
        raise AttachmentRetrievalError(type(exception).__name__) from None


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


def _failure_note(category: str) -> str:
    return f"<!-- adf:diagram source unavailable: attachment retrieval failed ({category}) -->"


def _replace_all_placeholders(markdown: str, note: str) -> str:
    markdown = _DRAWIO_PLACEHOLDER_RE.sub(note, markdown)
    markdown = _ATTACHMENT_PLACEHOLDER_RE.sub(note, markdown)
    return markdown


def restore_diagrams(markdown: str, snapshot: AttachmentSnapshot, assets_dir_name: str) -> str:
    """Substitute every `<!-- adf:diagram ... -->` / `<!-- adf:attachment ... -->` placeholder:
    a mermaid fence when a `{name}.source.mmd` sidecar exists, else a Markdown image or a plain
    link into `assets_dir_name`. Resolves entirely from `snapshot` — no REST call of its own.
    """
    if not has_diagram_placeholder(markdown):
        return markdown

    attachments = snapshot.attachments
    downloaded = snapshot.downloaded

    def _sidecar_text(sidecar_title: str) -> str | None:
        content = downloaded.get(sidecar_title)
        if content is None:
            return None
        return content.decode("utf-8") if isinstance(content, bytes) else content

    def _replace_drawio(match: re.Match) -> str:
        sidecar_title = _sidecar_title(match.group(1))
        text = _sidecar_text(sidecar_title)
        if text is None:
            return _missing_sidecar_note(sidecar_title)
        return _fence(text)

    def _replace_attachment(match: re.Match) -> str:
        media_id, alt, width, height = match.group(1), match.group(2), match.group(3), match.group(4)
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
            image_line = f"![{alt or filename}]({link})"
            if width and height:
                return f"{image_line}\n<!-- media-size: width={width} height={height} -->"
            return image_line
        return f"[{filename}]({link})"

    markdown = _DRAWIO_PLACEHOLDER_RE.sub(_replace_drawio, markdown)
    markdown = _ATTACHMENT_PLACEHOLDER_RE.sub(_replace_attachment, markdown)
    return markdown


def restore_diagrams_without_credentials(markdown: str) -> str:
    """Degraded mode: no token configured, so every placeholder gets a note instead of a fence."""
    return _replace_all_placeholders(markdown, NO_TOKEN_NOTE)


def restore_diagrams_skipped(markdown: str) -> str:
    """`--attachments skip`: retrieval was never attempted, so every placeholder says so."""
    return _replace_all_placeholders(markdown, SKIPPED_NOTE)


def restore_diagrams_failed(markdown: str, category: str) -> str:
    """`--attachments auto` after a failed retrieval: every placeholder names the safe category."""
    return _replace_all_placeholders(markdown, _failure_note(category))


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
    try:
        snapshot = fetch_attachment_snapshot(confluence, args.page_id)
        publish_attachment_cache(snapshot, args.assets_dir)
    except AttachmentRetrievalError as exception:
        sys.stdout.write(restore_diagrams_failed(markdown, str(exception)))
        return
    sys.stdout.write(restore_diagrams(markdown, snapshot, Path(args.assets_dir).name))


if __name__ == "__main__":
    main()
