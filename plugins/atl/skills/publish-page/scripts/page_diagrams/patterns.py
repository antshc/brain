"""Regexes and the marker helper shared by mermaid extraction and diagram naming."""
from __future__ import annotations

import re

MEDIA_MARKER_RE = re.compile(r"^\x00MEDIA:(\d+)\x00$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)", re.MULTILINE)
SUMMARY_RE = re.compile(r"^\s*<summary>(.*)</summary>\s*$", re.MULTILINE)


def media_marker(index: int) -> str:
    return f"\x00MEDIA:{index}\x00"
