#!/usr/bin/env python3
"""Integration tests for the fetch_issues handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from unittest.mock import MagicMock

from modules.github.features.fetch_issues.handler import fetch_issues
from modules.github.infrastructure.gh_cli import GhCli
from modules.github.infrastructure.vcs_client import VCSClient

_REPOSITORY = "owner/repo"


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_raw_issue(
    number: int,
    labels: list[str],
    *,
    title: str | None = None,
    comments: list[dict] | None = None,
) -> dict:
    return {
        "number": number,
        "title": title or f"Issue {number}",
        "body": f"Body for issue {number}",
        "url": f"https://github.com/owner/repo/issues/{number}",
        "labels": labels,
        "comments": comments or [
            {
                "id": f"IC_{number}",
                "body": f"Comment for issue {number}",
                "createdAt": "2026-05-24T10:00:00Z",
            }
        ],
    }



def setup_handler(issues_raw: list[dict]):
    """Return (repository, vcs, gh) wired for a test with a mock GhCli."""
    mock_gh = MagicMock(spec=GhCli)
    mock_gh.fetch_issues_raw.return_value = issues_raw
    return _REPOSITORY, VCSClient(gh=mock_gh), mock_gh


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestFetchIssues:
    """Feature: Fetch Issues"""

    def test_returns_correctly_shaped_output_for_actionable_issues(self):
        # Scenario: Handler returns correctly shaped output for actionable issues
        issues_raw = [
            make_raw_issue(14, ["ready", "bug"]),
            make_raw_issue(
                15,
                ["prd"],
                comments=[
                    {
                        "id": "IC_15",
                        "body": "Need a follow-up",
                        "createdAt": "2026-05-24T11:00:00Z",
                    }
                ],
            ),
        ]
        repository, vcs, _ = setup_handler(issues_raw)

        result = fetch_issues(repository, vcs=vcs)

        assert len(result) == 2
        issue = result[0]
        assert issue["number"] == 14
        assert issue["title"] == "Issue 14"
        assert issue["body"] == "Body for issue 14"
        assert issue["url"] == "https://github.com/owner/repo/issues/14"
        assert issue["labels"] == ["ready", "bug"]
        assert issue["comments"] == [
            {
                "id": "IC_14",
                "body": "Comment for issue 14",
                "created_at": "2026-05-24T10:00:00Z",
            }
        ]

    def test_returns_empty_list_when_no_actionable_issues(self):
        # Scenario: Handler returns empty list when no actionable issues exist
        issues_raw = [
            make_raw_issue(20, ["bug"]),
            make_raw_issue(21, ["blocked"]),
        ]
        repository, vcs, _ = setup_handler(issues_raw)

        result = fetch_issues(repository, vcs=vcs)

        assert result == []

    def test_excludes_blocked_and_non_actionable_issues(self):
        # Scenario: Handler excludes blocked and non-actionable issues
        issues_raw = [
            make_raw_issue(30, ["ready"]),
            make_raw_issue(31, ["ready", "blocked"]),
            make_raw_issue(32, ["enhancement"]),
        ]
        repository, vcs, _ = setup_handler(issues_raw)

        result = fetch_issues(repository, vcs=vcs)

        assert len(result) == 1
        assert result[0]["number"] == 30

    def test_milestone_title_is_forwarded_to_gh_cli(self):
        # Scenario: Milestone title is forwarded to GhCli
        issues_raw = [make_raw_issue(40, ["ready"])]
        repository, vcs, gh = setup_handler(issues_raw)

        result = fetch_issues(repository, milestone_title="Sprint 1", vcs=vcs)

        gh.fetch_issues_raw.assert_called_once_with("owner", "repo", "Sprint 1")
        assert result == [
            {
                "number": 40,
                "title": "Issue 40",
                "body": "Body for issue 40",
                "url": "https://github.com/owner/repo/issues/40",
                "labels": ["ready"],
                "comments": [
                    {
                        "id": "IC_40",
                        "body": "Comment for issue 40",
                        "created_at": "2026-05-24T10:00:00Z",
                    }
                ],
            }
        ]
