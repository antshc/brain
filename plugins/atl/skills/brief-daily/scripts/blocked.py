#!/usr/bin/env python3
"""Print the blocked-items rows from a Query A spill file as JSON.

Usage:
    python3 blocked.py --content <path> [--content <path> ...]
"""
from __future__ import annotations

from brief_daily.cli import main_blocked

if __name__ == "__main__":
    main_blocked()
