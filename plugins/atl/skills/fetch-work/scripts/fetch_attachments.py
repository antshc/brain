"""Cache a fetched Jira issue's attachments to disk and resolve its embedded-image placeholders
(I/O: Jira REST via `atlassian-python-api` — the one thing the Atlassian MCP does not expose for
either real ADF descriptions or attachment content).

`/map-markdown-adf`'s `adf-to-md` turns every `media`/`mediaSingle`/`mediaGroup` node into a
neutral `<!-- adf:attachment media-id="<id>" alt="<alt>" -->` placeholder (see its SKILL.md's
mapping table). Verified live against ZIC-5881: a Jira `media` node's `attrs.alt` always holds
the attachment's exact original filename — unlike Confluence, there is no media-id<->attachment-
id mapping to make, so every placeholder here resolves by matching its `alt` against
`fields.attachment[].filename` directly. Jira issues never carry a Draw.io macro or a
`/publish-page`-style mermaid sidecar, so unlike `/fetch-page`'s equivalent module, there is no
diagram branch at all here — every reference resolves to either a Markdown image or a plain link.

Every failure mode degrades to a one-line note instead of raising — a missing attachment (the
description references a file no longer attached) or a missing token never fails the rest of the
fetch.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import quote

from atlassian import Jira

from env import get_jira, load_credentials

_ATTACHMENT_PLACEHOLDER_RE = re.compile(
    r'<!-- adf:attachment media-id="([^"]*)" alt="([^"]*)"(?: width="(\d+)" height="(\d+)")? -->'
)
_BLOB_IMAGE_RE = re.compile(r"!\[\]\(blob:[^)]*\)")

NO_TOKEN_NOTE = (
    "<!-- adf:attachment source unavailable: set ATLASSIAN_API_TOKEN to resolve embedded images -->"
)

_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp")


def _looks_like_image(name: str) -> bool:
    return name.lower().endswith(_IMAGE_EXTENSIONS)


def has_attachment_placeholder(markdown: str) -> bool:
    return bool(_ATTACHMENT_PLACEHOLDER_RE.search(markdown))


def find_attachment_reference_nodes(node: object) -> list[dict]:
    """Recursively scan a raw ADF (sub)tree for a `media` node that references an attached file:
    a generic-file node, or an image node (its `alt` names an image file). Pure/offline, no REST
    — used only to decide whether it's worth touching Jira attachments at all.
    """
    found: list[dict] = []
    if isinstance(node, dict):
        node_type = node.get("type")
        attrs = node.get("attrs") or {}
        if node_type == "media":
            if attrs.get("type") == "file" or _looks_like_image(attrs.get("alt", "")):
                found.append(node)
        for value in node.values():
            found.extend(find_attachment_reference_nodes(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(find_attachment_reference_nodes(item))
    return found


def has_attachment_reference(body: dict) -> bool:
    return bool(find_attachment_reference_nodes(body))


def fetch_description_adf(jira: Jira, issue_key: str) -> dict:
    """Direct REST v3 call for the issue's real ADF description — the Atlassian MCP's
    `getJiraIssue` never returns real ADF (verified live against ZIC-5881), only an already-
    flattened Markdown-ish string with empty `alt` text on every embedded image.
    """
    resp = jira.get(f"rest/api/3/issue/{issue_key}", params={"fields": "description"})
    return resp["fields"]["description"]


def list_attachments(jira: Jira, issue_key: str) -> list[dict]:
    resp = jira.get(f"rest/api/3/issue/{issue_key}", params={"fields": "attachment"})
    return resp["fields"]["attachment"]


def _find_by_filename(attachments: list[dict], filename: str) -> dict | None:
    return next((a for a in attachments if a.get("filename") == filename), None)


def download_attachment_bytes(jira: Jira, attachment: dict) -> bytes:
    """Like `_download_text` but always bytes, so binary attachments (`.png` etc.) aren't
    corrupted by a text decode. Built from `attachment["id"]` rather than following
    `attachment["content"]` verbatim — that field is an absolute URL, and `atlassian-python-api`'s
    `.get()` always prepends the configured site to whatever path it's given, so passing the
    absolute URL through doubles the host and 404s.
    """
    content = jira.get(f"rest/api/3/attachment/content/{attachment['id']}", not_json_response=True)
    return content if isinstance(content, bytes) else content.encode("utf-8")


def save_attachments(jira: Jira, issue_key: str, assets_dir: str) -> dict[str, bytes]:
    """Download every attachment on the issue once and cache it under `assets_dir` (created only
    when the issue actually has attachments), returning `{filename: bytes}` so callers can
    resolve placeholders from memory instead of a second network round-trip.
    """
    attachments = list_attachments(jira, issue_key)
    if not attachments:
        return {}
    Path(assets_dir).mkdir(parents=True, exist_ok=True)
    downloaded: dict[str, bytes] = {}
    for attachment in attachments:
        content = download_attachment_bytes(jira, attachment)
        downloaded[attachment["filename"]] = content
        (Path(assets_dir) / attachment["filename"]).write_bytes(content)
    return downloaded


def _relative_link(assets_dir_name: str, filename: str) -> str:
    """Percent-encoded path relative to the Markdown file's own directory, e.g.
    `work.md.tmp/Screenshot%202026-02-10%20113535.png`."""
    return f"{assets_dir_name}/{quote(filename)}"


def restore_attachments(
    jira: Jira,
    issue_key: str,
    markdown: str,
    downloaded: dict[str, bytes],
    assets_dir_name: str,
) -> str:
    """Substitute every `<!-- adf:attachment ... -->` placeholder with a Markdown image or plain
    link into `assets_dir_name`, matching the placeholder's `alt` against a downloaded
    attachment's `filename` — never the `media-id`, which classic REST never exposes (only the
    media-services UUID `/map-markdown-adf` embeds; matching that against
    `fields.attachment[].filename` finds nothing). Reuses `downloaded` (from `save_attachments`)
    when possible; only falls back to a fresh `list_attachments` call when a filename isn't in it
    (e.g. a caller that didn't run `save_attachments` first).
    """
    if not has_attachment_placeholder(markdown):
        return markdown

    attachments: list[dict] | None = None

    def _resolve(alt: str) -> bytes | None:
        nonlocal attachments
        if alt in downloaded:
            return downloaded[alt]
        if attachments is None:
            attachments = list_attachments(jira, issue_key)
        attachment = _find_by_filename(attachments, alt)
        if attachment is None:
            return None
        return download_attachment_bytes(jira, attachment)

    def _replace(match: re.Match) -> str:
        alt, width, height = match.group(2), match.group(3), match.group(4)
        if not alt:
            return "<!-- adf:attachment source unavailable: placeholder carries no filename -->"
        if _resolve(alt) is None:
            return f'<!-- adf:attachment source unavailable: no attachment named "{alt}" on this issue -->'
        link = _relative_link(assets_dir_name, alt)
        if _looks_like_image(alt):
            image_line = f"![{alt}]({link})"
            if width and height:
                return f"{image_line}\n<!-- media-size: width={width} height={height} -->"
            return image_line
        return f"[{alt}]({link})"

    return _ATTACHMENT_PLACEHOLDER_RE.sub(_replace, markdown)


def restore_attachments_without_credentials(markdown: str) -> str:
    """Degraded mode: no token configured, so every placeholder gets a note instead of a file."""
    return _ATTACHMENT_PLACEHOLDER_RE.sub(NO_TOKEN_NOTE, markdown)


def replace_blob_image_refs_without_credentials(markdown: str) -> str:
    """The no-token, no-real-ADF branch: the MCP's already Markdown-ish `fields.description`
    string carries each embedded image as `![](blob:https://media...&id=<uuid>&...)` rather than
    an `/map-markdown-adf` placeholder — swap that pattern directly for the same note instead.
    """
    return _BLOB_IMAGE_RE.sub(NO_TOKEN_NOTE, markdown)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Restore Markdown image/link references from a fetched issue's attachment placeholders."
    )
    parser.add_argument("--issue-key", required=True, help="Jira issue key the Markdown was fetched from")
    parser.add_argument("--root", required=True, help="Harness Repo Path to bound the `.atlassian` search to")
    parser.add_argument("--assets-dir", required=True, help="Directory to cache this issue's attachments into")
    args = parser.parse_args()

    markdown = sys.stdin.read()
    if not has_attachment_placeholder(markdown):
        sys.stdout.write(markdown)
        return

    credentials = load_credentials(args.root)
    if credentials is None:
        sys.stdout.write(restore_attachments_without_credentials(markdown))
        return

    jira = get_jira(credentials)
    downloaded = save_attachments(jira, args.issue_key, args.assets_dir)
    sys.stdout.write(
        restore_attachments(jira, args.issue_key, markdown, downloaded, Path(args.assets_dir).name)
    )


if __name__ == "__main__":
    main()
