#!/usr/bin/env python3
"""Integration tests for the fetch_issues handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.github.infrastructure.tests.fake_gh_cli import FakeGhCli
from modules.github.infrastructure.vcs_client import VCSClient
from modules.github.features.fetch_issues.handler import fetch_issues


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_raw_issue(
    number: int,
    title: str,
    labels: list[str],
    body: str = "",
    comments: list[dict] | None = None,
) -> dict:
    return {
        "number": number,
        "title": title,
        "body": body,
        "url": f"https://github.com/owner/repo/issues/{number}",
        "labels": labels,
        "comments": comments or [],
    }


def setup_handler(issues_raw: list[dict]):
    """Return vcs wired for a test with FakeGhCli."""
    fake_gh = FakeGhCli(issues_raw=issues_raw)
    return VCSClient(gh=fake_gh)


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestFetchIssues:
    """Feature: Fetch Issues"""

    def test_handler_returns_correctly_shaped_output_for_actionable_issues(self):
        # Scenario: Handler returns correctly shaped output for actionable issues
        issues_raw = [
            make_raw_issue(1, "Fix the bug", ["ready"]),
            make_raw_issue(2, "Write the PRD", ["prd"]),
        ]
        vcs = setup_handler(issues_raw)

        result = fetch_issues("owner", "repo", vcs=vcs)

        assert len(result) == 2
        i1 = result[0]
        assert i1["number"] == 1
        assert i1["title"] == "Fix the bug"
        assert i1["url"] == "https://github.com/owner/repo/issues/1"
        assert i1["labels"] == ["ready"]
        assert "comments" in i1
        assert "body" in i1

    def test_handler_returns_empty_list_when_no_actionable_issues_exist(self):
        # Scenario: Handler returns empty list when no actionable issues exist
        issues_raw = [
            make_raw_issue(1, "Investigate", ["bug"]),
            make_raw_issue(2, "Blocked work", ["ready", "blocked"]),
        ]
        vcs = setup_handler(issues_raw)

        result = fetch_issues("owner", "repo", vcs=vcs)

        assert result == []

    def test_non_actionable_issues_are_excluded(self):
        # Scenario: Non-actionable issues are excluded
        issues_raw = [
            make_raw_issue(1, "Actionable", ["ready"]),
            make_raw_issue(2, "Not actionable", ["bug"]),
            make_raw_issue(3, "Also actionable", ["prd"]),
            make_raw_issue(4, "Blocked", ["ready", "hitl"]),
        ]
        vcs = setup_handler(issues_raw)

        result = fetch_issues("owner", "repo", vcs=vcs)

        assert len(result) == 2
        assert result[0]["number"] == 1
        assert result[1]["number"] == 3

    def test_no_issues_found_returns_empty_list(self):
        # Scenario: No issues found — empty JSON array; exit code 0
        vcs = setup_handler([])

        result = fetch_issues("owner", "repo", vcs=vcs)

        assert result == []

    def test_comments_are_included_in_output_shape(self):
        # Scenario: Comments are included in the output with correct fields
        issues_raw = [
            make_raw_issue(
                1, "Issue with comment", ["ready"],
                comments=[{"id": "C1", "body": "A comment", "updatedAt": "2024-01-01T00:00:00Z"}],
            ),
        ]
        vcs = setup_handler(issues_raw)

        result = fetch_issues("owner", "repo", vcs=vcs)

        assert len(result) == 1
        comments = result[0]["comments"]
        assert len(comments) == 1
        assert comments[0]["id"] == "C1"
        assert comments[0]["body"] == "A comment"
        assert comments[0]["created_at"] == "2024-01-01T00:00:00Z"
