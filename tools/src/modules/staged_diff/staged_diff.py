#!/usr/bin/env python3
"""Entry point for the to-codey/to-chorey/to-commit staged-diff-with-fallback step.

Stages all changes, then prints the cached diff, or the literal fallback
string when there are no uncommitted changes. Intended as a drop-in
replacement for the three skills' previously embedded inline shell snippet:
    git add -A 2>/dev/null; DIFF=$(git diff --cached 2>/dev/null); [ -n "$DIFF" ] && echo "$DIFF" || echo "No uncommitted changes"

Runs in the directory the calling agent was launched from (cwd) — takes no
path argument and performs no cwd-changing or path discovery of its own.

Usage:
    python staged_diff.py

Output (stdout):
    The cached diff, or the literal line `No uncommitted changes`.

Exit codes:
    0 - always (mirrors the bash snippet, which never fails on a git error)
"""

import subprocess
import sys
from typing import Callable

NO_CHANGES_MESSAGE = "No uncommitted changes"

GitRunner = Callable[[list[str]], str]


def run_git_command(args: list[str]) -> str:
    """Run `git <args>`, suppressing stderr, returning stdout (empty on failure)."""
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    return result.stdout


def get_staged_diff_with_fallback(run_git: GitRunner = run_git_command) -> str:
    """Stage all changes and return the cached diff, or the no-changes fallback message."""
    run_git(["add", "-A"])
    diff = run_git(["diff", "--cached"]).rstrip("\n")
    return diff if diff else NO_CHANGES_MESSAGE


def main() -> int:
    print(get_staged_diff_with_fallback())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
