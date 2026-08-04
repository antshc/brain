"""Unit tests for the actualize_branch handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from pathlib import Path

import pytest

from modules.git_worktree.domain.errors import GitCommandFailedError, MergeConflictError
from modules.git_worktree.features.actualize_branch.handler import actualize_branch
from modules.git_worktree.infrastructure.tests.fake_git_cli import FakeGitCli


class TestActualizeBranch:
    """Feature: Actualize Branch"""

    def test_fetches_pulls_and_merges_the_target_branch_on_success(self):
        # Scenario: Fetches, pulls, and merges the target branch on success
        git = FakeGitCli(pull_success=True, merge_success=True)
        cwd = Path("/repo")

        actualize_branch(cwd, "main", git=git)

        assert git.fetch_calls == [cwd]
        assert git.pull_calls == [cwd]
        assert git.merge_calls == [(cwd, "origin/main")]

    def test_pull_conflict_surfaces_conflicting_files(self):
        # Scenario: Pull conflict surfaces conflicting files
        git = FakeGitCli(pull_success=False, conflicted_files_output=["a.py", "b.py"])

        with pytest.raises(MergeConflictError) as excinfo:
            actualize_branch(Path("/repo"), "main", git=git)

        assert excinfo.value.conflicting_files == ["a.py", "b.py"]
        assert git.merge_calls == []

    def test_merge_conflict_surfaces_conflicting_files(self):
        # Scenario: Merge conflict surfaces conflicting files
        git = FakeGitCli(pull_success=True, merge_success=False, conflicted_files_output=["c.py"])

        with pytest.raises(MergeConflictError) as excinfo:
            actualize_branch(Path("/repo"), "main", git=git)

        assert excinfo.value.conflicting_files == ["c.py"]

    def test_pull_failure_without_conflicted_files_raises_git_command_failed_error(self):
        # Scenario: Pull failure without conflicted files raises git command failed error
        git = FakeGitCli(
            pull_success=False,
            pull_stderr="There is no tracking information for the current branch.",
            conflicted_files_output=[],
        )

        with pytest.raises(GitCommandFailedError) as excinfo:
            actualize_branch(Path("/repo"), "main", git=git)

        assert excinfo.value.command == "pull"
        assert excinfo.value.stderr == "There is no tracking information for the current branch."
        assert git.merge_calls == []

    def test_merge_failure_without_conflicted_files_raises_git_command_failed_error(self):
        # Scenario: Merge failure without conflicted files raises git command failed error
        git = FakeGitCli(pull_success=True, merge_success=False, merge_stderr="fatal: not something we can merge")

        with pytest.raises(GitCommandFailedError) as excinfo:
            actualize_branch(Path("/repo"), "main", git=git)

        assert excinfo.value.command == "merge"
        assert excinfo.value.stderr == "fatal: not something we can merge"
