"""Regexes and the marker helper shared by mermaid extraction and diagram naming."""
from __future__ import annotations

import re

from ..converter.syntax import syntax_lines

MEDIA_MARKER_RE = re.compile(r"^\x00MEDIA:(\d+)\x00$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)", re.MULTILINE)
SUMMARY_RE = re.compile(r"^\s*<summary>(.*)</summary>\s*$", re.MULTILINE)

# Matches the whole line so stripping it leaves source `mmdc` and Draw.io can still parse.
DIAGRAM_ID_RE = re.compile(
    r"^[ \t]*%%[ \t]*diagram-id:[ \t]*([A-Za-z0-9][A-Za-z0-9._-]*)[ \t]*\n?", re.MULTILINE
)

IGNORE_START_RE = re.compile(r"^\s*<!--\s*adf:ignore:start\s*-->\s*$", re.IGNORECASE | re.MULTILINE)
IGNORE_END_RE = re.compile(r"^\s*<!--\s*adf:ignore:end\s*-->\s*$", re.IGNORECASE | re.MULTILINE)


def media_marker(index: int) -> str:
    return f"\x00MEDIA:{index}\x00"


def strip_ignored_sections(md_text: str) -> str:
    """Drop every `adf:ignore:start`/`adf:ignore:end` span, tags included.

    Pairs are matched left to right and do not nest. An unterminated `start` marker is a
    hard error rather than a silent to-EOF strip or an accidental publish.
    """
    result = []
    ignoring = False
    raw_lines = md_text.splitlines(keepends=True)
    for (number, syntax), original in zip(syntax_lines(md_text), raw_lines):
        if IGNORE_START_RE.fullmatch(syntax):
            if ignoring:
                raise ValueError("nested adf:ignore:start")
            ignoring = True
        elif IGNORE_END_RE.fullmatch(syntax):
            if not ignoring:
                raise ValueError("stray adf:ignore:end")
            ignoring = False
        elif not ignoring:
            result.append(original)
    if ignoring:
        raise ValueError("unterminated adf:ignore:start (no matching adf:ignore:end)")
    return "".join(result)
