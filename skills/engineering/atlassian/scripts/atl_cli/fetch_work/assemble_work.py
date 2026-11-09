"""`fetch-work`: fetch a Jira issue over REST and assemble its header + Markdown body in one pass
(I/O: Jira REST via `atlassian-python-api`; ADF->Markdown in-process through `map_markdown`;
`fetch_attachments` caches attachments and resolves placeholders).

REST v3 returns the real ADF `description`, so every `map-markdown-adf` construct survives the
round trip. Credentials (`cloudId`/`email`/`apiToken`) are mandatory; `--site` overrides the
configured site for an issue URL on another site.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..config import load_credentials, require_supported_library
from ..jira_client import get_jira
from ..map_markdown import ConversionError, adf_to_md
from .fetch_attachments import (
    attachments_section,
    fetch_issue,
    has_attachment_placeholder,
    referenced_filenames,
    restore_attachments,
    save_attachments,
)


def convert_adf_to_markdown(body: dict) -> str:
    return adf_to_md(body)


def format_header(issue_key: str, fields: dict) -> str:
    summary = fields.get("summary", "")
    status = (fields.get("status") or {}).get("name", "")
    issuetype = (fields.get("issuetype") or {}).get("name", "")
    assignee = (fields.get("assignee") or {}).get("displayName") or "Unassigned"
    return (
        f"# {issue_key} — {summary}\n"
        f"**Status:** {status} · **Type:** {issuetype} · **Assignee:** {assignee}\n\n"
    )


def assemble(issue_key: str, fields: dict, jira, assets_dir: str, attachments_mode: str = "embedded") -> str:
    header = format_header(issue_key, fields)
    adf_body = fields.get("description")
    markdown = convert_adf_to_markdown(adf_body) if adf_body else ""
    referenced = referenced_filenames(markdown)

    attachments = fields.get("attachment") or []
    wanted = None if attachments_mode == "all" else referenced
    downloaded = save_attachments(jira, attachments, assets_dir, wanted)
    if has_attachment_placeholder(markdown):
        markdown = restore_attachments(jira, issue_key, markdown, downloaded, Path(assets_dir).name)

    section = attachments_section(attachments, downloaded, referenced, assets_dir)
    if not section:
        return header + markdown
    if not markdown:
        return header + section
    body = markdown.rstrip("\n")
    return f"{header}{body}\n\n{section}"


def main(argv: list[str] | None = None, *, prog: str | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Fetch a Jira issue over REST and assemble its header + Markdown body in one pass."
    )
    parser.add_argument("--issue-key", required=True, help="Jira issue key to fetch")
    parser.add_argument("--config", required=True, help="`.atlassian.json.user` path (`configPath` from `/preflight-atlassian`)")
    parser.add_argument("--md-path", required=True, help="Path to write the assembled Markdown to")
    parser.add_argument(
        "--assets-dir",
        help="Directory to cache this issue's attachments into (default: `<md-path>.tmp`)",
    )
    parser.add_argument(
        "--attachments",
        choices=("embedded", "all"),
        default="embedded",
        help="`embedded` (default): download only attachments the description embeds, list the rest; "
        "`all`: download every attachment",
    )
    parser.add_argument("--site", help="Site URL overriding the configured `cloudId` (issue URL on another site)")
    args = parser.parse_args(argv)

    require_supported_library()
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
    try:
        markdown = assemble(args.issue_key, fields, jira, assets_dir, args.attachments)
    except ConversionError as exception:
        print(f"error: ADF conversion failed: {exception}", file=sys.stderr)
        raise SystemExit(1)
    md_path.write_text(markdown)
