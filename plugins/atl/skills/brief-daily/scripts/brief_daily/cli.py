"""CLI orchestration for both reports. Offline only — reads spill files, no network."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import blocked, mentions
from .payload import cutoff_from, load_pages, nodes, truncated


def _content_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--content",
        required=True,
        action="append",
        metavar="PATH",
        help="A search spill `content.json`; repeat once per pagination page",
    )


def _load(paths: list[str]) -> tuple[list[dict], bool]:
    missing = [path for path in paths if not Path(path).is_file()]
    if missing:
        print(f"error: no such content file: {', '.join(missing)}", file=sys.stderr)
        raise SystemExit(1)
    pages = load_pages(paths)
    return nodes(pages), truncated(pages)


def main_blocked(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Rows for the blocked-items section.")
    _content_argument(parser)
    args = parser.parse_args(argv)
    issues, capped = _load(args.content)
    print(json.dumps({"rows": blocked.rows(issues), "truncated": capped}))


def main_mentions(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Bucket @mentions by whether they were answered.")
    _content_argument(parser)
    parser.add_argument("--account-id", required=True, help="Preflight's `accountId`")
    parser.add_argument("--display-name", required=True, help="Preflight's `displayName`")
    parser.add_argument("--cutoff-days", type=int, default=30, help="Period length in days")
    args = parser.parse_args(argv)
    issues, capped = _load(args.content)
    report = mentions.classify(
        issues,
        account_id=args.account_id,
        display_name=args.display_name,
        cutoff=cutoff_from(args.cutoff_days),
    )
    print(json.dumps({**report, "truncated": capped}))
