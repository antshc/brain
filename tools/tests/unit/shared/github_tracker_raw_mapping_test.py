"""Unit tests for github_tracker's raw JSON mapping helpers.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

import pytest

from modules.github_tracker.shared.raw_mapping import (
    normalize_comments,
    normalize_labels,
    parse_issue_number,
    ticket_from_raw,
)


class TestIssueNumberParsing:
    """Feature: Issue Number Parsing"""

    def test_issue_create_url_yields_the_trailing_number(self):
        # Scenario: Issue create URL yields the trailing number
        assert parse_issue_number("https://github.com/owner/repo/issues/123\n") == 123

    def test_unparseable_url_raises_value_error(self):
        # Scenario: Unparseable URL raises ValueError
        with pytest.raises(ValueError):
            parse_issue_number("not-a-url")


class TestLabelAndCommentNormalization:
    """Feature: Label And Comment Normalization"""

    def test_label_objects_are_flattened_to_names(self):
        # Scenario: Label objects are flattened to names
        assert normalize_labels([{"name": "hitl"}, {"name": "spec"}]) == ["hitl", "spec"]

    def test_comment_objects_are_flattened_to_bodies(self):
        # Scenario: Comment objects are flattened to bodies
        assert normalize_comments([{"body": "first"}, {"body": "second"}]) == ["first", "second"]

    def test_ticket_from_raw_maps_all_documented_fields(self):
        # Scenario: ticket_from_raw maps all documented fields
        raw = {
            "number": 5,
            "title": "Title",
            "body": "Body",
            "labels": [{"name": "hitl"}],
            "comments": [{"body": "ack"}],
        }

        assert ticket_from_raw(raw) == {
            "number": 5, "title": "Title", "body": "Body", "labels": ["hitl"], "comments": ["ack"]
        }
