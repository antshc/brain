#!/usr/bin/env python3
"""Entry point for the AFK review service.

Parses arguments, validates inputs, and delegates to the review use case.

Usage:
    python main.py review-prs <repo-dir> <github-user> <owner/repo> [max-executions]
    python main.py review-pr  <repo-dir> <pr-url>                   [max-executions]

Subcommands:
    review-prs  Process all open PRs for a given user and repository.
    review-pr   Process a single PR identified by its full GitHub URL.

Arguments (review-prs):
    repo-dir        Path to the local repository clone.
    github-user     GitHub username to filter open PRs by author.
    owner/repo      GitHub repository in owner/repo format.
    max-executions  Max processing attempts per PR before skipping (default: 5).

Arguments (review-pr):
    repo-dir        Path to the local repository clone.
    pr-url          Full GitHub PR URL, e.g. https://github.com/owner/repo/pull/123.
    max-executions  Max processing attempts before skipping (default: 5).

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

from features.review_pull_requests.handler import review_pull_requests
from features.review_pull_request.handler import review_pull_request

DEFAULT_MAX_EXECUTIONS = 5

_USAGE = (
    "Usage:\n"
    "  main.py review-prs <repo-dir> <github-user> <owner/repo> [max-executions]\n"
    "  main.py review-pr  <repo-dir> <pr-url>                   [max-executions]"
)

_PR_URL_RE = re.compile(r"^https://github\.com/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/pull/\d+$")


def _parse_repo_dir(value: str) -> Path:
    repo_dir = Path(value).resolve()
    if not repo_dir.is_dir():
        print(f"Error: repo-dir does not exist: {repo_dir}", file=sys.stderr)
        sys.exit(1)
    return repo_dir


def _parse_max_executions(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        print(f"Error: max-executions must be an integer, got: {value}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        print(_USAGE, file=sys.stderr)
        sys.exit(1)

    subcommand = sys.argv[1]
    logging.basicConfig(level=logging.DEBUG if "AFK_DEBUG" in os.environ else logging.WARNING)
    log_dir = Path(__file__).resolve().parent.parent / "logs"

    if subcommand == "review-prs":
        if len(sys.argv) < 5 or len(sys.argv) > 6:
            print(_USAGE, file=sys.stderr)
            sys.exit(1)

        repo_dir = _parse_repo_dir(sys.argv[2])
        github_user = sys.argv[3]
        github_repo = sys.argv[4]
        max_executions = _parse_max_executions(sys.argv[5]) if len(sys.argv) == 6 else DEFAULT_MAX_EXECUTIONS

        if not re.match(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$", github_repo):
            print(f"Error: Invalid repo format. Expected owner/repo, got: {github_repo}", file=sys.stderr)
            sys.exit(1)

        review_pull_requests(github_user, github_repo, log_dir, max_executions)

    elif subcommand == "review-pr":
        if len(sys.argv) < 4 or len(sys.argv) > 5:
            print(_USAGE, file=sys.stderr)
            sys.exit(1)

        repo_dir = _parse_repo_dir(sys.argv[2])
        pr_url = sys.argv[3]
        max_executions = _parse_max_executions(sys.argv[4]) if len(sys.argv) == 5 else DEFAULT_MAX_EXECUTIONS

        if not _PR_URL_RE.match(pr_url):
            print(
                f"Error: Invalid PR URL. Expected https://github.com/<owner>/<repo>/pull/<number>, got: {pr_url}",
                file=sys.stderr,
            )
            sys.exit(1)

        review_pull_request(pr_url, log_dir, max_executions)

    else:
        print(f"Error: Unknown subcommand '{subcommand}'\n{_USAGE}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
