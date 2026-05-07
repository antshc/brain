#!/usr/bin/env python3
"""Entry point for the AFK review service.

Parses arguments, validates inputs, and delegates to the review use case.

Usage:
    python review_service.py <repo-dir> <github-user> <owner/repo> [max-executions]

Arguments:
    repo-dir        Path to the local repository clone.
    github-user     GitHub username to filter open PRs by author.
    owner/repo      GitHub repository in owner/repo format.
    max-executions  Max processing attempts per PR before skipping (default: 5).

Exit codes:
    0 - success (may have 0 PRs to process)
    1 - usage / argument error
"""

import logging
import os
import re
import sys
from pathlib import Path

# Add app/ to path so feature/domain/shared imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parent))

from features.review.handler import run_review

DEFAULT_MAX_EXECUTIONS = 5


def main() -> None:
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Usage: review_service.py <repo-dir> <github-user> <owner/repo> [max-executions]", file=sys.stderr)
        sys.exit(1)

    repo_dir = Path(sys.argv[1]).resolve()
    github_user = sys.argv[2]
    github_repo = sys.argv[3]
    max_executions = int(sys.argv[4]) if len(sys.argv) == 5 else DEFAULT_MAX_EXECUTIONS

    if not repo_dir.is_dir():
        print(f"Error: repo-dir does not exist: {repo_dir}", file=sys.stderr)
        sys.exit(1)

    if not re.match(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$", github_repo):
        print(f"Error: Invalid repo format. Expected owner/repo, got: {github_repo}", file=sys.stderr)
        sys.exit(1)

    logging.basicConfig(level=logging.DEBUG if "AFK_DEBUG" in os.environ else logging.WARNING)

    log_dir = Path(__file__).resolve().parent.parent / "logs"
    run_review(github_user, github_repo, log_dir, max_executions)


if __name__ == "__main__":
    main()
