#!/usr/bin/env python3
"""Unit tests for Issue.is_actionable().

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.github.domain.issue import Issue
from modules.github.domain.issue_comment import IssueComment


class TestIssueActionability:
    """Feature: Issue Actionability"""

    def test_issue_with_ready_label_is_actionable(self):
        # Scenario: Issue with ready label is actionable
        issue = Issue(number=12, title="Issue", body="", url="https://example.com/issues/12", labels=["ready"])
        assert issue.is_actionable is True

    def test_issue_with_prd_label_is_actionable(self):
        # Scenario: Issue with prd label is actionable
        issue = Issue(number=12, title="Issue", body="", url="https://example.com/issues/12", labels=["prd"])
        assert issue.is_actionable is True

    def test_issue_with_ready_and_prd_labels_is_actionable(self):
        # Scenario: Issue with ready and prd labels is actionable
        issue = Issue(number=12, title="Issue", body="", url="https://example.com/issues/12", labels=["ready", "prd"])
        assert issue.is_actionable is True

    def test_issue_with_no_actionable_labels_is_not_actionable(self):
        # Scenario: Issue with no actionable labels is not actionable
        issue = Issue(number=12, title="Issue", body="", url="https://example.com/issues/12", labels=["enhancement"])
        assert issue.is_actionable is False

    def test_issue_with_ready_and_blocked_labels_is_not_actionable(self):
        # Scenario: Issue with ready and blocked labels is not actionable
        issue = Issue(number=12, title="Issue", body="", url="https://example.com/issues/12", labels=["ready", "blocked"])
        assert issue.is_actionable is False

    def test_issue_with_prd_and_hitl_labels_is_not_actionable(self):
        # Scenario: Issue with prd and hitl labels is not actionable
        issue = Issue(number=12, title="Issue", body="", url="https://example.com/issues/12", labels=["prd", "hitl"])
        assert issue.is_actionable is False

    def test_issue_with_ready_prd_and_blocking_labels_is_not_actionable(self):
        # Scenario: Issue with ready, prd, and blocking labels is not actionable
        issue = Issue(number=12, title="Issue", body="", url="https://example.com/issues/12", labels=["ready", "prd", "blocked", "hitl"])
        assert issue.is_actionable is False

    def test_issue_with_actionable_and_unrelated_labels_is_actionable(self):
        # Scenario: Issue with actionable and unrelated labels is actionable
        issue = Issue(number=12, title="Issue", body="", url="https://example.com/issues/12", labels=["ready", "bug"])
        assert issue.is_actionable is True

    def test_issue_comment_fields_are_preserved(self):
        # Scenario: Issue comment fields are preserved
        comment = IssueComment(id="IC_1", body="Need more context", created_at="2026-05-24T10:00:00Z")
        issue = Issue(
            number=12,
            title="Issue",
            body="",
            url="https://example.com/issues/12",
            labels=["ready"],
            comments=[comment],
        )
        assert issue.comments == [comment]
