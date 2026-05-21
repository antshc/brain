#!/usr/bin/env python3
"""Unit tests for VCSClient._thread_from_raw() and VCSClient._issue_from_raw().

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.github.infrastructure.vcs_client import VCSClient


class TestVCSClientThreadMapping:
    """Feature: VCS Client Thread Mapping"""

    def test_raw_thread_node_is_mapped_to_review_thread_domain_entity(self):
        # Scenario: Raw thread node is mapped to ReviewThread domain entity
        raw = {
            "id": "T1",
            "path": "src/foo.ts",
            "startLine": 10,
            "line": 15,
            "isResolved": False,
            "comments": [{"author": {"login": "reviewer"}, "body": "fix!: issue"}],
        }
        result = VCSClient()._thread_from_raw(raw)
        assert result.thread_id == "T1"
        assert result.path == "src/foo.ts"
        assert result.lines == "10-15"
        assert result.is_resolved is False
        assert result.comments[0].author == "reviewer"
        assert result.comments[0].body == "fix!: issue"

    def test_missing_start_line_falls_back_to_line_for_both_start_and_end(self):
        # Scenario: Missing startLine falls back to line for both start and end
        raw = {
            "id": "T2",
            "path": "a.py",
            "startLine": None,
            "line": 5,
            "isResolved": False,
            "comments": [],
        }
        result = VCSClient()._thread_from_raw(raw)
        assert result.lines == "5-5"


class TestVCSClientIssueMapping:
    """Feature: VCS Client Issue Mapping"""

    def test_raw_issue_node_is_mapped_to_issue_domain_entity(self):
        # Scenario: Raw issue node is mapped to Issue domain entity
        raw = {
            "number": 42,
            "title": "Fix the thing",
            "body": "Some description",
            "url": "https://github.com/owner/repo/issues/42",
            "labels": ["ready", "bug"],
            "comments": [
                {"id": "C1", "body": "First comment", "updatedAt": "2024-01-01T00:00:00Z"},
            ],
        }
        result = VCSClient()._issue_from_raw(raw)
        assert result.number == 42
        assert result.title == "Fix the thing"
        assert result.body == "Some description"
        assert result.url == "https://github.com/owner/repo/issues/42"
        assert result.labels == ["ready", "bug"]
        assert len(result.comments) == 1
        assert result.comments[0].id == "C1"
        assert result.comments[0].body == "First comment"
        assert result.comments[0].updated_at == "2024-01-01T00:00:00Z"

    def test_issue_with_no_comments_maps_to_empty_comments_list(self):
        # Scenario: Issue with no comments maps to empty comments list
        raw = {
            "number": 1,
            "title": "Empty",
            "body": "",
            "url": "https://github.com/owner/repo/issues/1",
            "labels": ["prd"],
            "comments": [],
        }
        result = VCSClient()._issue_from_raw(raw)
        assert result.comments == []

    def test_issue_labels_are_extracted_as_flat_list_of_strings(self):
        # Scenario: Issue labels are extracted as flat list of strings
        raw = {
            "number": 2,
            "title": "Labelled",
            "body": "",
            "url": "https://github.com/owner/repo/issues/2",
            "labels": ["ready", "prd", "feature"],
            "comments": [],
        }
        result = VCSClient()._issue_from_raw(raw)
        assert result.labels == ["ready", "prd", "feature"]

