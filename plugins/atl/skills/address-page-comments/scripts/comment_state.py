"""Classify a Confluence page's open comment threads for address-page-comments."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_ANNOTATION_ID = re.compile(r'data-annotation-id="([^"]+)"')


@dataclass(frozen=True)
class CommentPages:
    comments: list[dict[str, Any]]
    truncated: bool


def load_comment_pages(paths: list[Path]) -> CommentPages:
    comments: list[dict[str, Any]] = []
    next_cursor = None
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8")).get("data") or {}
        comments.extend(data.get("comments") or [])
        next_cursor = data.get("nextCursor")
    return CommentPages(comments=comments, truncated=bool(next_cursor))


def annotation_ids(html: str) -> set[str]:
    return set(_ANNOTATION_ID.findall(html))


def _entry(comment: dict[str, Any], account_id: str) -> dict[str, Any]:
    return {
        "id": comment.get("id"),
        "author": "me" if comment.get("authorAccountId") == account_id else "other",
        "authorAccountId": comment.get("authorAccountId"),
        "createdAt": comment.get("createdAt") or "",
        "body": ((comment.get("body") or {}).get("value") or "").strip(),
    }


def _anchor(comment: dict[str, Any], markers: set[str]) -> str:
    if comment.get("commentType") != "inline":
        return "page"
    return "anchored" if comment.get("inlineMarkerRef") in markers else "orphaned"


def _page_answer_exists(thread_id: str, after: str, own_footers: list[dict[str, Any]]) -> bool:
    link = f"focusedCommentId={thread_id}"
    return any(link in footer["body"] and footer["createdAt"] > after for footer in own_footers)


def classify(comments: list[dict[str, Any]], html: str, account_id: str, site: str) -> list[dict[str, Any]]:
    markers = annotation_ids(html)
    own_footers = [
        _entry(c, account_id) for c in comments
        if c.get("authorAccountId") == account_id and c.get("commentType") == "footer"
    ]
    threads = []
    for comment in comments:
        if comment.get("authorAccountId") == account_id:
            continue
        entries = [_entry(comment, account_id)]
        entries += sorted((_entry(r, account_id) for r in comment.get("replies") or []), key=lambda e: e["createdAt"])
        anchor = _anchor(comment, markers)
        last_other = max(e["createdAt"] for e in entries if e["author"] == "other")
        answered = entries[-1]["author"] == "me"
        if anchor == "orphaned" and not answered:
            answered = _page_answer_exists(comment["id"], last_other, own_footers)
        threads.append({
            "id": comment.get("id"),
            "type": comment.get("commentType"),
            "anchor": anchor,
            "replyTarget": "page" if anchor == "orphaned" else "thread",
            "state": "answered" if answered else "pending",
            "markerRef": comment.get("inlineMarkerRef"),
            "selection": comment.get("inlineOriginalSelection"),
            "url": f"{site.rstrip('/')}/wiki{comment.get('webUrl') or ''}",
            "comments": entries,
        })
    return threads


def build_report(pages: CommentPages, html: str, account_id: str, site: str) -> dict[str, Any]:
    if pages.truncated:
        return {"action": "stop", "reason": "Comment list truncated; fetch every nextCursor page first.", "threads": []}
    threads = classify(pages.comments, html, account_id, site)
    pending = [t for t in threads if t["state"] == "pending"]
    counts = {
        "open": len(threads),
        "pending": len(pending),
        "answered": len(threads) - len(pending),
        "orphaned": sum(t["anchor"] == "orphaned" for t in pending),
    }
    return {"action": "proceed" if pending else "skip", "counts": counts, "threads": pending}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comments", nargs="+", type=Path, required=True, help="twg comments list JSON pages, in cursor order")
    parser.add_argument("--html", type=Path, required=True, help="page body HTML from twg content get --format html")
    parser.add_argument("--account-id", required=True)
    parser.add_argument("--site", required=True, help="https://<host>")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)
    if not args.account_id:
        print("accountId is empty; resolve identity with preflight-atlassian first.", file=sys.stderr)
        return 2
    report = build_report(load_comment_pages(args.comments), args.html.read_text(encoding="utf-8"), args.account_id, args.site)
    print(json.dumps(report, indent=2 if args.pretty else None, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
