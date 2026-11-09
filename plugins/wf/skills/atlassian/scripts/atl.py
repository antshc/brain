#!/usr/bin/env python3
"""ATL command-line entry point; runs from any working directory.

    python3 <atlassian-skill-dir>/scripts/atl.py <command> [options]

Commands: fetch-work, publish-work, fetch-page, publish-page, map-markdown. See `--help`.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from atl_cli.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
