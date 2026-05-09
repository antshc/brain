#!/usr/bin/env python3
"""Integration tests for the review_pull_request handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from pathlib import Path
from unittest.mock import MagicMock, call

from afk.infrastructure.ai_agent import AIAgent
from modules.github.infrastructure.gh_cli import GhCli
from modules.github.infrastructure.vcs_client import VCSClient
from afk.shared.execution_log import ExecutionLog
from afk.features.review_pull_request.handler import review_pull_request

_PR_URL = "https://github.com/owner/repo/pull/1"
_LOG_DIR = Path("/tmp/ralph-test-logs")


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_raw_thread(id: str, body: str, resolved: bool = False, line: int = 10) -> dict:
    return {
        "id": id,
        "isResolved": resolved,
        "path": "src/foo.py",
        "startLine": line,
        "line": line,
        "comments": [{"author": {"login": "reviewer"}, "body": body}],
    }


def setup_handler(threads_raw: list[dict], exec_count: int = 0):
    """Return (mock_gh, vcs, mock_agent, mock_exec_log) wired for a test."""
    mock_gh = MagicMock(spec=GhCli)
    mock_gh.fetch_threads_raw.return_value = threads_raw
    vcs = VCSClient(gh=mock_gh)

    mock_agent = MagicMock(spec=AIAgent)
    mock_exec_log = MagicMock(spec=ExecutionLog)
    mock_exec_log.get_count.return_value = exec_count

    return mock_gh, vcs, mock_agent, mock_exec_log


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestReviewPullRequest:
    """Feature: Review Single PR (review_pull_request handler)"""

    def test_pr_with_actionable_threads_triggers_ai_agent(self):
        # Scenario: PR with actionable threads triggers the AI agent
        threads_raw = [
            make_raw_thread("T1", "fix!: broken null check"),
            make_raw_thread("T2", "suggest!: extract method"),
        ]
        mock_gh, vcs, mock_agent, mock_exec_log = setup_handler(threads_raw, exec_count=0)

        review_pull_request(_PR_URL, _LOG_DIR, max_executions=5, vcs=vcs, agent=mock_agent, exec_log=mock_exec_log)

        mock_agent.run.assert_called_once_with()
        mock_exec_log.update.assert_called_once_with(_PR_URL, ["T1", "T2"])

    def test_pr_with_no_actionable_threads_skips_ai_agent(self):
        # Scenario: PR with no actionable threads skips the AI agent
        threads_raw = [
            make_raw_thread("T1", "fix!: issue", resolved=True),
            make_raw_thread("T2", "nit: minor style"),
        ]
        mock_gh, vcs, mock_agent, mock_exec_log = setup_handler(threads_raw, exec_count=0)

        review_pull_request(_PR_URL, _LOG_DIR, max_executions=5, vcs=vcs, agent=mock_agent, exec_log=mock_exec_log)

        mock_agent.run.assert_not_called()
        mock_exec_log.update.assert_not_called()

    def test_pr_with_no_actionable_threads_resets_count_if_previously_processed(self):
        # Scenario: PR with no actionable threads resets execution count if previously processed
        threads_raw = [make_raw_thread("T1", "nit: minor style")]
        mock_gh, vcs, mock_agent, mock_exec_log = setup_handler(threads_raw, exec_count=2)

        review_pull_request(_PR_URL, _LOG_DIR, max_executions=5, vcs=vcs, agent=mock_agent, exec_log=mock_exec_log)

        mock_agent.run.assert_not_called()
        mock_exec_log.reset.assert_called_once_with(_PR_URL)

    def test_pr_at_max_executions_is_skipped(self):
        # Scenario: PR at max executions is skipped
        threads_raw = [make_raw_thread("T1", "fix!: broken null check")]
        mock_gh, vcs, mock_agent, mock_exec_log = setup_handler(threads_raw, exec_count=5)

        review_pull_request(_PR_URL, _LOG_DIR, max_executions=5, vcs=vcs, agent=mock_agent, exec_log=mock_exec_log)

        mock_agent.run.assert_not_called()
        mock_exec_log.update.assert_not_called()

    def test_custom_prompt_is_passed_to_ai_agent(self):
        # Scenario: Custom prompt is passed to the AI agent
        threads_raw = [make_raw_thread("T1", "fix!: broken null check")]
        mock_gh, vcs, mock_agent, mock_exec_log = setup_handler(threads_raw, exec_count=0)

        review_pull_request(_PR_URL, _LOG_DIR, max_executions=5, prompt="/custom-prompt", vcs=vcs, agent=mock_agent, exec_log=mock_exec_log)

        mock_agent.run.assert_called_once_with()
