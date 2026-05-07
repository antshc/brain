"""Review use case: lists open PRs and drives the Copilot agent to address review threads."""

from pathlib import Path

from features.review._fetch_threads import fetch_and_classify_threads
from features.review._run_agent import run_agent
from infrastructure.gh_client import list_prs
from shared.execution_log import ExecutionLog
from shared.log import log_json


def run_review(github_user: str, github_repo: str, log_dir: Path, max_executions: int) -> None:
    """List open PRs for *github_user* and run the Copilot agent on actionable review threads.

    Args:
        github_user:    GitHub username; only PRs authored by this user are processed.
        github_repo:    Repository in owner/repo format.
        log_dir:        Directory where execution logs are written.
        max_executions: Maximum processing attempts per PR before skipping.
    """
    exec_log = ExecutionLog(log_dir, github_repo)

    log_json("info", "Service run started", user=github_user, repo=github_repo)

    pull_requests = list_prs(github_user, github_repo)

    if not pull_requests:
        log_json("info", "No open PRs found for user", user=github_user, repo=github_repo)
        return

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
