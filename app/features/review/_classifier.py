"""Label detection and thread classification logic."""

import logging
import re

from domain.review_thread import ReviewThread, ThreadLabel

logger = logging.getLogger(__name__)

LABEL_PATTERNS: list[tuple[ThreadLabel, re.Pattern]] = [
    (ThreadLabel.FIX, re.compile(r"fix!:")),
    (ThreadLabel.SUGGEST_BANG, re.compile(r"suggest!:")),
    (ThreadLabel.SUGGEST, re.compile(r"suggest:")),
    (ThreadLabel.NIT, re.compile(r"nit:")),
    (ThreadLabel.GOOD, re.compile(r"good:")),
    (ThreadLabel.QUESTION, re.compile(r"question!:")),
]

EXCLUDED_KEYWORDS = {"fixed.", "question!:"}


def detect_label(body: str) -> ThreadLabel | None:
    """Return the first matching ThreadLabel in the body, or None."""
    for label, pattern in LABEL_PATTERNS:
        if pattern.search(body):
            return label
    return None


def classify_thread(thread: dict) -> ReviewThread | None:
    """Classify a single thread. Returns a ReviewThread or None if excluded."""
    thread_id = thread["id"]

    # Scan comments in reverse: last significant signal wins.
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

    return ReviewThread(
        thread_id=thread_id,
        label=label,
        path=thread.get("path", ""),
        lines=f"{start}-{end}",
        body=body,
        discussion=[
            {"author": c["author"]["login"], "body": c["body"]}
            for c in thread["comments"]
        ],
    )
