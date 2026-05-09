"""Review use case: drives the Copilot agent to address review threads for a single PR URL."""

from pathlib import Path

from modules.github.domain.pull_request import PullRequest
from modules.github.domain.services.thread_filter import ThreadFilter
from afk.infrastructure.ai_agent import AIAgent
from modules.github.infrastructure.vcs_client import VCSClient
from afk.shared.execution_log import ExecutionLog
from afk.shared.log import log_json
from modules.github.shared.pr_url import parse_pr_url


def review_pull_request(
    pr_url: str,
    log_dir: Path,
    max_executions: int,
    prompt: str = "/review",
    *,
    agent_name: str = "copilot",
    vcs: VCSClient | None = None,
    agent: AIAgent | None = None,
    exec_log: ExecutionLog | None = None,
) -> None:
    """Run the Copilot agent on actionable review threads for a single PR URL.

    Args:
        pr_url:         Full GitHub PR URL (e.g. https://github.com/owner/repo/pull/123).
        log_dir:        Directory where execution logs are written.
        max_executions: Maximum processing attempts before skipping.
        prompt:         Prompt text passed to the AI agent (default: "/review").
        vcs:            VCSClient instance (defaults to VCSClient()).
        agent:          AIAgent instance (defaults to AIAgent()).
        exec_log:       ExecutionLog instance (defaults to ExecutionLog(log_dir, github_repo)).
    """
    owner, repo_name, number = parse_pr_url(pr_url)
    github_repo = f"{owner}/{repo_name}"
    pr = PullRequest(owner=owner, repo=repo_name, number=number, url=pr_url)

    exec_log = exec_log or ExecutionLog(log_dir, github_repo)
    thread_filter = ThreadFilter()
    vcs = vcs or VCSClient()

    log_json("info", "Service run started", pr_url=pr_url)
    log_json("info", "Processing PR", pr_url=pr.url)

    exec_count = exec_log.get_count(pr.url)

    fetched_threads = vcs.fetch_review_threads(pr.owner, pr.repo, pr.number)
    actionable_pr_threads = thread_filter.get_actionable_threads(fetched_threads)
    thread_ids = [t.thread_id for t in actionable_pr_threads]

    if len(actionable_pr_threads) == 0:
        log_json("info", "No actionable threads, skipping", pr_url=pr.url)
        if exec_count > 0:
            exec_log.reset(pr.url)
            log_json("info", "Reset execution count (all threads resolved)", pr_url=pr.url)
        log_json("info", "Service run completed")
        return

    if exec_count >= max_executions:
        log_json(
            "warn", "PR exceeded max executions, skipping",
            pr_url=pr.url, count=str(exec_count), max=str(max_executions),
            unresolved_threads=str(len(actionable_pr_threads)),
        )
        log_json("info", "Service run completed")
        return

    log_json(
        "info", "Running copilot agent",
        pr_url=pr.url, threads=str(len(actionable_pr_threads)), attempt=str(exec_count + 1),
    )

    vcs.checkout_pr(pr.url)

    (agent or AIAgent(alias=agent_name, prompt=prompt)).run()

    exec_log.update(pr.url, thread_ids)
    log_json("info", "Completed PR processing", pr_url=pr.url, attempt=str(exec_count + 1))
