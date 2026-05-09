#!/usr/bin/env python3
"""Entry point for the AFK review service.

Parses arguments, validates inputs, and delegates to the review use case.

Usage:
    python review_pull_requests.py <repo-dir> <github-user> <owner/repo> [max-executions] [--prompt <text>]

Arguments:
    repo-dir        Path to the local repository clone.
    github-user     GitHub username to filter open PRs by author.
    owner/repo      GitHub repository in owner/repo format.
    max-executions  Max processing attempts per PR before skipping (default: 5).
    --prompt        Prompt text passed to the AI agent (default: /review).

Exit codes:
    0 - success (may have 0 PRs to process)
    1 - usage / argument error
"""

import logging
import os
import re
import sys
from pathlib import Path

from afk.features.review_pull_requests.handler import review_pull_requests

DEFAULT_MAX_EXECUTIONS = 5

_USAGE = (
    "Usage:\n"
    "  review_pull_requests.py <repo-dir> <github-user> <owner/repo> [max-executions] [--prompt <text>]"
)


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


def _parse_prompt(args: list[str]) -> tuple[str, list[str]]:
    """Extract --prompt value from args, return (prompt, remaining_args)."""
    if "--prompt" in args:
        idx = args.index("--prompt")
        if idx + 1 >= len(args):
            print("Error: --prompt requires a value", file=sys.stderr)
            sys.exit(1)
        prompt = args[idx + 1]
        remaining = args[:idx] + args[idx + 2:]
        return prompt, remaining
    return "/review", args


def main() -> None:
    if len(sys.argv) < 2:
        print(_USAGE, file=sys.stderr)
        sys.exit(1)

    args = sys.argv[1:]
    prompt, args = _parse_prompt(args)
    logging.basicConfig(level=logging.DEBUG if "AFK_DEBUG" in os.environ else logging.WARNING)
    log_dir = Path(__file__).resolve().parent.parent.parent.parent / "logs"

    if len(args) < 3 or len(args) > 4:
        print(_USAGE, file=sys.stderr)
        sys.exit(1)

    _parse_repo_dir(args[0])
    github_user = args[1]
    github_repo = args[2]
    max_executions = _parse_max_executions(args[3]) if len(args) == 4 else DEFAULT_MAX_EXECUTIONS

    if not re.match(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$", github_repo):
        print(f"Error: Invalid repo format. Expected owner/repo, got: {github_repo}", file=sys.stderr)
        sys.exit(1)

    review_pull_requests(github_user, github_repo, log_dir, max_executions, prompt)
