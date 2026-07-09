#!/usr/bin/env python3
"""Unit tests for the dev milestone handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

from afk.features.dev.handler import dev
from afk.infrastructure.ai_agent import AIAgent
from afk.shared.execution_log import ExecutionLog
from modules.github.domain.issue import Issue
from modules.github.domain.milestone import Milestone
from modules.github.infrastructure.vcs_client import VCSClient

_LOG_DIR = Path("logs")
_GITHUB_REPO = "owner/repo"
_MILESTONE_URL = "https://github.com/owner/repo/milestone/3"


class TestDevMilestoneLoop:
    """Feature: Dev Milestone Loop"""

    def test_no_open_milestones_early_exit(self, caplog):
        # Scenario: No open milestones found — early exit
        vcs = MagicMock(spec=VCSClient)
        vcs.list_milestones.return_value = []
        agent = MagicMock(spec=AIAgent)
        exec_log = MagicMock(spec=ExecutionLog)

        with caplog.at_level(logging.INFO):
            dev(_GITHUB_REPO, _LOG_DIR, max_executions=5, vcs=vcs, agent=agent, exec_log=exec_log)

        vcs.list_milestones.assert_called_once_with("owner", "repo")
        vcs.fetch_issues.assert_not_called()
        agent.run.assert_not_called()
        assert "No open milestones found" in caplog.text

    def test_milestone_with_no_actionable_issues_and_prior_count_resets_log(self, caplog):
        # Scenario: Milestone with no actionable issues and prior count resets execution log
        milestone = Milestone(
            id="M1",
            number=3,
            title="Sprint 3",
            description="",
            url=_MILESTONE_URL,
        )
        vcs = MagicMock(spec=VCSClient)
        vcs.list_milestones.return_value = [milestone]
        vcs.fetch_issues.return_value = [
            Issue(number=14, title="Refactor", body="", url="https://github.com/owner/repo/issues/14", labels=["spec"])
        ]
        agent = MagicMock(spec=AIAgent)
        exec_log = MagicMock(spec=ExecutionLog)
        exec_log.get_count.return_value = 3

        with caplog.at_level(logging.INFO):
            dev(_GITHUB_REPO, _LOG_DIR, max_executions=5, vcs=vcs, agent=agent, exec_log=exec_log)

        vcs.fetch_issues.assert_called_once_with("owner", "repo", milestone.title)
        exec_log.get_count.assert_called_once_with(milestone.url)
        exec_log.reset.assert_called_once_with(milestone.url)
        exec_log.update.assert_not_called()
        agent.run.assert_not_called()
        assert "No actionable issues, skipping" in caplog.text
        assert "Reset execution count (all issues resolved)" in caplog.text

    def test_milestone_with_no_actionable_issues_and_zero_count_does_not_reset_log(self, caplog):
        # Scenario: Milestone with no actionable issues and zero count does not reset execution log
        milestone = Milestone(
            id="M1",
            number=3,
            title="Sprint 3",
            description="",
            url=_MILESTONE_URL,
        )
        vcs = MagicMock(spec=VCSClient)
        vcs.list_milestones.return_value = [milestone]
        vcs.fetch_issues.return_value = [
            Issue(number=14, title="Refactor", body="", url="https://github.com/owner/repo/issues/14", labels=["spec"])
        ]
        agent = MagicMock(spec=AIAgent)
        exec_log = MagicMock(spec=ExecutionLog)
        exec_log.get_count.return_value = 0

        with caplog.at_level(logging.INFO):
            dev(_GITHUB_REPO, _LOG_DIR, max_executions=5, vcs=vcs, agent=agent, exec_log=exec_log)

        vcs.fetch_issues.assert_called_once_with("owner", "repo", milestone.title)
        exec_log.get_count.assert_called_once_with(milestone.url)
        exec_log.reset.assert_not_called()
        exec_log.update.assert_not_called()
        agent.run.assert_not_called()
        assert "No actionable issues, skipping" in caplog.text

    def test_milestone_at_max_executions_is_skipped(self, caplog):
        # Scenario: Milestone at max executions is skipped
        milestone = Milestone(
            id="M1",
            number=3,
            title="Sprint 3",
            description="",
            url=_MILESTONE_URL,
        )
        vcs = MagicMock(spec=VCSClient)
        vcs.list_milestones.return_value = [milestone]
        vcs.fetch_issues.return_value = [
            Issue(number=14, title="Build feature", body="", url="https://github.com/owner/repo/issues/14", labels=["ready"])
        ]
        agent = MagicMock(spec=AIAgent)
        exec_log = MagicMock(spec=ExecutionLog)
        exec_log.get_count.return_value = 5

        with caplog.at_level(logging.WARNING):
            dev(_GITHUB_REPO, _LOG_DIR, max_executions=5, vcs=vcs, agent=agent, exec_log=exec_log)

        exec_log.get_count.assert_called_once_with(milestone.url)
        exec_log.update.assert_not_called()
        agent.run.assert_not_called()
        assert "Milestone exceeded max executions, skipping" in caplog.text

    @patch("afk.features.dev.handler.AIAgent")
    def test_actionable_milestone_invokes_agent_and_updates_execution_log(self, mock_agent_class):
        # Scenario: Actionable milestone invokes agent and updates execution log
        milestone = Milestone(
            id="M1",
            number=3,
            title="Sprint 3",
            description="",
            url=_MILESTONE_URL,
        )
        vcs = MagicMock(spec=VCSClient)
        vcs.list_milestones.return_value = [milestone]
        vcs.fetch_issues.return_value = [
            Issue(number=14, title="Build feature", body="", url="https://github.com/owner/repo/issues/14", labels=["ready"])
        ]
        exec_log = MagicMock(spec=ExecutionLog)
        exec_log.get_count.return_value = 0
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        dev(_GITHUB_REPO, _LOG_DIR, max_executions=5, vcs=vcs, exec_log=exec_log)

        vcs.list_milestones.assert_called_once_with("owner", "repo")
        vcs.fetch_issues.assert_called_once_with("owner", "repo", milestone.title)
        exec_log.get_count.assert_called_once_with(milestone.url)
        mock_agent_class.assert_called_once_with(alias="yolo", prompt="/ralph:dev Sprint 3")
        mock_agent.run.assert_called_once_with()
        exec_log.update.assert_called_once_with(milestone.url, [14], "owner", "repo", "milestone", 3, milestone.title)

    @patch("afk.features.dev.handler.ExecutionLog")
    def test_default_execution_log_uses_dev_log_name(self, mock_execution_log_class):
        # Scenario: Default ExecutionLog is created with dev log name
        milestone = Milestone(
            id="M1",
            number=3,
            title="Sprint 3",
            description="",
            url=_MILESTONE_URL,
        )
        vcs = MagicMock(spec=VCSClient)
        vcs.list_milestones.return_value = [milestone]
        vcs.fetch_issues.return_value = []
        exec_log = MagicMock(spec=ExecutionLog)
        exec_log.get_count.return_value = 0
        mock_execution_log_class.return_value = exec_log

        dev(_GITHUB_REPO, _LOG_DIR, max_executions=5, vcs=vcs, agent=MagicMock(spec=AIAgent))

        mock_execution_log_class.assert_called_once_with(_LOG_DIR, _GITHUB_REPO, "dev")
