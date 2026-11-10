from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "plugins/wf/skills/git/scripts/git.py"


def git(path: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(path), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    path = tmp_path / "source repo"
    path.mkdir()
    git(path, "init", "-q")
    git(path, "config", "user.email", "test@example.invalid")
    git(path, "config", "user.name", "Test")
    (path / ".gitignore").write_text("ignored.txt\n")
    git(path, "add", ".gitignore")
    git(path, "commit", "-qm", "base")
    return path


def run(source: Path, action: str, *args: str, harness: Path | None = None) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), 'worktree', action, "--harness", str(harness or source),
         "--source", str(source), *args], capture_output=True, text=True,
    )
    payload = json.loads(result.stdout)
    assert result.returncode == (1 if payload["status"] == "blocked" else 0), result.stderr
    return payload


def create(
    source: Path, *, name: str = "task-1", branch: str | None = None, harness: Path | None = None
) -> dict:
    mode = ("--new-branch", branch) if branch else ("--detach",)
    return run(source, "create", "--repo-name", "code", "--name", name,
               "--commit", git(source, "rev-parse", "HEAD"), "--owner", "run-1", *mode,
               harness=harness)


def remove(source: Path, tmp_path: Path, record: dict, *, head: str | None = None) -> dict:
    record_file = tmp_path / "record.json"
    record_file.write_text(json.dumps(record))
    return run(source, "remove", "--record", str(record_file), "--expect-head",
               head or record["head"], "--recoverable")


@pytest.mark.parametrize("branch", [None, "feat/task-1"])
def test_create_and_remove_from_pinned_commit(repository: Path, tmp_path: Path, branch: str | None):
    result = create(repository, branch=branch)
    assert result["status"] == "created", result
    record = result["record"]
    path = Path(record["path"])
    assert path == repository / ".worktrees/code/task-1"
    assert git(path, "rev-parse", "HEAD") == record["head"]
    assert git(path, "branch", "--show-current") == (branch or "")
    assert len(result["changedExcludeFiles"]) == 1
    assert remove(repository, tmp_path, record)["status"] == "removed"
    assert not path.exists()
    assert remove(repository, tmp_path, record)["status"] == "absent"
    if branch:
        assert git(repository, "rev-parse", branch) == record["head"]


@pytest.mark.parametrize("filename", ["ignored.txt", "untracked.txt", ".gitignore"])
def test_remove_preserves_dirty_worktree(repository: Path, tmp_path: Path, filename: str):
    record = create(repository)["record"]
    file = Path(record["path"]) / filename
    file.write_text("preserve me")
    result = remove(repository, tmp_path, record)
    assert result["status"] == "blocked", result
    assert file.read_text() == "preserve me"


def test_remove_rejects_replacement_at_same_path(repository: Path, tmp_path: Path):
    first = create(repository)["record"]
    assert remove(repository, tmp_path, first)["status"] == "removed"
    second = create(repository)["record"]
    assert second["token"] != first["token"]
    assert remove(repository, tmp_path, first)["status"] == "blocked"
    assert Path(second["path"]).exists()


def test_remove_rejects_locked_checkout_and_changed_head(repository: Path, tmp_path: Path):
    record = create(repository, branch="feat/task-1")["record"]
    path = Path(record["path"])
    git(repository, "worktree", "lock", str(path))
    assert remove(repository, tmp_path, record)["status"] == "blocked"
    git(repository, "worktree", "unlock", str(path))
    git(path, "commit", "--allow-empty", "-qm", "new head")
    assert remove(repository, tmp_path, record)["status"] == "blocked"
    assert remove(repository, tmp_path, record, head=git(path, "rev-parse", "HEAD"))["status"] == "removed"


def test_create_rejects_occupied_path_and_traversal(repository: Path):
    occupied = repository / ".worktrees/code/task-1"
    occupied.mkdir(parents=True)
    (occupied / "keep").touch()
    assert create(repository, branch="feat/task-1")["status"] == "blocked"
    assert create(repository, name="../elsewhere")["status"] == "blocked"
    assert git(repository, "branch", "--list", "feat/task-1") == ""
    assert (occupied / "keep").exists()


def test_create_rejects_symlinked_worktree_root(repository: Path, tmp_path: Path):
    external = tmp_path / "elsewhere"
    external.mkdir()
    try:
        (repository / ".worktrees").symlink_to(external, target_is_directory=True)
    except OSError as exception:
        pytest.skip(f"Directory symlink unavailable: {exception}")
    assert create(repository)["status"] == "blocked"
    assert not list(external.iterdir())


def test_split_harness_creates_exclusion_in_harness_only(repository: Path, tmp_path: Path):
    harness = tmp_path / "harness"
    harness.mkdir()
    git(harness, "init", "-q")
    result = create(repository, harness=harness)
    assert result["status"] == "created", result
    assert Path(result["record"]["path"]).is_relative_to(harness)
    assert result["changedExcludeFiles"] == [str(harness / ".git/info/exclude")]
    assert "/.worktrees/" not in (repository / ".git/info/exclude").read_text()


@pytest.mark.parametrize("flag", ["--assume-unchanged", "--skip-worktree"])
def test_remove_preserves_files_with_hidden_index_changes(repository: Path, tmp_path: Path, flag: str):
    record = create(repository)["record"]
    path = Path(record["path"])
    git(path, "update-index", flag, ".gitignore")
    file = path / ".gitignore"
    file.write_text("hidden change")
    assert remove(repository, tmp_path, record)["status"] == "blocked"
    assert file.read_text() == "hidden change"


def test_create_rejects_shared_namespace_for_another_repository(repository: Path, tmp_path: Path):
    other = tmp_path / "another repo"
    git(repository, "clone", "-q", str(repository), str(other))
    assert create(repository)["status"] == "created"
    result = create(other, harness=repository, name="task-2")
    assert result["status"] == "blocked"
    assert "another repository" in result["reason"]
