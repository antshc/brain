#!/usr/bin/env python3
"""Integration tests for the review_pull_request handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.

Running modes
-------------
Mock mode (default)::

    python3 -m pytest integration_tests/ -v

Real mode (hits live GitHub API and Copilot CLI)::

    python3 -m pytest integration_tests/ --real -v
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from infrastructure.ai_agent import AIAgent
from infrastructure.gh_cli import GhCli
from infrastructure.vcs_client import VCSClient
from shared.execution_log import ExecutionLog
from features.review_pull_request.handler import review_pull_request

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


def setup_handler(
    threads_raw: list[dict],
    exec_count: int = 0,
    *,
    use_real: bool = False,
    real_config: dict | None = None,
):
    """Return (pr_url, vcs, agent, exec_log) wired for a test.

    In mock mode (default) the GhCli, AIAgent, and ExecutionLog are replaced
    with MagicMock instances so that no external processes are spawned.

    In real mode (--real flag) the real implementations are returned and
    pr_url, log_dir, and repo are read from integrationtest-config.json.
    The threads_raw and exec_count parameters are ignored in real mode.
    """
    if use_real:
        cfg = real_config or {}
        pr_url = cfg.get("pr_url", _PR_URL)
        log_dir = Path(cfg.get("log_dir", str(_LOG_DIR)))
        repo = cfg.get("github_repo", "owner/repo")
        return pr_url, VCSClient(), AIAgent(), ExecutionLog(log_dir, repo)

    mock_gh = MagicMock(spec=GhCli)
    mock_gh.fetch_threads_raw.return_value = threads_raw
    vcs = VCSClient(gh=mock_gh)

    mock_agent = MagicMock(spec=AIAgent)
    mock_exec_log = MagicMock(spec=ExecutionLog)
    mock_exec_log.get_count.return_value = exec_count

    return _PR_URL, vcs, mock_agent, mock_exec_log


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestReviewPullRequest:
    """Feature: Review Single PR (review_pull_request handler)"""

    @pytest.mark.mock_only
    def test_pr_with_actionable_threads_triggers_ai_agent(self, use_real, real_config):
        # Scenario: PR with actionable threads triggers the AI agent
        threads_raw = [
            make_raw_thread("T1", "fix!: broken null check"),
            make_raw_thread("T2", "suggest!: extract method"),
        ]
        pr_url, vcs, agent, exec_log = setup_handler(threads_raw, exec_count=0, use_real=use_real, real_config=real_config)

        with patch.object(vcs, 'checkout_pr') as mock_checkout:
            review_pull_request(pr_url, _LOG_DIR, max_executions=5, vcs=vcs, agent=agent, exec_log=exec_log)

        mock_checkout.assert_called_once_with(pr_url)
        agent.review.assert_called_once()
        call_threads, call_prompt = agent.review.call_args.args
        assert len(call_threads) == 2
        assert call_prompt == "/review"
        exec_log.update.assert_called_once_with(pr_url, ["T1", "T2"])

    @pytest.mark.mock_only
    def test_pr_with_no_actionable_threads_skips_ai_agent(self, use_real, real_config):
        # Scenario: PR with no actionable threads skips the AI agent
        threads_raw = [
            make_raw_thread("T1", "fix!: issue", resolved=True),
            make_raw_thread("T2", "nit: minor style"),
        ]
        pr_url, vcs, agent, exec_log = setup_handler(threads_raw, exec_count=0, use_real=use_real, real_config=real_config)

        review_pull_request(pr_url, _LOG_DIR, max_executions=5, vcs=vcs, agent=agent, exec_log=exec_log)

        agent.review.assert_not_called()
        exec_log.update.assert_not_called()

    @pytest.mark.mock_only
    def test_pr_with_no_actionable_threads_resets_count_if_previously_processed(self, use_real, real_config):
        # Scenario: PR with no actionable threads resets execution count if previously processed
        threads_raw = [make_raw_thread("T1", "nit: minor style")]
        pr_url, vcs, agent, exec_log = setup_handler(threads_raw, exec_count=2, use_real=use_real, real_config=real_config)

        review_pull_request(pr_url, _LOG_DIR, max_executions=5, vcs=vcs, agent=agent, exec_log=exec_log)

        agent.review.assert_not_called()
        exec_log.reset.assert_called_once_with(pr_url)

    @pytest.mark.mock_only
    def test_pr_at_max_executions_is_skipped(self, use_real, real_config):
        # Scenario: PR at max executions is skipped
        threads_raw = [make_raw_thread("T1", "fix!: broken null check")]
        pr_url, vcs, agent, exec_log = setup_handler(threads_raw, exec_count=5, use_real=use_real, real_config=real_config)

        review_pull_request(pr_url, _LOG_DIR, max_executions=5, vcs=vcs, agent=agent, exec_log=exec_log)

        agent.review.assert_not_called()
        exec_log.update.assert_not_called()

    @pytest.mark.mock_only
    def test_custom_prompt_is_passed_to_ai_agent(self, use_real, real_config):
        # Scenario: Custom prompt is passed to the AI agent
        threads_raw = [make_raw_thread("T1", "fix!: broken null check")]
        pr_url, vcs, agent, exec_log = setup_handler(threads_raw, exec_count=0, use_real=use_real, real_config=real_config)

        review_pull_request(pr_url, _LOG_DIR, max_executions=5, prompt="/custom-prompt", vcs=vcs, agent=agent, exec_log=exec_log)

        agent.review.assert_called_once()
        _, call_prompt = agent.review.call_args.args
        assert call_prompt == "/custom-prompt"


class TestReviewPullRequestSmoke:
    """Feature: Review Single PR (review_pull_request handler)"""

    def test_review_pull_request_with_no_actionable_threads_does_not_raise(self, use_real, real_config):
        # Scenario: review_pull_request with no actionable threads does not raise
        threads_raw = [make_raw_thread("T1", "nit: minor style")]
        pr_url, vcs, agent, exec_log = setup_handler(threads_raw, exec_count=0, use_real=use_real, real_config=real_config)

        review_pull_request(pr_url, _LOG_DIR, max_executions=5, vcs=vcs, agent=agent, exec_log=exec_log)
