#!/usr/bin/env python3
"""Unit tests for IssueFilter.get_actionable_issues.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.github.domain.issue import Issue
from modules.github.domain.services.issue_filter import IssueFilter


def make_issue(number: int, labels: list[str]) -> Issue:
    return Issue(number=number, title="t", body="", url="http://x", labels=labels)


class TestIssueFilter:
    """Feature: Issue Filter"""

    def test_only_actionable_issues_are_returned(self):
        # Scenario: Only actionable issues are returned from a mixed list
        issues = [
            make_issue(1, ["ready"]),
            make_issue(2, ["bug"]),
            make_issue(3, ["prd"]),
            make_issue(4, ["ready", "blocked"]),
        ]
        result = IssueFilter().get_actionable_issues(issues)
        assert [i.number for i in result] == [1, 3]

    def test_all_issues_actionable_all_returned(self):
        # Scenario: All actionable issues — all returned
        issues = [make_issue(1, ["ready"]), make_issue(2, ["prd"])]
        result = IssueFilter().get_actionable_issues(issues)
        assert len(result) == 2

    def test_no_actionable_issues_returns_empty_list(self):
        # Scenario: No actionable issues — empty list returned
        issues = [make_issue(1, ["bug"]), make_issue(2, ["blocked"])]
        result = IssueFilter().get_actionable_issues(issues)
        assert result == []

    def test_empty_input_returns_empty_list(self):
        # Scenario: Empty input returns empty list
        assert IssueFilter().get_actionable_issues([]) == []
