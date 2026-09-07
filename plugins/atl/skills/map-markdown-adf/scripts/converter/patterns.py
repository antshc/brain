"""Shared regexes for Markdown block parsing."""
from __future__ import annotations

import re

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)", re.MULTILINE)
TOC_COMMENT_RE = re.compile(r"^\s*<!--\s*confluence:toc\s*-->\s*$", re.IGNORECASE)
WIDE_TABLE_MARKER_RE = re.compile(r"^\s*<!--\s*confluence:wide-table\s*-->\s*$", re.IGNORECASE)

# GitHub-style alert marker for the first line of a panel blockquote, e.g. "[!WARNING]".
PANEL_MARKER_RE = re.compile(r"^\[!(INFO|NOTE|WARNING|SUCCESS|ERROR)\]\s*$")
PANEL_TYPES = {"info", "note", "warning", "success", "error"}
