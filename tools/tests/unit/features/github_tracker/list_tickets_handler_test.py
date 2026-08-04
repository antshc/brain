"""Unit tests for the list_tickets handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.github_tracker.features.list_tickets.handler import list_tickets
from modules.github_tracker.infrastructure.tests.fake_gh_cli import FakeGhCli


class TestListTickets:
    """Feature: List Tickets"""

    def test_matching_tickets_return_number_title_body_labels_and_comments(self):
        # Scenario: Matching tickets return number, title, body, labels, and comments
        gh = FakeGhCli(
            repo="owner/repo",
            issue_list_raw_output=[
                {"number": 1, "title": "A", "body": "a", "labels": [{"name": "hitl"}], "comments": []},
                {"number": 2, "title": "B", "body": "b", "labels": [], "comments": [{"body": "hi"}]},
            ],
        )

        tickets = list_tickets("open", "hitl", gh=gh)

        assert tickets == [
            {"number": 1, "title": "A", "body": "a", "labels": ["hitl"], "comments": []},
            {"number": 2, "title": "B", "body": "b", "labels": [], "comments": ["hi"]},
        ]

    def test_no_matching_tickets_returns_empty_array(self):
        # Scenario: No matching tickets returns empty array
        gh = FakeGhCli(repo="owner/repo", issue_list_raw_output=[])

        tickets = list_tickets("open", "hitl", gh=gh)

        assert tickets == []
