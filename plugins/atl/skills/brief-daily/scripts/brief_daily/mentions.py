"""Query B classification: bucket each issue by whether its latest @mention was answered.

Mentions are matched on display name, not `accountId`: the MCP renders a mention as
`<custom data-type="mention" data-id="id-0">@Display Name</custom>`, where `data-id` is a
per-comment positional placeholder with no mapping back to an account. Reply authorship
still uses `author.accountId`, which is the real identifier.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from .payload import comments, comments_truncated, parse_timestamp, to_date


def mention_pattern(display_name: str) -> re.Pattern[str]:
    return re.compile(
        r'<custom data-type="mention"[^>]*>@' + re.escape(display_name) + r"</custom>"
    )


def _mentions(node: dict[str, Any], pattern: re.Pattern[str]) -> list[dict[str, Any]]:
    return [
        comment
        for comment in comments(node)
        if isinstance(comment.get("body"), str) and pattern.search(comment["body"])
    ]


def _earliest_reply(
    node: dict[str, Any], after: datetime, *, by_me: bool, account_id: str
) -> dict[str, Any] | None:
    replies = [
        comment
        for comment in comments(node)
        if parse_timestamp(comment["created"]) > after
        and (comment["author"]["accountId"] == account_id) is by_me
    ]
    if not replies:
        return None
    return min(replies, key=lambda comment: parse_timestamp(comment["created"]))


def classify(
    nodes: list[dict[str, Any]],
    *,
    account_id: str,
    display_name: str,
    cutoff: datetime,
) -> dict[str, Any]:
    pattern = mention_pattern(display_name)
    buckets: dict[str, list[dict[str, Any]]] = {
        "unanswered": [],
        "answeredByYou": [],
        "answeredByOther": [],
    }
    cutoff_excluded: list[str] = []
    partial_comments: list[str] = []

    for node in nodes:
        found = _mentions(node, pattern)
        if not found:
            continue
        in_window = [m for m in found if parse_timestamp(m["created"]) >= cutoff]
        if not in_window:
            cutoff_excluded.append(node["key"])
            continue
        if comments_truncated(node):
            partial_comments.append(node["key"])

        mention = max(in_window, key=lambda comment: parse_timestamp(comment["created"]))
        mentioned_at = parse_timestamp(mention["created"])
        mine = _earliest_reply(node, mentioned_at, by_me=True, account_id=account_id)
        theirs = _earliest_reply(node, mentioned_at, by_me=False, account_id=account_id)

        entry = {
            "key": node["key"],
            "url": node["webUrl"],
            "summary": node["fields"].get("summary"),
            "status": (node["fields"].get("status") or {}).get("name"),
            "mentionedBy": mention["author"]["displayName"],
            "mentionedOn": to_date(mention["created"]),
        }
        if mine:
            buckets["answeredByYou"].append(
                {**entry, "answeredOn": to_date(mine["created"]), "answeredBy": "you"}
            )
        elif theirs:
            buckets["answeredByOther"].append(
                {
                    **entry,
                    "answeredOn": to_date(theirs["created"]),
                    "answeredBy": theirs["author"]["displayName"],
                }
            )
        else:
            buckets["unanswered"].append(entry)

    for rows in buckets.values():
        rows.sort(key=lambda item: item["mentionedOn"], reverse=True)

    return {
        **buckets,
        "cutoffExcluded": cutoff_excluded,
        "partialComments": partial_comments,
    }
