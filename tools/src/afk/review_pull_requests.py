#!/usr/bin/env python3
"""Entry point for the AFK review service.

Parses arguments, validates inputs, and delegates to the review use case.
Run with --help for usage.

Exit codes:
    0 - success (may have 0 PRs to process)
    2 - usage / argument error (argparse default)
"""

import argparse
import logging
import os
import re
import sys
from pathlib import Path

from afk.features.review_pull_requests.handler import review_pull_requests

DEFAULT_MAX_EXECUTIONS = 5


def _repo_dir(value: str) -> Path:
    repo_dir = Path(value).resolve()
    if not repo_dir.is_dir():
        raise argparse.ArgumentTypeError(f"repo-dir does not exist: {repo_dir}")
    return repo_dir


def _github_repo(value: str) -> str:
    if not re.match(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$", value):
        raise argparse.ArgumentTypeError(f"Invalid repo format. Expected owner/repo, got: {value}")
    return value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="review_pull_requests.py",
        description="AFK automated PR review service.",
    )
    parser.add_argument("repo_dir", type=_repo_dir, metavar="repo-dir",
                        help="Path to the local repository clone.")
    parser.add_argument("github_user", metavar="github-user",
                        help="GitHub username to filter open PRs by author.")
    parser.add_argument("github_repo", type=_github_repo, metavar="owner/repo",
                        help="GitHub repository in owner/repo format.")
    parser.add_argument("max_executions", nargs="?", type=int, default=DEFAULT_MAX_EXECUTIONS,
                        metavar="max-executions",
                        help=f"Max processing attempts per PR before skipping (default: {DEFAULT_MAX_EXECUTIONS}).")
    parser.add_argument("--prompt", default="/review",
                        help="Prompt text passed to the AI agent (default: /review).")
    parser.add_argument("--log-dir", type=Path, default=Path(__file__).resolve().parent.parent.parent.parent / "logs",
                        metavar="log-dir",
                        help="Directory for execution logs (default: <repo-root>/logs).")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if "AFK_DEBUG" in os.environ else logging.WARNING)

    review_pull_requests(args.github_user, args.github_repo, args.log_dir, args.max_executions, args.prompt)
