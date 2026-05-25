"""Dev use case: processes actionable milestones and drives the Copilot agent."""

from pathlib import Path

from modules.github.domain.services.issue_filter import IssueFilter
from afk.infrastructure.ai_agent import AIAgent
from modules.github.infrastructure.vcs_client import VCSClient
import logging

from afk.shared.execution_log import ExecutionLog

_log = logging.getLogger(__name__)


def dev(
    github_repo: str,
    log_dir: Path,
    max_executions: int,
    prompt: str = "/ralph:dev",
    *,
    agent_name: str = "copiloty",
    vcs: VCSClient | None = None,
    agent: AIAgent | None = None,
    exec_log: ExecutionLog | None = None,
) -> None:
    """List open milestones for *github_repo* and run the Copilot agent on actionable work.

    Args:
        github_repo:    Repository in owner/repo format.
        log_dir:        Directory where execution logs are written.
        max_executions: Maximum processing attempts per milestone before skipping.
        prompt:         Prompt text passed to the AI agent (default: "/ralph:dev").
        vcs:            VCSClient instance (defaults to VCSClient()).
        agent:          AIAgent instance (defaults to AIAgent()).
        exec_log:       ExecutionLog instance (defaults to ExecutionLog(log_dir, github_repo)).
    """
    exec_log = exec_log or ExecutionLog(log_dir, github_repo)
    owner, repo = github_repo.split("/", 1)
    issue_filter = IssueFilter()
    vcs = vcs or VCSClient()

    _log.info("Service run started owner=%s repo=%s", owner, repo)

    milestones = vcs.list_milestones(owner, repo)
    if not milestones:
        _log.info("No open milestones found owner=%s repo=%s", owner, repo)
        return

    _log.info("Found open milestones count=%d owner=%s repo=%s", len(milestones), owner, repo)

    for milestone in milestones:
        _log.info("Processing milestone milestone_url=%s title=%s", milestone.url, milestone.title)

        fetched_issues = vcs.fetch_issues(owner, repo, milestone.title)
        actionable_issues = issue_filter.get_actionable_issues(fetched_issues)

        if len(actionable_issues) == 0:
            _log.info("No actionable issues, skipping milestone_url=%s", milestone.url)
            continue

        exec_count = exec_log.get_count(milestone.url)
        if exec_count >= max_executions:
            _log.warning(
                "Milestone exceeded max executions, skipping milestone_url=%s count=%d max=%d actionable_issues=%d",
                milestone.url, exec_count, max_executions, len(actionable_issues),
            )
            continue

        _log.info(
            "Running copilot agent milestone_url=%s issues=%d attempt=%d",
            milestone.url, len(actionable_issues), exec_count + 1,
        )

        (agent or AIAgent(alias=agent_name, prompt=f"{prompt} #{milestone.number}")).run()

        exec_log.update(milestone.url, [])
        _log.info("Completed milestone processing milestone_url=%s attempt=%d", milestone.url, exec_count + 1)

    _log.info("Service run completed")
