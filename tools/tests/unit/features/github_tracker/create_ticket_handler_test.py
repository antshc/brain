"""Unit tests for the create_ticket handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.github_tracker.features.create_ticket.handler import create_ticket
from modules.github_tracker.infrastructure.tests.fake_gh_cli import FakeGhCli


class TestCreateTicket:
    """Feature: Create Ticket"""

    def test_new_ticket_returns_its_issue_number(self):
        # Scenario: New ticket returns its issue number
        gh = FakeGhCli(repo="owner/repo", issue_create_output="https://github.com/owner/repo/issues/9")

        issue_number = create_ticket("Title", "Body", "Sprint 1", "hitl", gh=gh)

        assert issue_number == 9
        assert gh.issue_create_calls == [
            {"repo": "owner/repo", "title": "Title", "body": "Body", "label": "hitl", "milestone": "Sprint 1"}
        ]
