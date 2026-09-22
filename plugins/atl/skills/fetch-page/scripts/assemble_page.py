"""Assemble a fetched Confluence page's title + Markdown body in one pass (I/O: shells out to
`/map-markdown-adf`'s CLI for ADF->Markdown, then reuses this skill's own `fetch_diagrams` module
for attachment caching and placeholder resolution) — replaces the old fetch-then-inspect-then-
convert-then-restore turn chain with a single call.

Reads the raw `getConfluencePage` (`contentFormat: "adf"`) tool result from stdin; the page's
title and ADF body live at `content.nodes[0].title` / `content.nodes[0].body` (a stable shape
confirmed by the tool's own JSON schema). Converts unconditionally; only touches the Confluence
REST/attachment path when a pure, offline scan of the raw ADF body finds a node that references
an attached file (see `fetch_diagrams.has_attachment_reference`) — a page with none of those
never makes a REST call or creates an `.assets` folder, regardless of credentials or
`--attachments`.

`--attachments` controls what happens when a reference is present:
- `auto` (default): attempt retrieval when credentials exist; degrade to a note on any failure.
- `skip`: no credential lookup, no REST call at all; every placeholder becomes a "skipped" note.
- `required`: any missing credential or retrieval/publish failure raises instead of degrading,
  and `main()` never writes `--md-path` in that case.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from env import get_confluence, load_credentials  # noqa: E402
from fetch_diagrams import (  # noqa: E402
    AttachmentRetrievalError,
    fetch_attachment_snapshot,
    has_attachment_reference,
    has_diagram_placeholder,
    publish_attachment_cache,
    restore_diagrams,
    restore_diagrams_failed,
    restore_diagrams_skipped,
    restore_diagrams_without_credentials,
)

_MAP_MARKDOWN_ADF = _SCRIPT_DIR.parents[1] / "map-markdown-adf" / "scripts" / "map_markdown_adf.py"

_ATTACHMENT_MODES = ("auto", "skip", "required")


class ConversionError(Exception):
    """`/map-markdown-adf`'s CLI rejected the ADF body. The message is exactly its own sanitized
    stderr — never a raw `CalledProcessError` traceback.
    """


def extract_title_and_body(raw: dict) -> tuple[str, dict]:
    node = raw["content"]["nodes"][0]
    return node["title"], node["body"]


def convert_adf_to_markdown(body: dict) -> str:
    result = subprocess.run(
        [sys.executable, str(_MAP_MARKDOWN_ADF), "adf-to-md"],
        input=json.dumps(body),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ConversionError(result.stderr.strip() or "unknown conversion failure")
    return result.stdout


def _with_title(markdown: str, title: str) -> str:
    # a body whose own first heading already is the title needs no second `# <title>` line
    if markdown.startswith(f"# {title}\n"):
        return markdown
    return f"# {title}\n\n{markdown}"


def default_assets_dir(md_path: Path) -> Path:
    return md_path.with_suffix(".assets")


def assemble(raw: dict, page_id: str, root: str, assets_dir: str, attachments: str = "auto") -> str:
    title, body = extract_title_and_body(raw)
    markdown = convert_adf_to_markdown(body)

    if not has_attachment_reference(body):
        return _with_title(markdown, title)

    if attachments == "skip":
        if has_diagram_placeholder(markdown):
            markdown = restore_diagrams_skipped(markdown)
        return _with_title(markdown, title)

    credentials = load_credentials(root)
    if credentials is None:
        if attachments == "required":
            raise AttachmentRetrievalError("missing credentials")
        if has_diagram_placeholder(markdown):
            markdown = restore_diagrams_without_credentials(markdown)
        return _with_title(markdown, title)

    confluence = get_confluence(credentials)
    try:
        snapshot = fetch_attachment_snapshot(confluence, page_id)
        publish_attachment_cache(snapshot, assets_dir)
    except AttachmentRetrievalError as exception:
        if attachments == "required":
            raise
        if has_diagram_placeholder(markdown):
            markdown = restore_diagrams_failed(markdown, str(exception))
        return _with_title(markdown, title)

    if has_diagram_placeholder(markdown):
        assets_dir_name = Path(assets_dir).name
        markdown = restore_diagrams(markdown, snapshot, assets_dir_name)
        if attachments == "required" and has_diagram_placeholder(markdown):
            raise AttachmentRetrievalError("unresolved attachment reference")
    return _with_title(markdown, title)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assemble a fetched Confluence page's title + Markdown body in one pass."
    )
    parser.add_argument("--page-id", required=True, help="Confluence pageId the page was fetched from")
    parser.add_argument("--root", required=True, help="Harness Repo Path to bound the `.atlassian` search to")
    parser.add_argument("--md-path", required=True, help="Path to write the assembled Markdown to")
    parser.add_argument(
        "--assets-dir",
        help="Directory to cache this page's attachments into (default: `<md-path stem>.assets`)",
    )
    parser.add_argument(
        "--attachments",
        choices=_ATTACHMENT_MODES,
        default="auto",
        help=(
            "Attachment retrieval policy: auto (default) attempts retrieval and degrades safely "
            "on failure; skip performs no credential lookup or REST call; required fails without "
            "writing --md-path when credentials, retrieval, or cache publication are unavailable"
        ),
    )
    args = parser.parse_args()

    md_path = Path(args.md_path)
    assets_dir = args.assets_dir or str(default_assets_dir(md_path))

    raw = json.loads(sys.stdin.read())
    try:
        markdown = assemble(raw, args.page_id, args.root, assets_dir, args.attachments)
    except ConversionError as exception:
        print(f"ADF conversion failed: {exception}", file=sys.stderr)
        raise SystemExit(1)
    except AttachmentRetrievalError as exception:
        print(f"Attachment retrieval failed: {exception}", file=sys.stderr)
        raise SystemExit(1)

    md_path.write_text(markdown)


if __name__ == "__main__":
    main()
