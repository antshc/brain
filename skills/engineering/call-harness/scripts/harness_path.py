#!/usr/bin/env python3
"""Resolve the harness repository from this installed skill's location."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


def fail(message: str) -> "NoReturn":
    print(message, file=sys.stderr)
    raise SystemExit(1)


def harness_root() -> Path:
    skill_dir = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        ["git", "-C", str(skill_dir), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        fail("call-harness must be installed inside a Git repository")

    root = Path(result.stdout.strip()).resolve()
    if not root.is_dir():
        fail("resolved harness repository does not exist")
    return root


def resolve_target(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        fail("target path escapes the harness repository")

    if not candidate.exists():
        fail(f"harness target does not exist: {relative_path}")
    return candidate


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resolve the Git repository containing the installed call-harness skill."
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Optional existing path relative to the harness repository.",
    )
    args = parser.parse_args()

    root = harness_root()
    print(resolve_target(root, args.path) if args.path else root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
