"""Unit tests for GhCli command construction.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

import json
from unittest.mock import Mock, patch

from modules.github_tracker.infrastructure.gh_cli import GhCli


class TestGhCliRepoResolution:
    """Feature: GhCli Repo Resolution"""

    @patch("modules.github_tracker.infrastructure.gh_cli.subprocess.run")
    def test_resolve_repo_uses_gh_repo_view_json(self, mock_run):
        # Scenario: resolve_repo uses gh repo view --json
        mock_run.return_value = Mock(stdout="owner/repo\n")

        result = GhCli().resolve_repo()

        assert result == "owner/repo"
        mock_run.assert_called_once_with(
            ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
            capture_output=True, text=True, check=True,
        )


class TestGhCliLabelCommands:
    """Feature: GhCli Label Commands"""

    @patch("modules.github_tracker.infrastructure.gh_cli.subprocess.run")
    def test_label_names_parses_json_name_list(self, mock_run):
        # Scenario: label_names parses JSON name list
        mock_run.return_value = Mock(stdout=json.dumps([{"name": "hitl"}, {"name": "spec"}]))

        result = GhCli().label_names("owner/repo")

        assert result == ["hitl", "spec"]
        mock_run.assert_called_once_with(
            ["gh", "label", "list", "--repo", "owner/repo", "--json", "name"],
            capture_output=True, text=True, check=True,
        )

    @patch("modules.github_tracker.infrastructure.gh_cli.subprocess.run")
    def test_label_create_passes_name_color_and_description(self, mock_run):
        # Scenario: label_create passes name, color, and description
        GhCli().label_create("owner/repo", "hitl", "fbca04", "Requires human implementation")

        mock_run.assert_called_once_with(
            [
                "gh", "label", "create", "hitl",
                "--repo", "owner/repo",
                "--color", "fbca04",
                "--description", "Requires human implementation",
            ],
            capture_output=True, text=True, check=True,
        )


class TestGhCliMilestoneCommands:
    """Feature: GhCli Milestone Commands"""

    @patch("modules.github_tracker.infrastructure.gh_cli.subprocess.run")
    def test_milestone_create_raw_posts_title_and_description_fields(self, mock_run):
        # Scenario: milestone_create_raw posts title and description fields
        mock_run.return_value = Mock(stdout=json.dumps({"title": "FEAT-1: Title"}))

        result = GhCli().milestone_create_raw("owner/repo", "FEAT-1: Title", "desc\nline2")

        assert result == {"title": "FEAT-1: Title"}
        mock_run.assert_called_once_with(
            [
                "gh", "api", "repos/owner/repo/milestones",
                "--method", "POST",
                "--field", "title=FEAT-1: Title",
                "--field", "description=desc\nline2",
            ],
            capture_output=True, text=True, check=True,
        )


class TestGhCliIssueCreateCommand:
    """Feature: GhCli Issue Create Command"""

    @patch("modules.github_tracker.infrastructure.gh_cli.subprocess.run")
    def test_issue_create_omits_optional_flags_when_not_given(self, mock_run):
        # Scenario: issue_create omits optional flags when not given
        mock_run.return_value = Mock(stdout="https://github.com/owner/repo/issues/1\n")

        result = GhCli().issue_create("owner/repo", "Title")

        assert result == "https://github.com/owner/repo/issues/1"
        mock_run.assert_called_once_with(
            ["gh", "issue", "create", "--repo", "owner/repo", "--title", "Title"],
            capture_output=True, text=True, check=True,
        )

    @patch("modules.github_tracker.infrastructure.gh_cli.subprocess.run")
    def test_issue_create_includes_body_label_and_milestone_when_given(self, mock_run):
        # Scenario: issue_create includes body, label, and milestone when given
        mock_run.return_value = Mock(stdout="https://github.com/owner/repo/issues/2\n")

        GhCli().issue_create("owner/repo", "Title", body="Body", label="spec", milestone="Sprint 1")

        mock_run.assert_called_once_with(
            [
                "gh", "issue", "create", "--repo", "owner/repo", "--title", "Title",
                "--body", "Body", "--label", "spec", "--milestone", "Sprint 1",
            ],
            capture_output=True, text=True, check=True,
        )
