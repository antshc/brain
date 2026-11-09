"""Shared regexes for Markdown block parsing."""
from __future__ import annotations

import re

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)", re.MULTILINE)
TOC_COMMENT_RE = re.compile(r"^\s*<!--\s*adf:toc\s*-->\s*$", re.IGNORECASE)
WIDE_TABLE_MARKER_RE = re.compile(r"^\s*<!--\s*adf:wide-table\s*-->\s*$", re.IGNORECASE)
# General table attributes, e.g. `<!-- adf:table layout="wide" width="960" -->`; a table with only
# `layout: wide` keeps the shorter `adf:wide-table` marker above.
TABLE_MARKER_RE = re.compile(r"^\s*<!--\s*adf:table((?:\s+[a-z-]+=\"[^\"]*\")+)\s*-->\s*$", re.IGNORECASE)
# Block width mark on the next expand or code block, e.g. `<!-- adf:breakout mode="wide" width="760" -->`.
BREAKOUT_MARKER_RE = re.compile(r"^\s*<!--\s*adf:breakout((?:\s+[a-z-]+=\"[^\"]*\")+)\s*-->\s*$", re.IGNORECASE)
_MARKER_ATTR_RE = re.compile(r'([a-z-]+)="([^"]*)"', re.IGNORECASE)


def marker_number(value: str) -> int | float | str:
    try:
        number = float(value)
    except ValueError:
        return value
    return int(number) if number.is_integer() else number


def table_marker_attrs(line: str) -> dict | None:
    """Table `attrs` (`layout`, `width`) a table marker line sets, or None for any other line."""
    if WIDE_TABLE_MARKER_RE.match(line):
        return {"layout": "wide"}
    match = TABLE_MARKER_RE.match(line)
    if not match:
        return None
    attrs = dict(_MARKER_ATTR_RE.findall(match.group(1)))
    result: dict = {"layout": attrs.get("layout", "default")}
    if "width" in attrs:
        result["width"] = marker_number(attrs["width"])
    return result


def breakout_marker_mark(line: str) -> dict | None:
    """The `breakout` mark a breakout marker line sets, or None for any other line."""
    match = BREAKOUT_MARKER_RE.match(line)
    if not match:
        return None
    attrs = {key: marker_number(value) if key == "width" else value for key, value in _MARKER_ATTR_RE.findall(match.group(1))}
    return {"type": "breakout", "attrs": attrs}

# GitHub-style alert marker for the first line of a panel blockquote, e.g. "[!WARNING]".
PANEL_MARKER_RE = re.compile(r"^\[!(INFO|NOTE|WARNING|SUCCESS|ERROR)\]\s*$")
PANEL_TYPES = {"info", "note", "warning", "success", "error"}

DETAILS_OPEN_RE = re.compile(r"^\s*<details>\s*$")
DETAILS_CLOSE_RE = re.compile(r"^\s*</details>\s*$")
SUMMARY_RE = re.compile(r"^\s*<summary>(.*)</summary>\s*$")

# Inline status lozenge, e.g. "[STATUS:Done|green]". `inline.py` splices this source into its
# combined alternation so parsing and ADF-only detection can never drift apart.
STATUS_PATTERN = r"\[STATUS:(?P<status_text>[^|\]]+?)(?:\|(?P<status_color>[a-zA-Z]+))?\]"
STATUS_RE = re.compile(STATUS_PATTERN)

# Emoji status lozenge, e.g. "🟢[Done]": renders as a coloured dot in any Markdown viewer.
# `adf-to-md` writes this form; `md-to-adf` reads it and the legacy `[STATUS:...]` form above.
STATUS_EMOJI = {"neutral": "⚪", "purple": "🟣", "blue": "🔵", "red": "🔴", "yellow": "🟡", "green": "🟢"}
EMOJI_STATUS_COLORS = {emoji: color for color, emoji in STATUS_EMOJI.items()}
EMOJI_STATUS_PATTERN = (
    r"(?P<status_emoji>" + "|".join(STATUS_EMOJI.values()) + r")\uFE0F?"
    r"\[(?P<emoji_status_text>[^\]\n]+)\](?!\()"
)
EMOJI_STATUS_RE = re.compile(EMOJI_STATUS_PATTERN)

# Inline comment anchor, e.g. `<!-- adf:comment id="a0b9..." -->text<!-- /adf:comment -->`, mapped to
# the ADF `annotation` mark (`annotationType: inlineComment`). Pairs may nest; ids are opaque.
COMMENT_OPEN_RE = re.compile(r'<!--\s*adf:comment\s+id="(?P<comment_id>[A-Za-z0-9-]+)"\s*-->')
COMMENT_CLOSE_RE = re.compile(r"<!--\s*/adf:comment\s*-->")
COMMENT_TAG_RE = re.compile(f"{COMMENT_OPEN_RE.pattern}|{COMMENT_CLOSE_RE.pattern}")


def comment_open_tag(comment_id: str) -> str:
    return f'<!-- adf:comment id="{comment_id}" -->'


COMMENT_CLOSE_TAG = "<!-- /adf:comment -->"
