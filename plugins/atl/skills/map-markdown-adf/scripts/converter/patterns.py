"""Shared regexes for Markdown block parsing."""
from __future__ import annotations

import re

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)", re.MULTILINE)
TOC_COMMENT_RE = re.compile(r"^\s*<!--\s*adf:toc\s*-->\s*$", re.IGNORECASE)
WIDE_TABLE_MARKER_RE = re.compile(r"^\s*<!--\s*adf:wide-table\s*-->\s*$", re.IGNORECASE)

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
