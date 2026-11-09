from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import git


@pytest.fixture
def head(repo: Path) -> str:
    return git(repo, "rev-parse", "HEAD")


def create(run, repo, head, name="slice", branch="feat/slice", repo_name="work", **overrides):
    mode = ["--new-branch", branch] if branch else ["--detach"]
    values = {"--harness": repo, "--source": repo, "--repo-name": repo_name, "--name": name, "--commit": head,
              "--owner": "run-1", **overrides}
    return run("worktree", "create", *[f"{key}={value}" for key, value in values.items()], *mode)


def record_file(tmp_path: Path, result) -> Path:
    path = tmp_path / "record.json"
    path.write_text(json.dumps(result.data["record"]))
    return path


def test_create_makes_a_clean_owned_worktree_on_a_new_branch(run, repo, head):
    result = create(run, repo, head)
    path = repo / ".worktrees/work/slice"
    assert result.code == 0 and result.data["status"] == "created" and result.data["path"] == str(path.resolve())
    assert git(path, "rev-parse", "--abbrev-ref", "HEAD") == "feat/slice"
    assert git(path, "status", "--porcelain") == ""
    assert result.data["record"]["owner"] == "run-1" and len(result.data["record"]["token"]) == 32
    assert "/.worktrees/" in (repo / ".git/info/exclude").read_text()
    assert result.data["changedExcludeFiles"]


def test_create_detached_leaves_no_branch(run, repo, head):
    result = create(run, repo, head, branch=None)
    assert result.code == 0 and result.data["record"]["branch"] is None
    assert git(repo / ".worktrees/work/slice", "rev-parse", "--abbrev-ref", "HEAD") == "HEAD"


def test_create_does_not_rewrite_an_existing_ignore_rule(run, repo, head):
    (repo / ".git/info/exclude").write_text("/.worktrees/\n")
    assert create(run, repo, head).data["changedExcludeFiles"] == []


def test_create_refuses_an_occupied_path_or_existing_branch(run, repo, head):
    create(run, repo, head)
    occupied = create(run, repo, head, branch="feat/other")
    assert occupied.code == 1 and "occupied" in occupied.err
    git(repo, "branch", "feat/taken")
    taken = create(run, repo, head, name="second", branch="feat/taken")
    assert taken.code == 1 and "already exists" in taken.err


@pytest.mark.parametrize("overrides", [
    {"repo_name": "../x"}, {"repo_name": "-x"}, {"name": "x."}, {"name": "a b"}, {"name": "a/b"}, {"name": ""},
])
def test_create_refuses_unsafe_path_segments(run, repo, head, overrides):
    result = create(run, repo, head, **overrides)
    assert result.code == 1 and result.data["status"] == "blocked"
    assert not (repo / ".worktrees").exists() or not any((repo / ".worktrees").rglob("*.git"))


@pytest.mark.parametrize("commit", ["HEAD", "abc123", "f" * 40, "A" * 40])
def test_create_demands_a_full_existing_local_commit(run, repo, commit):
    assert create(run, repo, commit).code == 1


def test_create_demands_an_owner_and_an_absolute_checkout(run, repo, head):
    assert create(run, repo, head, **{"--owner": "  "}).code == 1
    assert create(run, repo, head, **{"--harness": "relative"}).code == 1


def test_create_refuses_a_harness_that_tracks_worktree_files(run, repo, head):
    (repo / ".worktrees").mkdir()
    (repo / ".worktrees/tracked").write_text("x")
    git(repo, "add", "-f", ".worktrees/tracked")
    assert "tracks files" in create(run, repo, head).err


def test_inspect_reports_absent_clean_and_dirty(run, repo, head):
    args = ("worktree", "inspect", "--harness", repo, "--source", repo, "--repo-name", "work", "--name", "slice")
    assert run(*args).data["status"] == "absent"
    create(run, repo, head)
    present = run(*args).data
    assert present["status"] == "present" and present["clean"] is True and present["branch"] == "feat/slice"
    (repo / ".worktrees/work/slice/new.txt").write_text("x")
    dirty = run(*args).data
    assert dirty["clean"] is False and "modified, untracked" in dirty["reason"]


