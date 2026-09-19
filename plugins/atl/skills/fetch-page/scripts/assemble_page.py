"""Assemble a fetched Confluence page's title + Markdown body in one pass (I/O: shells out to
`/map-markdown-adf`'s CLI for ADF->Markdown, then reuses this skill's own `fetch_diagrams` module
for mermaid restoration) — replaces the old fetch-then-inspect-then-convert-then-restore turn
chain with a single call.

Reads the raw `getConfluencePage` (`contentFormat: "adf"`) tool result from stdin; the page's
title and ADF body live at `content.nodes[0].title` / `content.nodes[0].body` (a stable shape
confirmed by the tool's own JSON schema). Converts unconditionally; restores diagrams only when
the converted Markdown still carries an `<!-- adf:diagram` placeholder, so a diagram-free page
never touches the Confluence REST/attachment path.
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
    has_diagram_placeholder,
    restore_diagrams,
    restore_diagrams_without_credentials,
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


def assemble(raw: dict, page_id: str, root: str) -> str:
    title, body = extract_title_and_body(raw)
    markdown = convert_adf_to_markdown(body)

    if has_diagram_placeholder(markdown):
        credentials = load_credentials(root)
        if credentials is None:
            markdown = restore_diagrams_without_credentials(markdown)
        else:
            markdown = restore_diagrams(get_confluence(credentials), page_id, markdown)

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
    args = parser.parse_args()

    raw = json.loads(sys.stdin.read())
    sys.stdout.write(assemble(raw, args.page_id, args.root))


if __name__ == "__main__":
    main()
