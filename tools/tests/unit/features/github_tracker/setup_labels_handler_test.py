"""Unit tests for the setup_labels handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from modules.github_tracker.features.setup_labels.handler import setup_labels
from modules.github_tracker.infrastructure.tests.fake_gh_cli import FakeGhCli


class TestSetupLabels:
    """Feature: Setup Labels"""

    def test_missing_label_is_created_with_catalog_name_color_and_description(self):
        # Scenario: Missing label is created with catalog name, color, and description
        gh = FakeGhCli(repo="owner/repo", label_names_output=[])

        results = setup_labels(gh=gh)

        assert {(r.name, r.created) for r in results} == {("hitl", True), ("spec", True)}
        assert ("owner/repo", "hitl", "fbca04", "Requires human implementation") in gh.label_create_calls
        assert ("owner/repo", "spec", "5319e7", "Spec task with implementation context") in gh.label_create_calls

    def test_existing_label_is_left_unchanged_and_reported_as_existing(self):
        # Scenario: Existing label is left unchanged and reported as existing
        gh = FakeGhCli(repo="owner/repo", label_names_output=["hitl", "spec"])

        results = setup_labels(gh=gh)

        assert {(r.name, r.created) for r in results} == {("hitl", False), ("spec", False)}
        assert gh.label_create_calls == []