def test_inspect_needs_a_record_or_the_managed_names(run, repo):
    result = run("worktree", "inspect", "--harness", repo, "--source", repo)
    assert result.code == 1 and "ownership record" in result.err


def test_reuse_verifies_ownership_and_expected_head(run, repo, head, tmp_path):
    record = record_file(tmp_path, create(run, repo, head))
    args = ["worktree", "reuse", "--harness", repo, "--source", repo, "--record", record]
    assert run(*args).code == 1  # no expected head
    reused = run(*args, "--expect-head", head)
    assert reused.data["status"] == "reused" and reused.data["record"]["owner"] == "run-1"
    assert run("worktree", "reconcile", "--harness", repo, "--source", repo, "--record", record,
               "--expect-head", head).data["status"] == "verified"
    assert run(*args, "--expect-head", "f" * 40).code == 1


def test_reuse_rejects_a_forged_ownership_record(run, repo, head, tmp_path):
    result = create(run, repo, head)
    forged = dict(result.data["record"], token="0" * 32)
    path = tmp_path / "forged.json"
    path.write_text(json.dumps(forged))
    blocked = run("worktree", "reuse", "--harness", repo, "--source", repo, "--record", path, "--expect-head", head)
    assert blocked.code == 1 and "ownership could not be verified" in blocked.err


def test_reuse_of_a_missing_worktree_is_blocked(run, repo, head, tmp_path):
    result = create(run, repo, head)
    record = record_file(tmp_path, result)
    git(repo, "worktree", "remove", "--force", result.data["path"])
    assert run("worktree", "reuse", "--harness", repo, "--source", repo, "--record", record,
               "--expect-head", head).code == 1


def remove(run, repo, record, head, *extra):
    return run("worktree", "remove", "--harness", repo, "--source", repo, "--record", record, "--expect-head", head, *extra)


def test_remove_requires_recoverability_ownership_and_a_clean_tree(run, repo, head, tmp_path, monkeypatch):
    created = create(run, repo, head)
    record = record_file(tmp_path, created)
    monkeypatch.chdir(tmp_path)
    assert "recoverability" in remove(run, repo, record, head).err
    (repo / ".worktrees/work/slice/x.txt").write_text("unsaved")
    assert remove(run, repo, record, head, "--recoverable").code == 1
    assert (repo / ".worktrees/work/slice/x.txt").exists()
    (repo / ".worktrees/work/slice/x.txt").unlink()
    done = remove(run, repo, record, head, "--recoverable")
    assert done.data["status"] == "removed" and not (repo / ".worktrees/work/slice").exists()
    assert remove(run, repo, record, head, "--recoverable").data["status"] == "absent"
    assert "feat/slice" in git(repo, "branch", "--list")


def test_remove_refuses_a_moved_head_and_a_foreign_record(run, repo, head, tmp_path, monkeypatch):
    record = record_file(tmp_path, create(run, repo, head))
    monkeypatch.chdir(tmp_path)
    assert remove(run, repo, record, "f" * 40, "--recoverable").code == 1
    foreign = json.loads(record.read_text())
    foreign["commonDir"] = str(tmp_path / "elsewhere/.git")
    record.write_text(json.dumps(foreign))
    assert "another repository" in remove(run, repo, record, head, "--recoverable").err
    assert (repo / ".worktrees/work/slice").exists()


def test_remove_refuses_to_run_from_inside_the_target(run, repo, head, tmp_path, monkeypatch):
    record = record_file(tmp_path, create(run, repo, head))
    monkeypatch.chdir(repo / ".worktrees/work/slice")
    assert "outside the target" in remove(run, repo, record, head, "--recoverable").err


def test_remove_rejects_malformed_records(run, repo, head, tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"owner": "x"}))
    assert "Invalid worktree ownership record" in remove(run, repo, path, head, "--recoverable").err
