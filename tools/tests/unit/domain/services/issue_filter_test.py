#!/usr/bin/env python3
"""Unit tests for IssueFilter.get_actionable_issues().

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.github.domain.issue import Issue
from modules.github.domain.services.issue_filter import IssueFilter


def _make_issue(number: int, labels: list[str]) -> Issue:
    return Issue(
        number=number,
        title=f"Issue {number}",
        body="",
        url=f"https://example.com/issues/{number}",
        labels=labels,
    )


class TestIssueFilter:
    """Feature: Issue Filter"""

    def test_only_actionable_issues_are_returned(self):
        # Scenario: Only actionable issues are returned
        issues = [
            _make_issue(1, []),
            _make_issue(2, ["blocked"]),
            _make_issue(3, ["spec"]),
            _make_issue(4, ["bug", "hitl"]),
        ]
        result = IssueFilter().get_actionable_issues(issues)
        assert [issue.number for issue in result] == [1, 2]

    def test_all_issues_are_non_actionable_empty_list_returned(self):
        # Scenario: All issues are non-actionable — empty list returned
        issues = [
            _make_issue(1, ["spec"]),
            _make_issue(2, ["hitl"]),
        ]
        result = IssueFilter().get_actionable_issues(issues)
        assert result == []

    def test_empty_input_returns_empty_list(self):
        # Scenario: Empty input returns empty list
        assert IssueFilter().get_actionable_issues([]) == []
