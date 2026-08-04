"""Subprocess-level CLI tests for the staged_diff script.

Spawns the script against a real temporary git repository, mirroring the
create_worktree script's own subprocess-level test.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from pathlib import Path
import subprocess
import sys


SCRIPT = Path(__file__).parent.parent.parent.parent / "src" / "modules" / "staged_diff" / "staged_diff.py"


def run_script(cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    (repo / "f.txt").write_text("hi\n")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
    return repo


class TestStagedDiffCli:
    """Feature: Staged Diff CLI"""

    def test_uncommitted_changes_prints_the_cached_diff(self, tmp_path: Path):
        # Scenario: Uncommitted changes prints the cached diff
        repo = make_repo(tmp_path)
        (repo / "f.txt").write_text("hi\nbye\n")

        result = run_script(repo)

        assert result.returncode == 0, result.stderr
        assert "diff --git a/f.txt b/f.txt" in result.stdout
        assert "+bye" in result.stdout
        staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], cwd=repo, check=True, capture_output=True, text=True
        )
        assert "f.txt" in staged.stdout

    def test_no_uncommitted_changes_prints_the_fallback_message(self, tmp_path: Path):
        # Scenario: No uncommitted changes prints the fallback message
        repo = make_repo(tmp_path)

        result = run_script(repo)

        assert result.returncode == 0, result.stderr
        assert result.stdout == "No uncommitted changes\n"
