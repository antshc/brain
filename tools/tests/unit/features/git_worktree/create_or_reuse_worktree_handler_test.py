"""Unit tests for the create_or_reuse_worktree handler.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from pathlib import Path

import pytest

from modules.git_worktree.domain.errors import MergeConflictError, WorktreeCreationError
from modules.git_worktree.features.create_or_reuse_worktree.handler import create_or_reuse_worktree
from modules.git_worktree.infrastructure.git_cli import WorktreeAddResult
from modules.git_worktree.infrastructure.tests.fake_git_cli import FakeGitCli


class TestCreateOrReuseWorktree:
    """Feature: Create Or Reuse Worktree"""

    def test_current_branch_already_matches_feature_branch_skips_creation(self, tmp_path: Path):
        # Scenario: Current branch already matches feature branch skips creation
        git = FakeGitCli(current_branch_output="feature-1")

        result = create_or_reuse_worktree(tmp_path, "main", "feature-1", git=git)

        assert result.worktree_path == str(tmp_path)
        assert result.branch == "feature-1"
        assert result.target_branch == "main"
        assert result.codebase_repo_path == str(tmp_path)
        assert git.worktree_add_calls == []
        assert git.pull_calls == [tmp_path]
        assert git.merge_calls == [(tmp_path, "origin/main")]

    def test_current_branch_matches_feature_branch_surfaces_merge_conflict(self, tmp_path: Path):
        # Scenario: Current branch matches feature branch surfaces merge conflict
        git = FakeGitCli(current_branch_output="feature-1", merge_success=False, conflicted_files_output=["x.py"])

        with pytest.raises(MergeConflictError) as excinfo:
            create_or_reuse_worktree(tmp_path, "main", "feature-1", git=git)

        assert excinfo.value.conflicting_files == ["x.py"]

    def test_fresh_feature_branch_creates_worktree_from_existing_origin_feature_branch(self, tmp_path: Path):
        # Scenario: Fresh feature branch creates worktree from existing origin feature branch
        git = FakeGitCli(
            current_branch_output="main",
            ref_exists_map={"origin/feature-1": True},
        )

        result = create_or_reuse_worktree(tmp_path, "main", "feature-1", git=git)

        expected_worktree_path = tmp_path.parent / f"{tmp_path.name}.worktrees" / "feature-1"
        assert result.worktree_path == str(expected_worktree_path)
        assert result.branch == "feature-1"
        assert result.target_branch == "main"
        assert git.worktree_add_calls == [(tmp_path, expected_worktree_path, "feature-1", "origin/feature-1")]

    def test_fresh_feature_branch_falls_back_to_target_branch_when_no_origin_feature_branch(self, tmp_path: Path):
        # Scenario: Fresh feature branch falls back to target branch when no origin feature branch
        git = FakeGitCli(
            current_branch_output="main",
            ref_exists_map={"origin/feature-1": False},
        )

        result = create_or_reuse_worktree(tmp_path, "main", "feature-1", git=git)

        expected_worktree_path = tmp_path.parent / f"{tmp_path.name}.worktrees" / "feature-1"
        assert git.worktree_add_calls == [(tmp_path, expected_worktree_path, "feature-1", "origin/main")]
        assert result.worktree_path == str(expected_worktree_path)

    def test_existing_worktree_is_reused_and_branch_is_actualized(self, tmp_path: Path):
        # Scenario: Existing worktree is reused and branch is actualized
        git = FakeGitCli(
            current_branch_output="main",
            worktree_add_result=WorktreeAddResult(success=False, already_exists=True, stderr="already exists"),
        )

        result = create_or_reuse_worktree(tmp_path, "main", "feature-1", git=git)

        expected_worktree_path = tmp_path.parent / f"{tmp_path.name}.worktrees" / "feature-1"
        assert result.worktree_path == str(expected_worktree_path)
        assert git.pull_calls == [expected_worktree_path]
        assert git.merge_calls == [(expected_worktree_path, "origin/main")]

    def test_existing_worktree_reuse_surfaces_merge_conflict(self, tmp_path: Path):
        # Scenario: Existing worktree reuse surfaces merge conflict
        git = FakeGitCli(
            current_branch_output="main",
            worktree_add_result=WorktreeAddResult(success=False, already_exists=True, stderr="already exists"),
            merge_success=False,
            conflicted_files_output=["y.py"],
        )

        with pytest.raises(MergeConflictError) as excinfo:
            create_or_reuse_worktree(tmp_path, "main", "feature-1", git=git)

        assert excinfo.value.conflicting_files == ["y.py"]

    def test_worktree_creation_failure_for_other_reason_raises_error(self, tmp_path: Path):
        # Scenario: Worktree creation failure for other reason raises error
        git = FakeGitCli(
            current_branch_output="main",
            worktree_add_result=WorktreeAddResult(success=False, already_exists=False, stderr="permission denied"),
        )

        with pytest.raises(WorktreeCreationError) as excinfo:
            create_or_reuse_worktree(tmp_path, "main", "feature-1", git=git)

        assert "permission denied" in excinfo.value.message
