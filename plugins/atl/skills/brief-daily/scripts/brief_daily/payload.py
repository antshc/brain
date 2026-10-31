"""Shared reading of `twg jira workitem query -o json --output-file` pages."""
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


def nodes(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """twg flattens Jira fields onto each issue and carries its browse `url`."""
    return [issue for page in pages for issue in page["data"]["issues"]]


def truncated(pages: list[dict[str, Any]]) -> bool:
    if not pages:
        return False
    return bool(pages[-1].get("pageInfo", {}).get("hasNextPage"))


def comments(node: dict[str, Any]) -> list[dict[str, Any]]:
    return (node.get("comment") or {}).get("comments", [])


def comments_truncated(node: dict[str, Any]) -> bool:
    envelope = node.get("comment")
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
