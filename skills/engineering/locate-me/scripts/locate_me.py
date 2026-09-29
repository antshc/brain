#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

skill_dir = Path(__file__).resolve().parent
root = subprocess.run(
    ["git", "-C", str(skill_dir), "rev-parse", "--show-toplevel"],
    capture_output=True,
    text=True,
)

if root.returncode:
    print(root.stderr.strip(), file=sys.stderr)
    raise SystemExit(root.returncode)

target = Path(root.stdout.strip()) / "me.txt"
if not target.is_file():
    print(f"me.txt not found: {target}", file=sys.stderr)
    raise SystemExit(1)

print(target.resolve())
