#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

skill_dir = Path(__file__).resolve().parent
target = skill_dir / "me.txt"
if not target.is_file():
    print(f"me.txt not found: {target}", file=sys.stderr)
    raise SystemExit(1)

print(target.resolve())
