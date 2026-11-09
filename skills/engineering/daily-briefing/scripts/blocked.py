#!/usr/bin/env python3
"""Print the blocked-items rows from Query A twg pages as JSON.

Usage:
    python3 <daily-briefing-dir>/scripts/blocked.py --content <path> [--content <path> ...]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from brief_daily.cli import main_blocked  # noqa: E402

if __name__ == "__main__":
    main_blocked()
