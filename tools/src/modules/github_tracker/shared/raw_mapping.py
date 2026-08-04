"""Mapping helpers shared by `github_tracker` feature handlers.

Normalizes raw `gh` CLI JSON output (label objects, comment objects) into the
plain shapes `manage-backlog`'s actions document, and extracts an issue number
from the URL `gh issue create` prints on success.
"""

import re

_ISSUE_URL_NUMBER_RE = re.compile(r"/(\d+)/?\s*$")


def parse_issue_number(issue_url: str) -> int:
    """Extract the trailing issue number from a `gh issue create`/`gh issue view` URL."""
    match = _ISSUE_URL_NUMBER_RE.search(issue_url.strip())
    if not match:
        raise ValueError(f"Could not parse an issue number from: {issue_url!r}")
    return int(match.group(1))


def normalize_labels(raw_labels: list) -> list[str]:
    """Flatten `gh`'s label objects (`{"name": ...}`) or plain strings to a list of names."""
    return [label["name"] if isinstance(label, dict) else label for label in raw_labels]


def normalize_comments(raw_comments: list) -> list[str]:
    """Flatten `gh`'s comment objects to their `body` text."""
    return [comment["body"] if isinstance(comment, dict) else comment for comment in raw_comments]


def ticket_from_raw(raw: dict) -> dict:
    """Map a raw `gh issue view`/`gh issue list` JSON object to the ticket shape
    `Read ticket` and `List tickets` document: number, title, body, labels, comments.
    """
    return {
        "number": raw["number"],
        "title": raw.get("title", ""),
        "body": raw.get("body", ""),
        "labels": normalize_labels(raw.get("labels", [])),
        "comments": normalize_comments(raw.get("comments", [])),
    }
