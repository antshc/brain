from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from conftest import FakeGitHub, git

ZERO = "0" * 40


def bare(remote: Path, *args: str) -> str:
    return subprocess.check_output(["git", "--git-dir", str(remote), *args], text=True).strip()


def commit_file(repo: Path, name: str, text: str = "x", message: str = "add") -> str:
    (repo / name).write_text(text)
    git(repo, "add", name)
    git(repo, "commit", "-qm", message)
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture
def fake_repo(fake: FakeGitHub, repo: Path):
    fake.remote_url = "https://github.com/acme/work.git"
    return repo


@pytest.fixture
def remote(fake_repo: Path, tmp_path: Path) -> Path:
    bare = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    git(fake_repo, "remote", "add", "origin", str(bare))
    return bare


def test_checkout_must_be_absolute_and_the_repository_root(run, fake, repo):
    sub = repo / "sub"
    sub.mkdir()
    assert run("branch", "inspect", "--checkout", "relative", "--name", "x", gh=fake).code == 2
    result = run("branch", "inspect", "--checkout", sub, "--name", "x", gh=fake)
    assert result.code == 2 and "repository root" in result.err
    assert run("branch", "inspect", "--checkout", repo, "--name", "x", gh=fake).code == 0


@pytest.mark.parametrize("value", ["short", "A" * 40, "g" * 40, "a" * 39, "a" * 41, ""])
def test_commands_demand_a_full_lowercase_sha(run, fake, repo, value):
    result = run("branch", "create", "--checkout", repo, "--name", "x", "--start", value, gh=fake)
    assert result.code == 2 and "full commit SHA" in result.err


def test_branch_create_and_inspect_round_trip(run, fake, repo):
    base = git(repo, "rev-parse", "HEAD")
    assert run("branch", "inspect", "--checkout", repo, "--name", "feat/a", gh=fake).data == {
        "ref": "refs/heads/feat/a", "local": None}
    created = run("branch", "create", "--checkout", repo, "--name", "feat/a", "--start", base, gh=fake)
    assert created.data == {"ref": "refs/heads/feat/a", "head": base}
    assert run("branch", "inspect", "--checkout", repo, "--name", "feat/a", gh=fake).data["local"] == base


def test_branch_create_rejects_invalid_names_unknown_starts_and_duplicates(run, fake, repo):
    base = git(repo, "rev-parse", "HEAD")
    assert run("branch", "create", "--checkout", repo, "--name", "bad..name", "--start", base, gh=fake).code == 1
    assert run("branch", "create", "--checkout", repo, "--name", "x", "--start", "c" * 40, gh=fake).code == 1
    run("branch", "create", "--checkout", repo, "--name", "dup", "--start", base, gh=fake)
    assert run("branch", "create", "--checkout", repo, "--name", "dup", "--start", base, gh=fake).code == 1


def test_branch_name_cannot_inject_git_options(run, fake, repo):
    base = git(repo, "rev-parse", "HEAD")
    result = run("branch", "create", "--checkout", repo, "--name=--delete", "--start", base, gh=fake)
    assert result.code == 1
    assert git(repo, "for-each-ref", "--format=%(refname)") == "refs/heads/main"


def test_branch_inspect_with_remote_requires_repo_and_matching_origin(run, fake_repo, fake, remote):
    result = run("branch", "inspect", "--checkout", fake_repo, "--name", "main", "--remote", "origin", gh=fake)
    assert result.code == 2 and "--repo" in result.err
    fake.remote_url = "https://github.com/someone/fork.git"
    result = run("branch", "inspect", "--checkout", fake_repo, "--name", "main", "--remote", "origin",
                 "--repo", "acme/work", gh=fake)
    assert result.code == 2 and "does not uniquely identify" in result.err


@pytest.mark.parametrize("url", [
    "https://github.com/acme/work", "https://github.com/acme/work.git", "https://github.com/acme/work/",
    "ssh://git@github.com/acme/work.git", "git@github.com:acme/work.git", "https://github.com/ACME/Work.git",
])
def test_verify_remote_accepts_github_url_forms(run, fake_repo, fake, remote, url):
    fake.remote_url = url
    result = run("branch", "inspect", "--checkout", fake_repo, "--name", "main", "--remote", "origin",
                 "--repo", "acme/work", gh=fake)
    assert result.code == 0 and result.data["remote"] is None


