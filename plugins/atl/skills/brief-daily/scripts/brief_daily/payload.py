"""Shared reading of `searchJiraIssuesUsingJql` spill files."""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Jira stamps offsets as `+0300`; `fromisoformat` needs `+03:00` before Python 3.11.
_OFFSET = re.compile(r"([+-]\d{2})(\d{2})$")


def load_pages(paths: list[str]) -> list[dict[str, Any]]:
    return [json.loads(Path(path).read_text(encoding="utf-8")) for path in paths]


def _issue_list(page: dict[str, Any]) -> list[dict[str, Any]]:
    """`searchJiraIssuesUsingJql` returns a flat `{"issues": [...]}` live; some fixtures
    still model the older nested `{"issues": {"nodes": [...]}}` envelope."""
    issues = page["issues"]
    return issues if isinstance(issues, list) else issues["nodes"]


def nodes(pages: list[dict[str, Any]], *, cloud_id: str) -> list[dict[str, Any]]:
    """The flat response carries no per-issue `webUrl`; synthesize it from `cloudId` + `key`."""
    result = []
    for page in pages:
        for issue in _issue_list(page):
            issue.setdefault("webUrl", f"{cloud_id}/browse/{issue['key']}")
            result.append(issue)
    return result


def truncated(pages: list[dict[str, Any]]) -> bool:
    if not pages:
        return False
    last = pages[-1]
    issues = last["issues"]
    if isinstance(issues, dict):
        return bool(issues["pageInfo"]["hasNextPage"])
    return not last.get("isLast", True)


def comments(node: dict[str, Any]) -> list[dict[str, Any]]:
    return node["fields"].get("comment", {}).get("comments", [])


def comments_truncated(node: dict[str, Any]) -> bool:
    envelope = node["fields"].get("comment")
    if not envelope:
        return False
    return len(envelope.get("comments", [])) < envelope.get("total", 0)


def parse_timestamp(stamp: str) -> datetime:
    normalised = _OFFSET.sub(r"\1:\2", stamp.replace("Z", "+00:00"))
    return datetime.fromisoformat(normalised)


def to_date(stamp: str) -> str:
    return parse_timestamp(stamp).date().isoformat()


def cutoff_from(days: int, *, now: datetime | None = None) -> datetime:
    return (now or datetime.now(timezone.utc)) - timedelta(days=days)
