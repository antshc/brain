"""Query B classification: bucket each issue by whether its latest @mention was answered.

twg returns comment bodies as ADF, where a mention is a `mention` node whose `attrs.id` is the
mentioned `accountId`; mentions and reply authorship both match on `accountId`.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .payload import comments, comments_truncated, parse_timestamp, to_date


def mentions_account(adf: Any, account_id: str) -> bool:
    if isinstance(adf, dict):
        if adf.get("type") == "mention" and (adf.get("attrs") or {}).get("id") == account_id:
            return True
        return any(mentions_account(value, account_id) for value in adf.values())
    if isinstance(adf, list):
        return any(mentions_account(item, account_id) for item in adf)
    return False


def _mentions(node: dict[str, Any], account_id: str) -> list[dict[str, Any]]:
    return [comment for comment in comments(node) if mentions_account(comment.get("body"), account_id)]


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
    cutoff: datetime,
) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = {
        "unanswered": [],
        "answeredByYou": [],
        "answeredByOther": [],
    }
    cutoff_excluded: list[str] = []
    partial_comments: list[str] = []

    for node in nodes:
        found = _mentions(node, account_id)
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
            "url": node["url"],
            "summary": node.get("summary"),
            "status": (node.get("status") or {}).get("name"),
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
