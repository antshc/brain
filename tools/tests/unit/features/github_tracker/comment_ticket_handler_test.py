"""Unit tests for the comment_ticket handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.github_tracker.features.comment_ticket.handler import comment_ticket
from modules.github_tracker.infrastructure.tests.fake_gh_cli import FakeGhCli


class TestCommentTicket:
    """Feature: Comment Ticket"""

    def test_comment_is_added_to_the_resolved_repo_and_issue(self):
        # Scenario: Comment is added to the resolved repo and issue
        gh = FakeGhCli(repo="owner/repo")

        result = comment_ticket(3, "Looks good", gh=gh)

        assert result is None
        assert gh.issue_comment_calls == [("owner/repo", 3, "Looks good")]
