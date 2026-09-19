#!/usr/bin/env python3
"""Bucket @mentions from a Query B spill file and print the buckets as JSON.

Usage:
    python3 mentions.py --content <path> [--content <path> ...] \
        --account-id <id> --display-name <name> [--cutoff-days 30]
"""
from __future__ import annotations

from brief_daily.cli import main_mentions

if __name__ == "__main__":
    main_mentions()
