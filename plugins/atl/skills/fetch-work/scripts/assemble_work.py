"""Fetch a Jira issue over REST and assemble its header + Markdown body in one pass (I/O: Jira
REST via `atlassian-python-api`, shells out to `/map-markdown-adf`'s CLI for ADF->Markdown, then
reuses this skill's own `fetch_attachments` module for attachment caching and placeholder
resolution).

REST v3 returns the real ADF `description`, so every `map-markdown-adf` construct survives the
round trip. Credentials (`cloudId`/`email`/`apiToken`) are mandatory; `--site` overrides the
configured site for an issue URL on another site.
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
    fetch_issue,
    has_attachment_placeholder,
    has_attachment_reference,
    restore_attachments,
    save_attachments,
)

_MAP_MARKDOWN_ADF = _SCRIPT_DIR.parents[1] / "map-markdown-adf" / "scripts" / "map_markdown_adf.py"


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


def assemble(issue_key: str, fields: dict, jira, assets_dir: str) -> str:
    header = format_header(issue_key, fields)
    adf_body = fields.get("description")
    if not adf_body:
        return header

    markdown = convert_adf_to_markdown(adf_body)
    if has_attachment_reference(adf_body):
        downloaded = save_attachments(jira, issue_key, assets_dir)
        if has_attachment_placeholder(markdown):
            assets_dir_name = Path(assets_dir).name
            markdown = restore_attachments(jira, issue_key, markdown, downloaded, assets_dir_name)

    return header + markdown


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch a Jira issue over REST and assemble its header + Markdown body in one pass."
    )
    parser.add_argument("--issue-key", required=True, help="Jira issue key to fetch")
    parser.add_argument("--config", required=True, help="`.atlassian.json.user` path (`configPath` from `/preflight-atlassian`)")
    parser.add_argument("--md-path", required=True, help="Path to write the assembled Markdown to")
    parser.add_argument(
        "--assets-dir",
        help="Directory to cache this issue's attachments into (default: `<md-path>.tmp`)",
    )
    parser.add_argument("--site", help="Site URL overriding the configured `cloudId` (issue URL on another site)")
    args = parser.parse_args()

    credentials = load_credentials(args.config)
    if credentials is None:
        print(
            "error: .atlassian.json.user needs cloudId, email, and apiToken to fetch a work item",
            file=sys.stderr,
        )
        raise SystemExit(1)
    if args.site:
        credentials = {**credentials, "site": args.site}

    md_path = Path(args.md_path)
    assets_dir = args.assets_dir or str(md_path.parent / f"{md_path.name}.tmp")

    jira = get_jira(credentials)
    fields = fetch_issue(jira, args.issue_key)
    md_path.write_text(assemble(args.issue_key, fields, jira, assets_dir))


if __name__ == "__main__":
    main()
