"""Unit tests for the close_ticket handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.github_tracker.features.close_ticket.handler import close_ticket
from modules.github_tracker.infrastructure.tests.fake_gh_cli import FakeGhCli


class TestCloseTicket:
    """Feature: Close Ticket"""

    def test_close_with_comment_passes_the_comment(self):
        # Scenario: Close with comment passes the comment
        gh = FakeGhCli(repo="owner/repo")

        close_ticket(6, "Done", gh=gh)

        assert gh.issue_close_calls == [{"repo": "owner/repo", "issue_number": 6, "comment": "Done"}]

    def test_close_without_comment_omits_the_comment(self):
        # Scenario: Close without comment omits the comment
        gh = FakeGhCli(repo="owner/repo")

        close_ticket(6, "", gh=gh)

        assert gh.issue_close_calls == [{"repo": "owner/repo", "issue_number": 6, "comment": None}]
