from __future__ import annotations

import json
import subprocess
import sys

import pytest

from conftest import SCRIPT, FakeGitHub, git

SHA = "a" * 40


@pytest.mark.parametrize("url", [
    "https://github.com/acme/work.git", "git@github.com:acme/work.git", "ssh://git@github.com/acme/work", "https://github.com/acme/work/",
])
def test_repo_resolve_derives_the_repository_from_a_github_remote(run, fake, repo, url):
    git(repo, "remote", "add", "origin", url)
    result = run("repo", "resolve", "--checkout", repo, gh=fake)
    assert result.data == {"repo": "acme/work", "checkout": str(repo), "remote": "origin"}


def test_repo_resolve_rejects_non_github_remotes_and_mismatched_claims(run, fake, repo):
    git(repo, "remote", "add", "origin", "https://gitlab.com/acme/work.git")
    assert "not a GitHub repository" in run("repo", "resolve", "--checkout", repo, gh=fake).err
    git(repo, "remote", "set-url", "origin", "https://github.com/acme/work.git")
    assert run("repo", "resolve", "--checkout", repo, "--repo", "acme/other", gh=fake).code == 2
    assert run("repo", "resolve", "--checkout", repo, "--repo", "acme/work", gh=fake).code == 0


def test_repo_resolve_requires_the_named_remote(run, fake, repo):
    assert run("repo", "resolve", "--checkout", repo, "--remote", "upstream", gh=fake).code == 1


def api_stub(fake: FakeGitHub, payload=None):
    fake.stub(("gh", "api"), lambda argv: (0, json.dumps(payload or {"ok": True}), ""))


def test_repo_read_builds_pinned_endpoints(run, fake):
    api_stub(fake)
    run("repo", "read", "--repo", "acme/work", gh=fake)
    run("repo", "read", "--repo", "acme/work", "--ref", SHA, gh=fake)
    run("repo", "read", "--repo", "acme/work", "--ref", SHA, "--path", "docs/a b/c.md", gh=fake)
    assert [call[-1] for call in fake.calls] == [
        "repos/acme/work", f"repos/acme/work/commits/{SHA}", f"repos/acme/work/contents/docs/a%20b/c.md?ref={SHA}"]


@pytest.mark.parametrize("extra", [
    ["--path", "/etc/passwd", "--ref", SHA], ["--path", "../x", "--ref", SHA], ["--path", ".", "--ref", SHA],
    ["--path", "a.md"], ["--path", "a.md", "--ref", "main"], ["--ref", "main"],
])
def test_repo_read_rejects_unpinned_or_escaping_reads(run, fake, extra):
    api_stub(fake)
    assert run("repo", "read", "--repo", "acme/work", *extra, gh=fake).code == 2
    assert fake.calls == []


def test_repo_search_scopes_the_query_and_ends_option_parsing(run, fake):
    fake.stub(("gh", "search", "code"), (0, json.dumps([{"path": "a.py"}]), ""))
    result = run("repo", "search", "--repo", "acme/work", "--", "--flag-like query", gh=fake)
    assert result.data == {"matches": [{"path": "a.py"}]}
    assert fake.calls[0] == ["gh", "search", "code", "--repo", "acme/work", "--json", "path,repository,sha,url", "--",
                             "--flag-like query"]
    assert run("repo", "search", "--repo", "bad", "q", gh=fake).code == 2


def test_exit_codes_follow_the_documented_contract(run, fake, body):
    assert run("issue", "read", "nonsense", gh=fake).code == 2
    assert run("issue", "read", "acme/work#404", gh=fake).code == 1
    assert run("label", "verify", "--repo", "acme/work", "--name", "absent", gh=fake).code == 3
    assert run("label", "verify", "--repo", "acme/work", "--name", "x", "--manifest", "/no/such.json", gh=fake).code == 2


def test_incomplete_remote_data_is_a_failure_not_a_crash(run, fake):
    fake.stub(("gh", "api"), (0, json.dumps({"unexpected": True}), ""))
    result = run("issue", "assign", "acme/work#1", "--login", "alice", gh=fake)
    assert result.code == 1 and "incomplete operation data" in result.err
    fake.stub(("gh", "api"), (0, "<html>", ""))
    assert run("issue", "read", "acme/work#1", gh=fake).code == 1


def test_a_missing_gh_binary_is_reported_not_raised(run, monkeypatch):
    monkeypatch.setenv("PATH", "")
    result = run("issue", "read", "acme/work#1")
    assert result.code == 1 and "gh is not installed" in result.err


@pytest.mark.parametrize("argv", [[], ["unknown"], ["issue"], ["issue", "nope"], ["branch", "create"], ["pr", "open"]])
def test_argument_errors_exit_2_without_touching_github(argv):
    done = subprocess.run([sys.executable, str(SCRIPT), *argv], capture_output=True, text=True)
    assert done.returncode == 2 and "usage:" in done.stderr


def test_every_documented_command_is_registered():
    done = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True)
    for group in ("repo", "branch", "commit", "worktree", "spec", "graph", "ticket", "issue", "label", "artifact",
                  "pr", "review", "checks", "run", "preflight"):
        assert group in done.stdout


def test_errors_go_to_stderr_and_stdout_stays_empty():
    done = subprocess.run([sys.executable, str(SCRIPT), "issue", "read", "nonsense"], capture_output=True, text=True)
    assert done.stdout == "" and done.stderr.startswith("error:")
