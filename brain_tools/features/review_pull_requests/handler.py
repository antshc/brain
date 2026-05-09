"""Review use case: lists open PRs and drives the Copilot agent to address review threads."""

from pathlib import Path

from brain_tools.domain.services.thread_filter import ThreadFilter
from brain_tools.infrastructure.ai_agent import AIAgent
from brain_tools.infrastructure.vcs_client import VCSClient
from brain_tools.shared.execution_log import ExecutionLog
from brain_tools.shared.log import log_json


def review_pull_requests(
    github_user: str,
    github_repo: str,
    log_dir: Path,
    max_executions: int,
    prompt: str = "/review",
    *,
    vcs: VCSClient | None = None,
    agent: AIAgent | None = None,
    exec_log: ExecutionLog | None = None,
) -> None:
    """List open PRs for *github_user* and run the Copilot agent on actionable review threads.

    Args:
        github_user:    GitHub username; only PRs authored by this user are processed.
        github_repo:    Repository in owner/repo format.
        log_dir:        Directory where execution logs are written.
        max_executions: Maximum processing attempts per PR before skipping.
        prompt:         Prompt text passed to the AI agent (default: "/review").
        vcs:            VCSClient instance (defaults to VCSClient()).
        agent:          AIAgent instance (defaults to AIAgent()).
        exec_log:       ExecutionLog instance (defaults to ExecutionLog(log_dir, github_repo)).
    """
    exec_log = exec_log or ExecutionLog(log_dir, github_repo)
    thread_filter = ThreadFilter()
    vcs = vcs or VCSClient()

    log_json("info", "Service run started", user=github_user, repo=github_repo)

    pull_requests = vcs.list_prs(github_user, github_repo)

    if not pull_requests:
        log_json("info", "No open PRs found for user", user=github_user, repo=github_repo)
        return

    log_json("info", "Found open PRs", count=str(len(pull_requests)), user=github_user)

    for pr in pull_requests:
        log_json("info", "Processing PR", pr_url=pr.url)

        exec_count = exec_log.get_count(pr.url)

        fetched_threads = vcs.fetch_review_threads(pr.owner, pr.repo, pr.number)
        actionable_threads = thread_filter.get_actionable_threads(fetched_threads)
        thread_ids = [t.thread_id for t in actionable_threads]

        if len(actionable_threads) == 0:
            log_json("info", "No actionable threads, skipping", pr_url=pr.url)
            if exec_count > 0:
                exec_log.reset(pr.url)
                log_json("info", "Reset execution count (all threads resolved)", pr_url=pr.url)
            continue

        if exec_count >= max_executions:
            log_json(
                "warn", "PR exceeded max executions, skipping",
                pr_url=pr.url, count=str(exec_count), max=str(max_executions),
                unresolved_threads=str(len(actionable_threads)),
            )
            continue

        log_json(
            "info", "Running copilot agent",
            pr_url=pr.url, threads=str(len(actionable_threads)), attempt=str(exec_count + 1),
        )

        vcs.checkout_pr(pr.url)

        (agent or AIAgent()).review(actionable_threads, prompt)

        exec_log.update(pr.url, thread_ids)
        log_json("info", "Completed PR processing", pr_url=pr.url, attempt=str(exec_count + 1))

    log_json("info", "Service run completed")
