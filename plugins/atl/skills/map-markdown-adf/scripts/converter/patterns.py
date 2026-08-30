"""Shared regexes for Markdown block parsing."""
from __future__ import annotations

import re

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)", re.MULTILINE)
