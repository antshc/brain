#!/usr/bin/env python3
"""Fetch and classify PR review threads from GitHub.

Usage:
    python fetch_threads.py <pr_url>
    
As a library:
    from fetch_threads import fetch_and_classify_threads
    threads = fetch_and_classify_threads("https://github.com/owner/repo/pull/42")
"""

import logging
import re
import sys

from gh_client import fetch_review_threads
from pr_url import parse_pr_url

logger = logging.getLogger(__name__)

LABEL_PATTERNS = [
    ("fix!", re.compile(r"fix!:")),
    ("suggest!", re.compile(r"suggest!:")),
    ("suggest", re.compile(r"suggest:")),
    ("nit", re.compile(r"nit:")),
    ("good", re.compile(r"good:")),
    ("question", re.compile(r"question!:")),
]

ACTIONABLE_LABELS = {"fix!", "suggest!"}
EXCLUDED_KEYWORDS = {"fixed.", "question!:"}


def detect_label(body: str) -> str | None:
    """Return the first matching label in the body, or None."""
    for label, pattern in LABEL_PATTERNS:
        if pattern.search(body):
            return label
    return None


def classify_thread(thread: dict) -> dict | None:
    """Classify a single thread. Returns classified dict or None if excluded."""
    thread_id = thread["id"]

    # Scan comments in reverse: last significant signal wins.
    # An actionable label (fix!, suggest!) after question!/fixed. un-excludes;
    # question!/fixed. after an actionable label re-excludes.
    body = None
    for comment in reversed(thread["comments"]):
        text = comment["body"]
        if any(keyword in text.lower() for keyword in EXCLUDED_KEYWORDS):
            return None
        if detect_label(text):
            body = text
            break

    if body is None:
        body = thread["comments"][0]["body"] if thread["comments"] else ""

    label = detect_label(body)
    if not label:
        logger.warning("Unrecognized label for thread %s: %.60s", thread_id, body)
        return None

    start = thread.get("startLine") or thread.get("line")
    end = thread.get("line")

    return {
        "thread_id": thread_id,
        "prefix": label,
        "path": thread.get("path", ""),
        "lines": f"{start}-{end}",
        "body": body,
        "discussion": [
            {"author": c["author"]["login"], "body": c["body"]}
            for c in thread["comments"]
        ],
    }


def fetch_and_classify_threads(pr_url: str) -> list[dict]:
    """Fetch unresolved review threads and return actionable ones, sorted by priority."""
    owner, repo, number = parse_pr_url(pr_url)
    threads = fetch_review_threads(owner, repo, number)

    fix_threads = []
    suggest_threads = []

    for thread in threads:
        if thread.get("isResolved"):
            continue
        classified = classify_thread(thread)
        if not classified or classified["prefix"] not in ACTIONABLE_LABELS:
            continue
        if classified["prefix"] == "fix!":
            fix_threads.append(classified)
        else:
            suggest_threads.append(classified)

    return fix_threads + suggest_threads


if __name__ == "__main__":
    import json, os

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <PR_URL>", file=sys.stderr)
        sys.exit(1)

    logging.basicConfig(level=logging.DEBUG if "AFK_DEBUG" in os.environ else logging.WARNING)
    result = fetch_and_classify_threads(sys.argv[1])
    print(json.dumps(result, indent=2))