@pytest.mark.parametrize("url", [
    "https://github.com/acme/work-fork.git", "https://github.com/xacme/work.git", "https://evil.com/github.com/acme/work",
    "https://github.com.evil.com/acme/work", "https://github.com/acme/work.git\nhttps://github.com/acme/other.git",
])
def test_verify_remote_rejects_lookalike_or_ambiguous_urls(run, fake_repo, fake, remote, url):
    fake.remote_url = url
    result = run("branch", "inspect", "--checkout", fake_repo, "--name", "main", "--remote", "origin",
                 "--repo", "acme/work", gh=fake)
    assert result.code == 2


def push(run, fake, repo, name, head, previous="absent", *extra):
    return run("branch", "push", "--checkout", repo, "--repo", "acme/work", "--remote", "origin", "--name", name,
               "--expected", head, "--previous", previous, *extra, gh=fake)


def test_branch_push_publishes_then_is_idempotent(run, fake, fake_repo, remote):
    head = commit_file(fake_repo, "a.txt")
    git(fake_repo, "branch", "feat/p")
    result = push(run, fake, fake_repo, "feat/p", head)
    assert result.data == {"ref": "refs/heads/feat/p", "head": head}
    assert bare(remote, "rev-parse", "refs/heads/feat/p") == head
    fake.calls.clear()
    assert push(run, fake, fake_repo, "feat/p", head).code == 0
    assert not any("push" in call for call in fake.calls)


def test_branch_push_sets_upstream_when_asked(run, fake, fake_repo, remote):
    head = commit_file(fake_repo, "a.txt")
    git(fake_repo, "branch", "feat/up")
    assert push(run, fake, fake_repo, "feat/up", head, "absent", "--set-upstream").code == 0
    assert git(fake_repo, "config", "branch.feat/up.remote") == "origin"


def test_branch_push_refuses_a_moved_local_or_remote_head(run, fake, fake_repo, remote):
    head = commit_file(fake_repo, "a.txt")
    git(fake_repo, "branch", "feat/m")
    stale = push(run, fake, fake_repo, "feat/m", "d" * 40)
    assert stale.code == 2 and "local head changed" in stale.err
    git(fake_repo, "push", "origin", f"{head}:refs/heads/feat/m")
    other = push(run, fake, fake_repo, "feat/m", head, "e" * 40)
    assert other.code == 0  # already at the expected head, nothing to move
    git(fake_repo, "branch", "-f", "feat/m", commit_file(fake_repo, "b.txt"))
    new_head = git(fake_repo, "rev-parse", "feat/m")
    moved = push(run, fake, fake_repo, "feat/m", new_head, "absent")
    assert moved.code == 2 and "remote head changed" in moved.err


def test_branch_push_fast_forwards_from_the_recorded_previous_head(run, fake, fake_repo, remote):
    first = commit_file(fake_repo, "a.txt")
    git(fake_repo, "branch", "feat/ff")
    push(run, fake, fake_repo, "feat/ff", first)
    second = commit_file(fake_repo, "b.txt")
    git(fake_repo, "branch", "-f", "feat/ff", second)
    assert push(run, fake, fake_repo, "feat/ff", second, first).code == 0
    assert bare(remote, "rev-parse", "refs/heads/feat/ff") == second


def test_branch_push_rejects_a_previous_that_is_not_an_ancestor(run, fake, fake_repo, remote):
    first = commit_file(fake_repo, "a.txt")
    git(fake_repo, "branch", "feat/na", first)
    push(run, fake, fake_repo, "feat/na", first)
    git(fake_repo, "reset", "-q", "--hard", "HEAD~1")
    divergent = commit_file(fake_repo, "c.txt", "other")
    git(fake_repo, "branch", "-f", "feat/na", divergent)
    assert push(run, fake, fake_repo, "feat/na", divergent, first).code == 1
    assert bare(remote, "rev-parse", "refs/heads/feat/na") == first


def test_branch_fetch_brings_the_exact_commit(run, fake, fake_repo, remote, tmp_path):
    head = commit_file(fake_repo, "a.txt")
    git(fake_repo, "push", "origin", f"{head}:refs/heads/main")
    clone = tmp_path / "other"
    subprocess.run(["git", "clone", "-q", str(remote), str(clone)], check=True)
    fake.remote_url = "https://github.com/acme/work.git"
    git(clone, "remote", "set-url", "origin", str(remote))
    result = run("branch", "fetch", "--checkout", clone, "--repo", "acme/work", "--remote", "origin",
                 "--expected", head, gh=fake)
    assert result.data == {"head": head}
    assert run("branch", "fetch", "--checkout", clone, "--repo", "acme/work", "--remote", "origin",
               "--expected", "f" * 40, gh=fake).code == 1


