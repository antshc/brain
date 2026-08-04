"""Unit tests for the label_ticket handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.github_tracker.features.label_ticket.handler import label_ticket
from modules.github_tracker.infrastructure.tests.fake_gh_cli import FakeGhCli


class TestLabelTicket:
    """Feature: Label Ticket"""

    def test_add_and_remove_labels_are_both_applied(self):
        # Scenario: Add and remove labels are both applied
        gh = FakeGhCli(repo="owner/repo")

        label_ticket(4, "hitl", "spec", gh=gh)

        assert gh.issue_edit_labels_calls == [
            {"repo": "owner/repo", "issue_number": 4, "add_labels": "hitl", "remove_labels": "spec"}
        ]

    def test_empty_add_or_remove_labels_is_omitted(self):
        # Scenario: Empty add or remove labels is omitted
        gh = FakeGhCli(repo="owner/repo")

        label_ticket(4, "", "spec", gh=gh)

        assert gh.issue_edit_labels_calls == [
            {"repo": "owner/repo", "issue_number": 4, "add_labels": None, "remove_labels": "spec"}
        ]
