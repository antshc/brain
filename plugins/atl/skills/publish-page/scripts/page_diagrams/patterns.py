"""Regexes and the marker helper shared by mermaid extraction and diagram naming."""
from __future__ import annotations

import re

MEDIA_MARKER_RE = re.compile(r"^\x00MEDIA:(\d+)\x00$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)", re.MULTILINE)
SUMMARY_RE = re.compile(r"^\s*<summary>(.*)</summary>\s*$", re.MULTILINE)

IGNORE_START_RE = re.compile(r"^\s*<!--\s*confluence:ignore:start\s*-->\s*$", re.IGNORECASE | re.MULTILINE)
IGNORE_END_RE = re.compile(r"^\s*<!--\s*confluence:ignore:end\s*-->\s*$", re.IGNORECASE | re.MULTILINE)


def media_marker(index: int) -> str:
    return f"\x00MEDIA:{index}\x00"


def strip_ignored_sections(md_text: str) -> str:
    """Drop every `confluence:ignore:start`/`confluence:ignore:end` span, tags included.

    Pairs are matched left to right and do not nest. An unterminated `start` marker is a
    hard error rather than a silent to-EOF strip or an accidental publish.
    """
    result_parts: list[str] = []
    pos = 0
    while True:
        start_m = IGNORE_START_RE.search(md_text, pos)
        if not start_m:
            result_parts.append(md_text[pos:])
            break
        end_m = IGNORE_END_RE.search(md_text, start_m.end())
        if not end_m:
            raise ValueError("unterminated confluence:ignore:start (no matching confluence:ignore:end)")
        result_parts.append(md_text[pos : start_m.start()])
        pos = end_m.end()
    return "".join(result_parts)
