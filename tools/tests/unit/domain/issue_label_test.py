#!/usr/bin/env python3
"""Unit tests for Issue.is_actionable.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.github.domain.issue import Issue


def make_issue(**kwargs) -> Issue:
    defaults = {"number": 1, "title": "t", "body": "", "url": "http://x"}
    return Issue(**{**defaults, **kwargs})


class TestIssueActionability:
    """Feature: Issue Actionability"""

    def test_issue_with_ready_label_is_actionable(self):
        # Scenario: Issue with ready label is actionable
        assert make_issue(labels=["ready"]).is_actionable is True

    def test_issue_with_prd_label_is_actionable(self):
        # Scenario: Issue with prd label is actionable
        assert make_issue(labels=["prd"]).is_actionable is True

    def test_issue_with_ready_and_prd_labels_is_actionable(self):
        # Scenario: Issue with ready and prd labels is actionable
        assert make_issue(labels=["ready", "prd"]).is_actionable is True

    def test_issue_with_no_labels_is_not_actionable(self):
        # Scenario: Issue with no labels is not actionable
        assert make_issue(labels=[]).is_actionable is False

    def test_issue_with_unrelated_label_only_is_not_actionable(self):
        # Scenario: Issue with unrelated label only is not actionable
        assert make_issue(labels=["bug"]).is_actionable is False

    def test_issue_with_ready_and_blocked_is_not_actionable(self):
        # Scenario: Issue with ready and blocked labels is not actionable
        assert make_issue(labels=["ready", "blocked"]).is_actionable is False

    def test_issue_with_prd_and_hitl_is_not_actionable(self):
        # Scenario: Issue with prd and hitl labels is not actionable
        assert make_issue(labels=["prd", "hitl"]).is_actionable is False

    def test_issue_with_blocked_label_only_is_not_actionable(self):
        # Scenario: Issue with blocked label only is not actionable
        assert make_issue(labels=["blocked"]).is_actionable is False

    def test_issue_with_hitl_label_only_is_not_actionable(self):
        # Scenario: Issue with hitl label only is not actionable
        assert make_issue(labels=["hitl"]).is_actionable is False

    def test_issue_with_ready_and_hitl_is_not_actionable(self):
        # Scenario: Issue with ready and hitl labels is not actionable
        assert make_issue(labels=["ready", "hitl"]).is_actionable is False
