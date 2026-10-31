#!/usr/bin/env python3
"""Create or update a Jira work item from an ADF description over REST v3, attach files, and
read the live description back for verification (I/O: Jira REST via `atlassian-python-api`).

The ADF comes from `/map-markdown-adf`'s `md-to-adf`; REST v3 accepts only ADF for
`description`, so every `map-markdown-adf` construct (`expand`, `panel`, `status`, ...) lands as
its real node. Credentials (`cloudId`/`email`/`apiToken`) are mandatory and read from
`.atlassian.json.user` — never passed as CLI args.

Usage:
    python3 publish_work.py create --config <configPath> --project <KEY> --issue-type <type> \
        --summary <text> --adf <description.json> [--parent <KEY>] [--fields-json <file>] \
        [--attach <path> ...]
    python3 publish_work.py update --config <configPath> --key <KEY> --adf <description.json> \
        [--summary <text>] [--fields-json <file>] [--attach <path> ...]
    python3 publish_work.py read-adf --config <configPath> --key <KEY> --out <live.json>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from env import get_jira, load_credentials, site_url  # noqa: E402
from requests.exceptions import HTTPError, RequestException  # noqa: E402


class PublishError(Exception):
    """A Jira call failed; the message is Jira's own error text or the exception class only."""


def _read_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_fields(
    *,
    adf: dict,
    summary: str | None = None,
    project: str | None = None,
    issue_type: str | None = None,
    parent: str | None = None,
    extra: dict | None = None,
) -> dict:
    """Caller-supplied fields only; `extra` never overrides the explicit ones."""
    fields: dict = dict(extra or {})
    if project:
        fields["project"] = {"key": project}
    if issue_type:
        fields["issuetype"] = {"name": issue_type}
    if summary:
        fields["summary"] = summary
    if parent:
        fields["parent"] = {"key": parent}
    fields["description"] = adf
    return fields


def _call(action):
    try:
        return action()
    except HTTPError as exception:
        raise PublishError(str(exception) or type(exception).__name__) from None
    except RequestException as exception:
        raise PublishError(type(exception).__name__) from None


def create_issue(jira, fields: dict) -> str:
    return _call(lambda: jira.post("rest/api/3/issue", data={"fields": fields}))["key"]


def update_issue(jira, key: str, fields: dict) -> None:
    _call(lambda: jira.put(f"rest/api/3/issue/{key}", data={"fields": fields}))


def attach_files(jira, key: str, paths: list[str]) -> tuple[list[str], list[dict]]:
    """Attach each file; a failure is recorded, never raised, so the issue key still reaches
    the caller."""
    attached: list[str] = []
    failed: list[dict] = []
    for path in paths:
        try:
            _call(lambda path=path: jira.add_attachment(key, path))
        except (PublishError, OSError) as exception:
            failed.append({"file": Path(path).name, "error": str(exception) or type(exception).__name__})
            continue
        attached.append(Path(path).name)
    return attached, failed


def read_description(jira, key: str) -> dict | None:
    return _call(lambda: jira.get(f"rest/api/3/issue/{key}", params={"fields": "description"}))["fields"]["description"]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Publish a Jira work item over REST v3 with an ADF description.")
    sub = parser.add_subparsers(dest="action", required=True)

    create = sub.add_parser("create", help="Create a work item")
    create.add_argument("--project", required=True, help="Jira project key")
    create.add_argument("--issue-type", required=True, help="Issue type name, e.g. Story")
    create.add_argument("--summary", required=True, help="One-line title")
    create.add_argument("--parent", help="Parent/epic key")

    update = sub.add_parser("update", help="Update an existing work item in place")
    update.add_argument("--key", required=True, help="Work item key to update")
    update.add_argument("--summary", help="New title; omit to keep the current one")

    for command in (create, update):
        command.add_argument("--adf", required=True, help="ADF description JSON file (from map-markdown-adf md-to-adf)")
        command.add_argument("--fields-json", help="JSON file of additional caller-supplied fields")
        command.add_argument("--attach", action="append", default=[], metavar="PATH", help="File to attach; repeatable")

    read = sub.add_parser("read-adf", help="Write the live description ADF to a file")
    read.add_argument("--key", required=True, help="Work item key to read")
    read.add_argument("--out", required=True, help="Path to write the live ADF to")

    for command in (create, update, read):
        command.add_argument("--config", required=True, help="`.atlassian.json.user` path (`configPath` from `/preflight-atlassian`)")
    return parser


def run(args: argparse.Namespace, jira, site: str) -> dict:
    if args.action == "read-adf":
        description = read_description(jira, args.key)
        Path(args.out).write_text(json.dumps(description, indent=2) + "\n", encoding="utf-8")
        return {"key": args.key, "adfPath": args.out}

    extra = _read_json(args.fields_json) if args.fields_json else None
    adf = _read_json(args.adf)
    if args.action == "create":
        fields = build_fields(
            adf=adf, summary=args.summary, project=args.project, issue_type=args.issue_type, parent=args.parent, extra=extra
        )
        key = create_issue(jira, fields)
    else:
        key = args.key
        update_issue(jira, key, build_fields(adf=adf, summary=args.summary, extra=extra))

    result: dict = {"key": key, "url": f"{site}/browse/{key}"}
    if args.attach:
        result["attached"], failed = attach_files(jira, key, args.attach)
        if failed:
            result["attachFailed"] = failed
    return result


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    credentials = load_credentials(args.config)
    if credentials is None:
        print("error: .atlassian.json.user needs cloudId, email, and apiToken to publish a work item", file=sys.stderr)
        raise SystemExit(1)
    try:
        result = run(args, get_jira(credentials), site_url(credentials))
    except PublishError as exception:
        print(f"error: Jira rejected the request: {exception}", file=sys.stderr)
        raise SystemExit(1)
    json.dump(result, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
