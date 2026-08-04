"""Subprocess-level CLI tests for the create_worktree script.

Spawns the script against a real temporary git repository, mirroring the
harness-resolver script's own subprocess-level test.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from pathlib import Path
import subprocess
import sys


SCRIPT = Path(__file__).parent.parent.parent.parent / "src" / "modules" / "git_worktree" / "create_worktree.py"


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def make_repo_with_origin(tmp_path: Path) -> Path:
    """Create a bare-ish origin repo plus a clone with an `origin` remote, on branch main.

    Returns the path to the clone (the codebase-repo-path used by the script).
    """
    origin = tmp_path / "origin"
    origin.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=origin, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=origin, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=origin, check=True)
    (origin / "f.txt").write_text("hi\n")
    subprocess.run(["git", "add", "."], cwd=origin, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=origin, check=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=origin, check=True)

    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=clone, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=clone, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=clone, check=True)
    return clone


class TestCreateWorktreeCli:
    """Feature: Create Worktree CLI"""

    def test_fresh_feature_branch_creates_new_worktree(self, tmp_path: Path):
        # Scenario: Fresh feature branch creates new worktree
        clone = make_repo_with_origin(tmp_path)

        result = run_script(str(clone), "main", "feature-1")

        expected_worktree_path = clone.parent / f"{clone.name}.worktrees" / "feature-1"
        assert result.returncode == 0, result.stderr
        assert f"CODEBASE_REPO_PATH: {clone}" in result.stdout
        assert f"WORKTREE_PATH: {expected_worktree_path}" in result.stdout
        assert "BRANCH: feature-1" in result.stdout
        assert "TARGET_BRANCH: main" in result.stdout
        assert expected_worktree_path.is_dir()

    def test_existing_worktree_is_reused_instead_of_failing(self, tmp_path: Path):
        # Scenario: Existing worktree is reused instead of failing
        clone = make_repo_with_origin(tmp_path)
        first = run_script(str(clone), "main", "feature-1")
        assert first.returncode == 0, first.stderr

        second = run_script(str(clone), "main", "feature-1")

        expected_worktree_path = clone.parent / f"{clone.name}.worktrees" / "feature-1"
        assert second.returncode == 0, second.stderr
        assert f"WORKTREE_PATH: {expected_worktree_path}" in second.stdout

    def test_worktree_creation_failure_for_non_existing_reason_reports_error(self, tmp_path: Path):
        # Scenario: Worktree creation failure for non existing reason reports error
        clone = make_repo_with_origin(tmp_path)

        result = run_script(str(clone), "does-not-exist", "feature-1")

        assert result.returncode == 3
        assert "Error: worktree creation failed" in result.stderr
