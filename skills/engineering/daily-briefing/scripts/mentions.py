#!/usr/bin/env python3
"""Bucket @mentions from Query B twg pages and print the buckets as JSON.

Usage:
    python3 <daily-briefing-dir>/scripts/mentions.py --content <path> [--content <path> ...] \
        --account-id <id> [--cutoff-days 30]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from brief_daily.cli import main_mentions  # noqa: E402

if __name__ == "__main__":
    main_mentions()
