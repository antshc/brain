"""Restore ```mermaid fences from a fetched page's diagram placeholders (I/O: Confluence REST
via `atlassian-python-api` — the one thing the Atlassian MCP does not expose for attachment
content).

`/map-markdown-adf`'s `adf-to-md` turns every Draw.io/media diagram node into a
`<!-- adf:diagram ... -->` placeholder comment (see its SKILL.md's mapping table). This module
resolves each placeholder to the `{name}.source.mmd` sidecar `/publish-page` attaches alongside
the rendered diagram (see its "Round-trip sidecar" section) and substitutes the verbatim
```mermaid fence back in.

Every failure mode degrades to a one-line note instead of raising — a missing sidecar (the page
predates the sidecar, or was never republished) or a missing token never fails the rest of the
fetch.
"""
from __future__ import annotations

import argparse
import re
import sys

from atlassian import Confluence

from env import get_confluence, load_credentials

_DRAWIO_PLACEHOLDER_RE = re.compile(r'<!-- adf:diagram drawio="([^"]*)" -->')
_MEDIA_PLACEHOLDER_RE = re.compile(r'<!-- adf:diagram media-id="([^"]*)" -->')
_ANY_PLACEHOLDER_RE = re.compile(r"<!-- adf:diagram ")

NO_TOKEN_NOTE = "<!-- adf:diagram source unavailable: set ATLASSIAN_API_TOKEN to restore it -->"


def has_diagram_placeholder(markdown: str) -> bool:
    return bool(_ANY_PLACEHOLDER_RE.search(markdown))


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


def _download_text(confluence: Confluence, attachment: dict) -> str:
    content = confluence.get(attachment["_links"]["download"], not_json_response=True)
    return content.decode("utf-8") if isinstance(content, bytes) else content


def _missing_sidecar_note(sidecar_title: str) -> str:
    return (
        f'<!-- adf:diagram source unavailable: "{sidecar_title}" not attached to this page; '
        "republish with /publish-page to enable round-trip -->"
    )


def _fence(source: str) -> str:
    return f"```mermaid\n{source.rstrip(chr(10))}\n```"


def restore_diagrams(confluence: Confluence, page_id: str, markdown: str) -> str:
    """Substitute every `<!-- adf:diagram ... -->` placeholder with its restored fence."""
    if not has_diagram_placeholder(markdown):
        return markdown

    attachments = list_attachments(confluence, page_id)

    def _resolve(sidecar_title: str) -> str:
        sidecar = _find_by_title(attachments, sidecar_title)
        if sidecar is None:
            return _missing_sidecar_note(sidecar_title)
        return _fence(_download_text(confluence, sidecar))

    def _replace_drawio(match: re.Match) -> str:
        return _resolve(_sidecar_title(match.group(1)))

    def _replace_media(match: re.Match) -> str:
        media_id = match.group(1)
        attachment = _find_by_file_id(attachments, media_id)
        if attachment is None:
            return f'<!-- adf:diagram source unavailable: attachment for media-id="{media_id}" not found -->'
        return _resolve(_sidecar_title(attachment["title"]))

    markdown = _DRAWIO_PLACEHOLDER_RE.sub(_replace_drawio, markdown)
    markdown = _MEDIA_PLACEHOLDER_RE.sub(_replace_media, markdown)
    return markdown


def restore_diagrams_without_credentials(markdown: str) -> str:
    """Degraded mode: no token configured, so every placeholder gets a note instead of a fence."""
    markdown = _DRAWIO_PLACEHOLDER_RE.sub(NO_TOKEN_NOTE, markdown)
    markdown = _MEDIA_PLACEHOLDER_RE.sub(NO_TOKEN_NOTE, markdown)
    return markdown


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Restore mermaid fences from a fetched page's diagram placeholders."
    )
    parser.add_argument("--page-id", required=True, help="Confluence pageId the Markdown was fetched from")
    parser.add_argument("--root", required=True, help="Harness Repo Path to bound the `.atlassian` search to")
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
    sys.stdout.write(restore_diagrams(confluence, args.page_id, markdown))


if __name__ == "__main__":
    main()
