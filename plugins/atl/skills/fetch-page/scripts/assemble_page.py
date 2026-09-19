"""Assemble a fetched Confluence page's title + Markdown body in one pass (I/O: shells out to
`/map-markdown-adf`'s CLI for ADF->Markdown, then reuses this skill's own `fetch_diagrams` module
for attachment caching and placeholder resolution) — replaces the old fetch-then-inspect-then-
convert-then-restore turn chain with a single call.

Reads the raw `getConfluencePage` (`contentFormat: "adf"`) tool result from stdin; the page's
title and ADF body live at `content.nodes[0].title` / `content.nodes[0].body` (a stable shape
confirmed by the tool's own JSON schema). Converts unconditionally; only touches the Confluence
REST/attachment path when a pure, offline scan of the raw ADF body finds a node that references
an attached file (see `fetch_diagrams.has_attachment_reference`) — a page with none of those
never makes a REST call or creates a `.tmp` assets folder, regardless of credentials.
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
    has_attachment_reference,
    has_diagram_placeholder,
    restore_diagrams,
    restore_diagrams_without_credentials,
    save_attachments,
)

_MAP_MARKDOWN_ADF = _SCRIPT_DIR.parents[1] / "map-markdown-adf" / "scripts" / "map_markdown_adf.py"


def extract_title_and_body(raw: dict) -> tuple[str, dict]:
    node = raw["content"]["nodes"][0]
    return node["title"], node["body"]


def convert_adf_to_markdown(body: dict) -> str:
    result = subprocess.run(
        [sys.executable, str(_MAP_MARKDOWN_ADF), "adf-to-md"],
        input=json.dumps(body),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def assemble(raw: dict, page_id: str, root: str, assets_dir: str) -> str:
    title, body = extract_title_and_body(raw)
    markdown = convert_adf_to_markdown(body)

    if has_attachment_reference(body):
        credentials = load_credentials(root)
        if credentials is None:
            if has_diagram_placeholder(markdown):
                markdown = restore_diagrams_without_credentials(markdown)
        else:
            confluence = get_confluence(credentials)
            downloaded = save_attachments(confluence, page_id, assets_dir)
            if has_diagram_placeholder(markdown):
                assets_dir_name = Path(assets_dir).name
                markdown = restore_diagrams(confluence, page_id, markdown, downloaded, assets_dir_name)

    # a body whose own first heading already is the title needs no second `# <title>` line
    if markdown.startswith(f"# {title}\n"):
        return markdown
    return f"# {title}\n\n{markdown}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assemble a fetched Confluence page's title + Markdown body in one pass."
    )
    parser.add_argument("--page-id", required=True, help="Confluence pageId the page was fetched from")
    parser.add_argument("--root", required=True, help="Harness Repo Path to bound the `.atlassian` search to")
    parser.add_argument("--md-path", required=True, help="Path to write the assembled Markdown to")
    parser.add_argument(
        "--assets-dir",
        help="Directory to cache this page's attachments into (default: `<md-path>.tmp`)",
    )
    args = parser.parse_args()

    md_path = Path(args.md_path)
    assets_dir = args.assets_dir or str(md_path.parent / f"{md_path.name}.tmp")

    raw = json.loads(sys.stdin.read())
    markdown = assemble(raw, args.page_id, args.root, assets_dir)
    md_path.write_text(markdown)


if __name__ == "__main__":
    main()
