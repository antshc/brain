"""Unit tests for the read_ticket handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.github_tracker.features.read_ticket.handler import read_ticket
from modules.github_tracker.infrastructure.tests.fake_gh_cli import FakeGhCli


class TestReadTicket:
    """Feature: Read Ticket"""

    def test_ticket_returns_number_title_body_labels_and_comments(self):
        # Scenario: Ticket returns number, title, body, labels, and comments
        gh = FakeGhCli(
            repo="owner/repo",
            issue_view_raw_output={
                "number": 12,
                "title": "Bug",
                "body": "steps",
                "labels": [{"name": "hitl"}],
                "comments": [{"body": "ack"}],
            },
        )

        ticket = read_ticket(12, gh=gh)

        assert ticket == {"number": 12, "title": "Bug", "body": "steps", "labels": ["hitl"], "comments": ["ack"]}
