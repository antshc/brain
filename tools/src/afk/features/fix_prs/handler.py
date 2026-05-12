"""Review use case: lists open PRs and drives the Copilot agent to address review threads."""

from pathlib import Path

from modules.github.domain.services.thread_filter import ThreadFilter
from afk.infrastructure.ai_agent import AIAgent
from modules.github.infrastructure.vcs_client import VCSClient
import logging

from afk.shared.execution_log import ExecutionLog

_log = logging.getLogger(__name__)


def fix_prs(
    github_user: str,
    github_repo: str,
    log_dir: Path,
    max_executions: int,
    prompt: str = "/ralph:fix",
    *,
    agent_name: str = "copiloty",
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
        prompt:         Prompt text passed to the AI agent (default: "/ralph:fix").
        vcs:            VCSClient instance (defaults to VCSClient()).
        agent:          AIAgent instance (defaults to AIAgent()).
        exec_log:       ExecutionLog instance (defaults to ExecutionLog(log_dir, github_repo)).
    """
    exec_log = exec_log or ExecutionLog(log_dir, github_repo)
    thread_filter = ThreadFilter()
    vcs = vcs or VCSClient()

    _log.info("Service run started user=%s repo=%s", github_user, github_repo)

    pull_requests = vcs.list_prs(github_user, github_repo)

    if not pull_requests:
        _log.info("No open PRs found for user user=%s repo=%s", github_user, github_repo)
        return

    _log.info("Found open PRs count=%d user=%s", len(pull_requests), github_user)

    for pr in pull_requests:
        _log.info("Processing PR pr_url=%s", pr.url)

        exec_count = exec_log.get_count(pr.url)

        fetched_threads = vcs.fetch_review_threads(pr.owner, pr.repo, pr.number)
        actionable_threads = thread_filter.get_actionable_threads(fetched_threads)
        thread_ids = [t.thread_id for t in actionable_threads]

        if len(actionable_threads) == 0:
            _log.info("No actionable threads, skipping pr_url=%s", pr.url)
            if exec_count > 0:
                exec_log.reset(pr.url)
                _log.info("Reset execution count (all threads resolved) pr_url=%s", pr.url)
            continue

        if exec_count >= max_executions:
            _log.warning(
                "PR exceeded max executions, skipping pr_url=%s count=%d max=%d unresolved_threads=%d",
                pr.url, exec_count, max_executions, len(actionable_threads),
            )
            continue

        _log.info(
            "Running copilot agent pr_url=%s threads=%d attempt=%d",
            pr.url, len(actionable_threads), exec_count + 1,
        )

        (agent or AIAgent(alias=agent_name, prompt=prompt)).run()

        exec_log.update(pr.url, thread_ids)
        _log.info("Completed PR processing pr_url=%s attempt=%d", pr.url, exec_count + 1)

    _log.info("Service run completed")
