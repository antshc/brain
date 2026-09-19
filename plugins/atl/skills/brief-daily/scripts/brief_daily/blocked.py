"""Query A rows: blocked work items assigned to the current user."""
from __future__ import annotations

from typing import Any

from .payload import to_date


def _named(field: Any) -> str | None:
    return field["name"] if isinstance(field, dict) else None


def row(node: dict[str, Any]) -> dict[str, Any]:
    fields = node["fields"]
    return {
        "key": node["key"],
        "url": node["webUrl"],
        "summary": fields.get("summary"),
        "type": _named(fields.get("issuetype")),
        "status": _named(fields.get("status")),
        "priority": _named(fields.get("priority")),
        "updated": to_date(fields["updated"]) if fields.get("updated") else None,
    }


def rows(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        (row(node) for node in nodes),
        key=lambda item: (item["updated"] or ""),
        reverse=True,
    )
