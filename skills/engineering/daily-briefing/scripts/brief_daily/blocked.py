"""Query A rows: blocked work items assigned to the current user."""
from __future__ import annotations

from typing import Any

from .payload import to_date


def _named(field: Any) -> str | None:
    return field["name"] if isinstance(field, dict) else None


def row(node: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": node["key"],
        "url": node["url"],
        "summary": node.get("summary"),
        "type": _named(node.get("issuetype")),
        "status": _named(node.get("status")),
        "priority": _named(node.get("priority")),
        "updated": to_date(node["updated"]) if node.get("updated") else None,
    }


def rows(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        (row(node) for node in nodes),
        key=lambda item: (item["updated"] or ""),
        reverse=True,
    )