def test_branch_delete_requires_the_head_to_be_integrated(run, fake, repo):
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "switch", "-qc", "feat/d")
    head = commit_file(repo, "a.txt")
    git(repo, "switch", "-q", "main")
    stale = run("branch", "delete", "--checkout", repo, "--name", "feat/d", "--expected", base,
                "--integrated-into", base, gh=fake)
    assert stale.code == 2 and "local head changed" in stale.err
    unintegrated = run("branch", "delete", "--checkout", repo, "--name", "feat/d", "--expected", head,
                       "--integrated-into", base, gh=fake)
    assert unintegrated.code == 1
    assert "feat/d" in git(repo, "branch", "--list")
    git(repo, "merge", "-q", "--ff-only", "feat/d")
    done = run("branch", "delete", "--checkout", repo, "--name", "feat/d", "--expected", head,
               "--integrated-into", head, gh=fake)
    assert done.data == {"ref": "refs/heads/feat/d", "deleted": True}
    assert "feat/d" not in git(repo, "branch", "--list")


def test_commit_create_commits_only_the_named_paths(run, fake, repo, tmp_path):
    base = git(repo, "rev-parse", "HEAD")
    (repo / "keep.txt").write_text("keep")
    (repo / "other.txt").write_text("other")
    message = tmp_path / "msg"
    message.write_text("ccode(X acme/work#1): subject\n\nBody line\n")
    result = run("commit", "create", "--checkout", repo, "--expected", base, "--message-file", message, "keep.txt", gh=fake)
    assert result.data["previous"] == base
    assert git(repo, "show", "--format=", "--name-only", result.data["head"]) == "keep.txt"
    assert git(repo, "status", "--porcelain") == "?? other.txt"


@pytest.mark.parametrize("path", ["/abs/file", "../escape", "a/../../escape", "."])
def test_commit_create_rejects_non_exact_paths(run, fake, repo, tmp_path, path):
    base = git(repo, "rev-parse", "HEAD")
    message = tmp_path / "msg"
    message.write_text("m")
    result = run("commit", "create", "--checkout", repo, "--expected", base, "--message-file", message, path, gh=fake)
    assert result.code == 2 and "exact repository-relative" in result.err


def test_commit_create_rejects_directories_staged_changes_and_moved_heads(run, fake, repo, tmp_path):
    base = git(repo, "rev-parse", "HEAD")
    message = tmp_path / "msg"
    message.write_text("m")
    (repo / "dir").mkdir()
    (repo / "dir/f.txt").write_text("x")
    args = ("commit", "create", "--checkout", repo, "--message-file", message)
    assert "directory" in run(*args, "--expected", base, "dir", gh=fake).err
    assert "HEAD changed" in run(*args, "--expected", "a" * 40, "dir/f.txt", gh=fake).err
    git(repo, "add", "dir/f.txt")
    assert "staged changes" in run(*args, "--expected", base, "dir/f.txt", gh=fake).err


def test_commit_create_treats_glob_characters_literally(run, fake, repo, tmp_path):
    base = git(repo, "rev-parse", "HEAD")
    (repo / "a.txt").write_text("a")
    message = tmp_path / "msg"
    message.write_text("m")
    result = run("commit", "create", "--checkout", repo, "--expected", base, "--message-file", message, "*.txt", gh=fake)
    assert result.code == 1
    assert git(repo, "rev-parse", "HEAD") == base
    assert git(repo, "diff", "--cached", "--name-only") == ""


def test_commit_history_orders_filters_and_keeps_bodies(run, fake, repo):
    base = git(repo, "rev-parse", "HEAD")
    (repo / "a").write_text("1")
    git(repo, "add", "a")
    git(repo, "commit", "-qm", "ccode(PAY-1 acme/work#1): first", "-m", "Body one")
    (repo / "b").write_text("2")
    git(repo, "add", "b")
    git(repo, "commit", "-qm", "chore: not tracked")
    tip = git(repo, "rev-parse", "HEAD")
    everything = run("commit", "history", "--checkout", repo, "--base", base, "--tip", tip, gh=fake).data["commits"]
    assert [item["subject"] for item in everything] == ["ccode(PAY-1 acme/work#1): first", "chore: not tracked"]
    assert everything[0]["body"] == "Body one\n"
    only = run("commit", "history", "--checkout", repo, "--base", base, "--tip", tip, "--ccode", gh=fake).data["commits"]
    assert [item["subject"] for item in only] == ["ccode(PAY-1 acme/work#1): first"]
    whole = run("commit", "history", "--checkout", repo, gh=fake).data["commits"]
    assert len(whole) == 3


def test_commit_history_handles_a_range_with_no_commits(run, fake, repo):
    head = git(repo, "rev-parse", "HEAD")
    assert run("commit", "history", "--checkout", repo, "--base", head, "--tip", head, gh=fake).data == {"commits": []}
