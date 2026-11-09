"""Live: repository resolution, pinned reads, code search, remote inspection and history against antshc/brain.

Run with BRAIN_GH_LIVE=repo. Read-only: nothing is created in the live repository.
"""
from __future__ import annotations

import re

import pytest

from conftest import LIVE_REPO, git

pytestmark = [pytest.mark.integration, pytest.mark.live("repo")]


@pytest.fixture
def clone(fresh_clone):
    return fresh_clone("repo")


def test_resolve_derives_the_repository_from_the_clone_origin(live, clone):
    assert live("repo", "resolve", "--checkout", clone).data == {"repo": LIVE_REPO, "checkout": str(clone), "remote": "origin"}
    assert live("repo", "resolve", "--checkout", clone, "--repo", "antshc/other", code=2).code == 2


def test_read_returns_repository_commit_and_pinned_file(live, clone):
    head = git(clone, "rev-parse", "HEAD")
    assert live("repo", "read", "--repo", LIVE_REPO).data["full_name"] == LIVE_REPO
    assert live("repo", "read", "--repo", LIVE_REPO, "--ref", head).data["sha"] == head
    readme = live("repo", "read", "--repo", LIVE_REPO, "--ref", head, "--path", "README.md").data
    assert readme["path"] == "README.md" and readme["type"] == "file"
    assert live("repo", "read", "--repo", LIVE_REPO, "--ref", head, "--path", "no/such/file.md", code=1).code == 1


def test_read_refuses_unpinned_or_escaping_paths_without_calling_github(live):
    assert "pinned commit SHA" in live("repo", "read", "--repo", LIVE_REPO, "--path", "README.md", code=2).err
    assert "repository-relative" in live("repo", "read", "--repo", LIVE_REPO, "--ref", "a" * 40, "--path", "../x", code=2).err
    assert "full commit SHA" in live("repo", "read", "--repo", LIVE_REPO, "--ref", "main", code=2).err


def test_search_returns_a_list_of_matches(live):
    matches = live("repo", "search", "--repo", LIVE_REPO, "github").data["matches"]
    assert isinstance(matches, list) and all({"path", "sha", "url"} <= set(item) for item in matches)


def test_branch_inspect_and_fetch_verify_the_remote_identity(live, clone):
    head = git(clone, "rev-parse", "HEAD")
    inspected = live("branch", "inspect", "--checkout", clone, "--name", "main", "--remote", "origin", "--repo", LIVE_REPO).data
    assert inspected["ref"] == "refs/heads/main" and inspected["local"] == inspected["remote"] == head
    assert live("branch", "fetch", "--checkout", clone, "--repo", LIVE_REPO, "--remote", "origin", "--expected", head).data == {"head": head}
    git(clone, "remote", "set-url", "origin", "https://github.com/antshc/brain-lookalike.git")
    assert "does not uniquely identify" in live("branch", "fetch", "--checkout", clone, "--repo", LIVE_REPO,
                                                "--remote", "origin", "--expected", head, code=2).err


def test_commit_history_lists_the_range_oldest_first(live, clone):
    commits = git(clone, "rev-list", "--reverse", "-n", "3", "HEAD").split()
    tip, base = commits[-1], git(clone, "rev-parse", f"{commits[-1]}~2")
    history = live("commit", "history", "--checkout", clone, "--base", base, "--tip", tip).data["commits"]
    assert len(history) == 2 and history[-1]["sha"] == tip and all(re.fullmatch(r"[0-9a-f]{40}", c["sha"]) for c in history)
