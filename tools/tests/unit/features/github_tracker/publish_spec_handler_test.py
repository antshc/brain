"""Unit tests for the publish_spec handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.github_tracker.features.publish_spec.handler import publish_spec
from modules.github_tracker.infrastructure.tests.fake_gh_cli import FakeGhCli


class TestPublishSpec:
    """Feature: Publish Spec"""

    def test_existing_matching_milestone_is_reused_unchanged(self):
        # Scenario: Existing matching milestone is reused unchanged
        gh = FakeGhCli(
            repo="owner/repo",
            milestones_raw_output=[{"title": "FEAT-1: Original Title"}],
            issue_create_output="https://github.com/owner/repo/issues/42",
        )

        issue_number = publish_spec("FEAT-1", "New Title", "main", gh=gh)

        assert issue_number == 42
        assert gh.milestone_create_calls == []
        assert gh.issue_edit_milestone_calls == [("owner/repo", 42, "FEAT-1: Original Title")]
        assert gh.issue_create_calls == [
            {"repo": "owner/repo", "title": "FEAT-1: New Title", "body": None, "label": "spec", "milestone": None}
        ]

    def test_no_matching_milestone_creates_one_and_assigns_the_new_issue(self):
        # Scenario: No matching milestone creates one and assigns the new issue
        gh = FakeGhCli(
            repo="owner/repo",
            milestones_raw_output=[],
            milestone_create_raw_output={"title": "FEAT-1: New Title"},
            issue_create_output="https://github.com/owner/repo/issues/7",
        )

        issue_number = publish_spec("FEAT-1", "New Title", "main", gh=gh)

        assert issue_number == 7
        assert gh.milestone_create_calls == [
            ("owner/repo", "FEAT-1: New Title", "**Feature ID:** `FEAT-1`\n**Target Branch:** `main`")
        ]
        assert gh.issue_edit_milestone_calls == [("owner/repo", 7, "FEAT-1: New Title")]
