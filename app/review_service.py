#!/usr/bin/env python3
"""Orchestrator for the AFK review service.

Finds open PRs, fetches actionable threads, checks execution limits,
checks out each PR, and runs the copilot agent to address review comments.

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

from features.fetch_threads.handler import fetch_and_classify_threads
from features.list_prs.handler import list_prs
from features.run_agent.handler import run_agent
from features.track_execution.handler import ExecutionLog
from shared.log import log_json

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
    exec_log = ExecutionLog(log_dir, github_repo)

    log_json("info", "Service run started", user=github_user, repo=github_repo)

    pull_requests = list_prs(github_user, github_repo)

    if not pull_requests:
        log_json("info", "No open PRs found for user", user=github_user, repo=github_repo)
        sys.exit(0)

    log_json("info", "Found open PRs", count=str(len(pull_requests)), user=github_user)

    for pr in pull_requests:
        log_json("info", "Processing PR", pr_url=pr.url)

        exec_count = exec_log.get_count(pr.url)

        threads = fetch_and_classify_threads(pr.url)
        thread_ids = [t.thread_id for t in threads]

        if len(threads) == 0:
            log_json("info", "No actionable threads, skipping", pr_url=pr.url)
            if exec_count > 0:
                exec_log.reset(pr.url)
                log_json("info", "Reset execution count (all threads resolved)", pr_url=pr.url)
            continue

        if exec_count >= max_executions:
            log_json(
                "warn", "PR exceeded max executions, skipping",
                pr_url=pr.url, count=str(exec_count), max=str(max_executions),
                unresolved_threads=str(len(threads)),
            )
            continue

        log_json(
            "info", "Running copilot agent",
            pr_url=pr.url, threads=str(len(threads)), attempt=str(exec_count + 1),
        )

        run_agent(pr, threads)

        exec_log.update(pr.url, thread_ids)
        log_json("info", "Completed PR processing", pr_url=pr.url, attempt=str(exec_count + 1))

    log_json("info", "Service run completed")


if __name__ == "__main__":
    main()
