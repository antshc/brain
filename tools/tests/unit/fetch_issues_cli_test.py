#!/usr/bin/env python3
"""Unit tests for the fetch_issues CLI entry point.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

import json

import modules.github.fetch_issues as fetch_issues_cli


class TestFetchIssuesCli:
    """Feature: Fetch Issues CLI"""

    def test_cli_prints_json_array_for_valid_repository(self, monkeypatch, capsys):
        # Scenario: CLI prints JSON array for valid repository
        monkeypatch.setattr(
            fetch_issues_cli,
            "fetch_issues",
            lambda repository, milestone_title=None: [{"number": 14, "title": "Issue 14", "body": "", "url": "u", "labels": [], "comments": []}],
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
        assert captured.err == "Usage: fetch_issues.py <owner>/<repo> [--milestone <title>]\n"

    def test_invalid_repository_format_prints_error_and_returns_one(self, capsys):
        # Scenario: Invalid repository format prints error and returns one
        exit_code = fetch_issues_cli.main(["owner-repo"])
        captured = capsys.readouterr()

        assert exit_code == 1
        assert captured.out == ""
        assert captured.err == "Error: Invalid repository. Expected <owner>/<repo>, got: owner-repo\n"

    def test_no_actionable_issues_prints_empty_json_array(self, monkeypatch, capsys):
        # Scenario: No actionable issues prints empty JSON array
        monkeypatch.setattr(fetch_issues_cli, "fetch_issues", lambda repository, milestone_title=None: [])

        exit_code = fetch_issues_cli.main(["owner/repo"])
        captured = capsys.readouterr()

        assert exit_code == 0
        assert json.loads(captured.out) == []
        assert captured.err == ""

    def test_cli_passes_milestone_title_when_provided(self, monkeypatch, capsys):
        # Scenario: CLI passes milestone title when provided
        captured_args = {}

        def fake_fetch_issues(repository, milestone_title=None):
            captured_args["repository"] = repository
            captured_args["milestone_title"] = milestone_title
            return []

        monkeypatch.setattr(fetch_issues_cli, "fetch_issues", fake_fetch_issues)

        exit_code = fetch_issues_cli.main(["owner/repo", "--milestone", "Sprint 1"])
        captured = capsys.readouterr()

        assert exit_code == 0
        assert json.loads(captured.out) == []
        assert captured.err == ""
        assert captured_args == {"repository": "owner/repo", "milestone_title": "Sprint 1"}
