"""Assemble a fetched Jira issue's header + Markdown body in one pass (I/O: shells out to
`/map-markdown-adf`'s CLI for ADF->Markdown, then reuses this skill's own `fetch_attachments`
module for attachment caching and placeholder resolution) — replaces the old fetch-then-convert
turn chain with a single call.

Reads the raw `getJiraIssue` tool result from stdin; the issue's fields live at
`issues.nodes[0].fields` (a stable shape confirmed live against ZIC-5881). That MCP result never
carries real ADF for `description` (verified live — see `fetch_attachments.fetch_description_adf`'s
docstring), only an already-flattened Markdown-ish string with empty `alt` text on every embedded
image, so it is used as-is only in the no-token branch; the token branch instead fetches the real
ADF directly over REST and converts that.
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

from env import get_jira, load_credentials  # noqa: E402
from fetch_attachments import (  # noqa: E402
    fetch_description_adf,
    has_attachment_placeholder,
    has_attachment_reference,
    replace_blob_image_refs_without_credentials,
    restore_attachments,
    save_attachments,
)

_MAP_MARKDOWN_ADF = _SCRIPT_DIR.parents[1] / "map-markdown-adf" / "scripts" / "map_markdown_adf.py"


def extract_fields(raw: dict) -> dict:
    return raw["issues"]["nodes"][0]["fields"]


def convert_adf_to_markdown(body: dict) -> str:
    result = subprocess.run(
        [sys.executable, str(_MAP_MARKDOWN_ADF), "adf-to-md"],
        input=json.dumps(body),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def format_header(issue_key: str, fields: dict) -> str:
    summary = fields.get("summary", "")
    status = (fields.get("status") or {}).get("name", "")
    issuetype = (fields.get("issuetype") or {}).get("name", "")
    assignee = (fields.get("assignee") or {}).get("displayName") or "Unassigned"
    return (
        f"# {issue_key} — {summary}\n"
        f"**Status:** {status} · **Type:** {issuetype} · **Assignee:** {assignee}\n\n"
    )


def assemble(raw: dict, issue_key: str, root: str, assets_dir: str) -> str:
    fields = extract_fields(raw)
    header = format_header(issue_key, fields)

    credentials = load_credentials(root)
    if credentials is None:
        body = replace_blob_image_refs_without_credentials(fields.get("description") or "")
        return header + body

    jira = get_jira(credentials)
    adf_body = fetch_description_adf(jira, issue_key)
    markdown = convert_adf_to_markdown(adf_body)

    if has_attachment_reference(adf_body):
        downloaded = save_attachments(jira, issue_key, assets_dir)
        if has_attachment_placeholder(markdown):
            assets_dir_name = Path(assets_dir).name
            markdown = restore_attachments(jira, issue_key, markdown, downloaded, assets_dir_name)

    return header + markdown


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assemble a fetched Jira issue's header + Markdown body in one pass."
    )
    parser.add_argument("--issue-key", required=True, help="Jira issue key the issue was fetched from")
    parser.add_argument("--root", required=True, help="Harness Repo Path to bound the `.atlassian` search to")
    parser.add_argument("--md-path", required=True, help="Path to write the assembled Markdown to")
    parser.add_argument(
        "--assets-dir",
        help="Directory to cache this issue's attachments into (default: `<md-path>.tmp`)",
    )
    args = parser.parse_args()

    md_path = Path(args.md_path)
    assets_dir = args.assets_dir or str(md_path.parent / f"{md_path.name}.tmp")

    raw = json.loads(sys.stdin.read())
    markdown = assemble(raw, args.issue_key, args.root, assets_dir)
    md_path.write_text(markdown)


if __name__ == "__main__":
    main()
