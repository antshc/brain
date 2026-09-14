"""Detect Markdown constructs that only ADF can express (pure).

Jira accepts `contentFormat: "markdown"` for plain CommonMark, but the markers below have no
Markdown equivalent and arrive as literal text — a caller that finds any of them must convert to
ADF instead. Patterns are shared with the converter so detection and parsing cannot drift.
"""
from __future__ import annotations

import re

from .patterns import (
    DETAILS_OPEN_RE,
    PANEL_MARKER_RE,
    STATUS_RE,
    TOC_COMMENT_RE,
    WIDE_TABLE_MARKER_RE,
)

_FENCE_RE = re.compile(r"^\s*```")
_QUOTE_PREFIX_RE = re.compile(r"^\s*>\s?")


def detect_adf_only(markdown: str) -> list[dict]:
    """Return one `{"kind", "line"}` entry per ADF-only construct, in source order."""
    found: list[dict] = []
    in_fence = False

    for number, line in enumerate(markdown.splitlines(), start=1):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            # A marker shown inside a code sample is literal text, not a node.
            continue

        if DETAILS_OPEN_RE.match(line):
            found.append({"kind": "expand", "line": number})
        elif TOC_COMMENT_RE.match(line):
            found.append({"kind": "toc", "line": number})
        elif WIDE_TABLE_MARKER_RE.match(line):
            found.append({"kind": "wideTable", "line": number})
        elif line.lstrip().startswith(">") and PANEL_MARKER_RE.match(_QUOTE_PREFIX_RE.sub("", line, count=1)):
            found.append({"kind": "panel", "line": number})

        if STATUS_RE.search(line):
            found.append({"kind": "status", "line": number})

    return found
