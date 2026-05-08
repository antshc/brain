#!/usr/bin/env python3
"""Integration tests for the review_pull_requests handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from pathlib import Path
from unittest.mock import MagicMock

from ralph_tools.infrastructure.ai_agent import AIAgent
from ralph_tools.infrastructure.gh_cli import GhCli
from ralph_tools.infrastructure.vcs_client import VCSClient
from ralph_tools.shared.execution_log import ExecutionLog
from ralph_tools.features.review_pull_requests.handler import review_pull_requests

_USER = "dev"
_REPO = "owner/repo"
_LOG_DIR = Path("/tmp/ralph-test-logs")

_PR1_URL = "https://github.com/owner/repo/pull/1"
_PR2_URL = "https://github.com/owner/repo/pull/2"
_PR3_URL = "https://github.com/owner/repo/pull/3"


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


def make_pr_dict(url: str) -> dict:
    return {"url": url}


def setup_handler(pr_urls: list[str], threads_by_pr_number: dict[int, list[dict]], exec_count_by_url: dict[str, int] | None = None):
    """Return (mock_gh, vcs, mock_agent, mock_exec_log) wired for a multi-PR test."""
    mock_gh = MagicMock(spec=GhCli)
    mock_gh.pr_list.return_value = [make_pr_dict(url) for url in pr_urls]
    mock_gh.fetch_threads_raw.side_effect = lambda owner, repo, number: threads_by_pr_number.get(number, [])
    vcs = VCSClient(gh=mock_gh)

    mock_agent = MagicMock(spec=AIAgent)

    mock_exec_log = MagicMock(spec=ExecutionLog)
    if exec_count_by_url:
        mock_exec_log.get_count.side_effect = lambda url: exec_count_by_url.get(url, 0)
    else:
        mock_exec_log.get_count.return_value = 0

    return mock_gh, vcs, mock_agent, mock_exec_log


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestReviewPullRequests:
    """Feature: Review Multiple PRs (review_pull_requests handler)"""

    def test_multiple_prs_with_actionable_threads_are_all_processed(self):
        # Scenario: Multiple PRs with actionable threads are all processed
        threads_by_pr = {
            1: [make_raw_thread("T1", "fix!: issue in PR1")],
            2: [make_raw_thread("T2", "suggest!: extract in PR2")],
        }
        mock_gh, vcs, mock_agent, mock_exec_log = setup_handler([_PR1_URL, _PR2_URL], threads_by_pr)

        review_pull_requests(_USER, _REPO, _LOG_DIR, max_executions=5, vcs=vcs, agent=mock_agent, exec_log=mock_exec_log)

        assert mock_agent.review.call_count == 2
        mock_exec_log.update.assert_any_call(_PR1_URL, ["T1"])
        mock_exec_log.update.assert_any_call(_PR2_URL, ["T2"])

    def test_no_open_prs_early_exit(self):
        # Scenario: No open PRs found — early exit
        mock_gh, vcs, mock_agent, mock_exec_log = setup_handler([], {})

        review_pull_requests(_USER, _REPO, _LOG_DIR, max_executions=5, vcs=vcs, agent=mock_agent, exec_log=mock_exec_log)

        mock_agent.review.assert_not_called()

    def test_mix_of_actionable_and_non_actionable_prs(self):
        # Scenario: Mix of actionable and non-actionable PRs
        threads_by_pr = {
            1: [make_raw_thread("T1", "fix!: issue")],
            2: [make_raw_thread("T2", "nit: style")],
            3: [make_raw_thread("T3", "suggest!: extract")],
        }
        mock_gh, vcs, mock_agent, mock_exec_log = setup_handler([_PR1_URL, _PR2_URL, _PR3_URL], threads_by_pr)

        review_pull_requests(_USER, _REPO, _LOG_DIR, max_executions=5, vcs=vcs, agent=mock_agent, exec_log=mock_exec_log)

        assert mock_agent.review.call_count == 2
        mock_exec_log.update.assert_any_call(_PR1_URL, ["T1"])
        mock_exec_log.update.assert_any_call(_PR3_URL, ["T3"])

    def test_pr_at_max_executions_skipped_while_others_processed(self):
        # Scenario: PR at max executions is skipped while others are processed
        threads_by_pr = {
            1: [make_raw_thread("T1", "fix!: issue in PR1")],
            2: [make_raw_thread("T2", "fix!: issue in PR2")],
        }
        exec_counts = {_PR1_URL: 5, _PR2_URL: 0}
        mock_gh, vcs, mock_agent, mock_exec_log = setup_handler([_PR1_URL, _PR2_URL], threads_by_pr, exec_counts)

        review_pull_requests(_USER, _REPO, _LOG_DIR, max_executions=5, vcs=vcs, agent=mock_agent, exec_log=mock_exec_log)

        assert mock_agent.review.call_count == 1
        mock_exec_log.update.assert_called_once_with(_PR2_URL, ["T2"])

    def test_pr_with_no_actionable_threads_and_prior_count_resets_log(self):
        # Scenario: PR with no actionable threads and prior count resets execution log
        threads_by_pr = {1: [make_raw_thread("T1", "nit: style")]}
        mock_gh, vcs, mock_agent, mock_exec_log = setup_handler([_PR1_URL], threads_by_pr, {_PR1_URL: 3})

        review_pull_requests(_USER, _REPO, _LOG_DIR, max_executions=5, vcs=vcs, agent=mock_agent, exec_log=mock_exec_log)

        mock_agent.review.assert_not_called()
        mock_exec_log.reset.assert_called_once_with(_PR1_URL)
