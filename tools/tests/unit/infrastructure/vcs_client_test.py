#!/usr/bin/env python3
"""Unit tests for VCSClient._thread_from_raw().

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
