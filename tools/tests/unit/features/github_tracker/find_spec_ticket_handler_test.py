"""Unit tests for the find_spec_ticket handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.github_tracker.features.find_spec_ticket.handler import find_spec_ticket
from modules.github_tracker.infrastructure.tests.fake_gh_cli import FakeGhCli


class TestFindSpecTicket:
    """Feature: Find Spec Ticket"""

    def test_matching_spec_ticket_returns_number_title_body_and_comments(self):
        # Scenario: Matching spec ticket returns number, title, body, and comments
        gh = FakeGhCli(
            repo="owner/repo",
            issue_list_raw_output=[
                {"number": 5, "title": "FEAT-1: Spec", "body": "details", "comments": [{"body": "lgtm"}]}
            ],
        )

        ticket = find_spec_ticket("FEAT-1: Spec", gh=gh)

        assert ticket == {"number": 5, "title": "FEAT-1: Spec", "body": "details", "comments": ["lgtm"]}

    def test_no_matching_spec_ticket_reports_not_found(self):
        # Scenario: No matching spec ticket reports not found
        gh = FakeGhCli(repo="owner/repo", issue_list_raw_output=[])

        ticket = find_spec_ticket("FEAT-1: Spec", gh=gh)

        assert ticket is None
