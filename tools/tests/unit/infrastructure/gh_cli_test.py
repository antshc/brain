#!/usr/bin/env python3
"""Unit tests for GhCli milestone GraphQL queries.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

import json
from unittest.mock import Mock, patch

from modules.github.infrastructure.gh_cli import GhCli, _MILESTONES_QUERY


class TestGhCliMilestoneQueryConstruction:
    """Feature: GhCli Milestone Query Construction"""

    @patch("modules.github.infrastructure.gh_cli.subprocess.run")
    def test_open_milestones_query_is_built_and_nodes_are_returned(self, mock_run):
        # Scenario: Open milestones query is built and nodes are returned
        nodes = [
            {
                "id": "M1",
                "number": 1,
                "title": "Sprint 1",
                "description": "First delivery slice",
                "url": "https://github.com/owner/repo/milestone/1",
            }
        ]
        mock_run.return_value = Mock(
            stdout=json.dumps({"data": {"repository": {"milestones": {"nodes": nodes}}}})
        )

        result = GhCli().list_milestones_raw("owner", "repo")

        assert result == nodes
        mock_run.assert_called_once_with(
            [
                "gh", "api", "graphql",
                "-f", f"query={_MILESTONES_QUERY}",
                "-f", "owner=owner",
                "-f", "repo=repo",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
