#!/usr/bin/env python3
"""Unit tests for the fetch_issues CLI entry point.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from __future__ import annotations

import json

import modules.github.fetch_issues as fetch_issues_cli


class TestFetchIssuesCli:
    """Feature: Fetch Issues CLI"""

    def test_cli_prints_json_array_for_valid_repository(self, monkeypatch, capsys):
        # Scenario: CLI prints JSON array for valid repository
        monkeypatch.setattr(
            fetch_issues_cli,
            "fetch_issues",
            lambda owner, repo, milestone_title=None, kind="all": [{"number": 14, "title": "Issue 14", "body": "", "url": "u", "labels": [], "comments": []}],
        )

        exit_code = fetch_issues_cli.main(["owner/repo"])
        captured = capsys.readouterr()

        assert exit_code == 0
        assert json.loads(captured.out) == [
            {"number": 14, "title": "Issue 14", "body": "", "url": "u", "labels": [], "comments": []}
        ]
        assert captured.err == ""

    def test_missing_argument_prints_usage_error_and_returns_one(self, capsys):
        # Scenario: Missing argument prints usage error and returns one
        exit_code = fetch_issues_cli.main([])
        captured = capsys.readouterr()

        assert exit_code == 1
        assert captured.out == ""
        assert captured.err == "Usage: fetch_issues.py <owner>/<repo> [--milestone <title>] [--kind all|implementation|tests]\n"

    def test_invalid_repository_format_prints_error_and_returns_one(self, capsys):
        # Scenario: Invalid repository format prints error and returns one
        exit_code = fetch_issues_cli.main(["owner-repo"])
        captured = capsys.readouterr()

        assert exit_code == 1
        assert captured.out == ""
        assert captured.err == "Error: Invalid repository. Expected <owner>/<repo>, got: owner-repo\n"

    def test_no_actionable_issues_prints_empty_json_array(self, monkeypatch, capsys):
        # Scenario: No actionable issues prints empty JSON array
        monkeypatch.setattr(fetch_issues_cli, "fetch_issues", lambda owner, repo, milestone_title=None, kind="all": [])

        exit_code = fetch_issues_cli.main(["owner/repo"])
        captured = capsys.readouterr()

        assert exit_code == 0
        assert json.loads(captured.out) == []
        assert captured.err == ""

    def test_cli_passes_milestone_title_when_provided(self, monkeypatch, capsys):
        # Scenario: CLI passes milestone title when provided
        captured_args = {}

        def fake_fetch_issues(owner, repo, milestone_title=None, kind="all"):
            captured_args["owner"] = owner
            captured_args["repo"] = repo
            captured_args["milestone_title"] = milestone_title
            return []

        monkeypatch.setattr(fetch_issues_cli, "fetch_issues", fake_fetch_issues)

        exit_code = fetch_issues_cli.main(["owner/repo", "--milestone", "Sprint 1"])
        captured = capsys.readouterr()

        assert exit_code == 0
        assert json.loads(captured.out) == []
        assert captured.err == ""
        assert captured_args == {"owner": "owner", "repo": "repo", "milestone_title": "Sprint 1"}

    def test_cli_passes_kind_and_milestone_in_either_order(self, monkeypatch, capsys):
        # Scenario: CLI passes kind and milestone in either order
        calls = []
        def fake_fetch(owner, repo, **kwargs):
            calls.append((owner, repo, kwargs))
            return []
        monkeypatch.setattr(fetch_issues_cli, "fetch_issues", fake_fetch)
        for options in (["--kind", "tests", "--milestone", "Sprint 1"],
                        ["--milestone", "Sprint 1", "--kind", "implementation"]):
            assert fetch_issues_cli.main(["owner/repo", *options]) == 0
        assert [call[2] for call in calls] == [
            {"milestone_title": "Sprint 1", "kind": "tests"},
            {"milestone_title": "Sprint 1", "kind": "implementation"},
        ]

    def test_cli_rejects_invalid_kind_without_fetching(self, monkeypatch, capsys):
        # Scenario: CLI rejects invalid kind without fetching
        def unexpected_fetch(*args, **kwargs):
            raise AssertionError("Invalid arguments must not fetch tickets")
        monkeypatch.setattr(fetch_issues_cli, "fetch_issues", unexpected_fetch)
        for options in (["--kind", "typo"], ["--kind"], ["--unknown", "tests"]):
            assert fetch_issues_cli.main(["owner/repo", *options]) == 1
        assert capsys.readouterr().out == ""
