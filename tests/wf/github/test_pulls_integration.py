"""Live: branch push, pull request, comment, diff, fetch, checkout and review-thread commands against antshc/brain.

Run with BRAIN_GH_LIVE=pulls. Every test pushes its own `it/<id>` branch and opens its own draft PR, so tests
share nothing and may run on any xdist worker. PRs are closed and branches deleted at session end.
"""
from __future__ import annotations

import json
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

import pytest

from conftest import LIVE_REPO, git, ident, quiet

pytestmark = [pytest.mark.integration, pytest.mark.live("pulls")]


@dataclass
class Branch:
    name: str
    clone: Path
    base: str
    head: str
    path: str
    initiative: str


@dataclass
class Pull(Branch):
    number: int = 0

    @property
    def ref(self) -> str:
        return f"{LIVE_REPO}#{self.number}"


def write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def live_branch(live, fresh_clone, cleanup, run_id, tmp_path) -> Branch:
    """A clone with one commit on a new branch, created, committed and pushed through the CLI."""
    suffix = ident(run_id)
    name, clone = f"it/{suffix}", fresh_clone("branch")
    base = git(clone, "rev-parse", "HEAD")
    live("branch", "create", "--checkout", clone, "--name", name, "--start", base)
    git(clone, "switch", "-q", name)
    relative = f"tests-live/{suffix}.txt"
    (clone / "tests-live").mkdir()
    (clone / relative).write_text(f"live test {suffix}\n")
    message = write(tmp_path, "message", f"ccode({suffix.upper()} {LIVE_REPO}#1): live test\n\nBody\n")
    head = live("commit", "create", "--checkout", clone, "--expected", base, "--message-file", message, relative).data["head"]
    push = ["branch", "push", "--checkout", clone, "--repo", LIVE_REPO, "--remote", "origin", "--name", name,
            "--expected", head, "--previous", "absent", "--set-upstream"]
    cleanup(lambda: quiet("api", "--method", "DELETE", f"repos/{LIVE_REPO}/git/refs/heads/{name}"))
    for attempt in range(3):
        pushed = live(*push, code=None)  # GitHub occasionally rejects a push under load; branch push is retry-safe
        if pushed.code == 0:
            break
        time.sleep(3 * (attempt + 1))
    assert pushed.code == 0, pushed.err
    assert pushed.data == {"ref": f"refs/heads/{name}", "head": head}
    return Branch(name, clone, base, head, relative, suffix.upper())


def open_args(branch: Branch, body: Path, title: str | None = None) -> list:
    return ["pr", "open", "--repo", LIVE_REPO, "--head", branch.name, "--base", "main", "--expected", branch.head,
            "--title", title or f"[{branch.initiative}] test: live pull request", "--body-file", body, "--draft"]


def close_pull(number: int) -> None:
    quiet("api", "--method", "PATCH", f"repos/{LIVE_REPO}/pulls/{number}", "-f", "state=closed")


@pytest.fixture
def live_pr(live, live_branch, cleanup, tmp_path) -> Pull:
    opened = live(*open_args(live_branch, write(tmp_path, "pr.md", "Live PR body\n"))).data
    cleanup(lambda: close_pull(opened["number"]))
    return Pull(**vars(live_branch), number=opened["number"])


def snapshot(live, pull: Pull, *flags) -> dict:
    return live("pr", "snapshot", pull.ref, *flags).data


def test_branch_push_is_idempotent_and_refuses_a_stale_previous(live, live_branch):
    args = ("branch", "push", "--checkout", live_branch.clone, "--repo", LIVE_REPO, "--remote", "origin", "--name",
            live_branch.name, "--expected", live_branch.head)
    assert live(*args, "--previous", "absent").data["head"] == live_branch.head
    inspected = live("branch", "inspect", "--checkout", live_branch.clone, "--name", live_branch.name,
                     "--remote", "origin", "--repo", LIVE_REPO).data
    assert inspected["local"] == inspected["remote"] == live_branch.head
    stale = live(*args[:-1], "d" * 40, "--previous", "e" * 40, code=2)
    assert "local head changed" in stale.err


def test_pr_open_creates_a_draft_once_and_find_returns_it(live, live_branch, cleanup, tmp_path):
    body = write(tmp_path, "pr.md", "Body\n")
    first = live(*open_args(live_branch, body)).data
    cleanup(lambda: close_pull(first["number"]))
    assert first["draft"] is True and first["state"] == "open" and first["body"] == "Body\n"
    assert live(*open_args(live_branch, body)).data["number"] == first["number"]
    found = live("pr", "find", "--repo", LIVE_REPO, "--head", live_branch.name).data["pullRequest"]
    assert found["number"] == first["number"] and found["isDraft"] is True
    other = live(*open_args(live_branch, body, "[X-1] test: a different title"), code=2)
    assert "differs" in other.err


def test_pr_open_refuses_a_branch_head_that_moved(live, live_branch, tmp_path):
    args = open_args(live_branch, write(tmp_path, "pr.md", "Body\n"))
    args[args.index("--expected") + 1] = "c" * 40
    assert "head changed" in live(*args, code=2).err


def test_snapshot_returns_head_base_and_threads(live, live_pr):
    data = snapshot(live, live_pr, "--inline", "--comments")
    assert data["head"]["sha"] == live_pr.head and data["draft"] is True
    assert data["inlineComments"] == [] and data["comments"] == []


def test_diff_is_pinned_to_the_reviewed_head_and_base(live, live_pr):
    base = snapshot(live, live_pr)["base"]["sha"]
    diff = live("pr", "diff", live_pr.ref, "--expected", live_pr.head, "--base", base).data
    assert f"b/{live_pr.path}" in diff["diff"] and diff["head"] == live_pr.head
    assert "changed" in live("pr", "diff", live_pr.ref, "--expected", "c" * 40, "--base", base, code=2).err


def test_diff_split_writes_one_file_per_path_with_a_manifest(live, live_pr):
    base = snapshot(live, live_pr)["base"]["sha"]
    url = f"https://github.com/{LIVE_REPO}/pull/{live_pr.number}"
    for extra in ([], ["--expected", live_pr.head, "--base", base]):
        result = live("pr", "diff-split", "--pr", url, *extra).data
        manifest = Path(result["manifest"]).read_text().splitlines()
        assert result["files"] == 1 and manifest == [f"{live_pr.path}\t{live_pr.path.replace('/', '_')}"]
        assert (Path(result["diff_dir"]) / live_pr.path.replace("/", "_")).read_text().startswith("diff --git")
        shutil.rmtree(result["diff_dir"])
    assert "requires both" in live("pr", "diff-split", "--pr", url, "--expected", live_pr.head, code=2).err


@pytest.mark.xfail(strict=True, reason="diff-split passes owner/repo#N straight to `gh pr diff`, which reads it as a branch name; "
                                       "pinned mode parses the short ref but still fails there, so only a PR URL works")
@pytest.mark.parametrize("pinned", [False, True])
def test_diff_split_accepts_a_qualified_short_reference(live, live_pr, pinned):
    base = snapshot(live, live_pr)["base"]["sha"]
    extra = ["--expected", live_pr.head, "--base", base] if pinned else []
    assert live("pr", "diff-split", "--pr", live_pr.ref, *extra).data["files"] == 1


def test_pr_comment_is_idempotent_and_upsert_replaces_in_place(live, live_pr, tmp_path):
    plain = write(tmp_path, "plain.md", "Plain\n")
    first = live("pr", "comment", live_pr.ref, "--body-file", plain).data
    assert live("pr", "comment", live_pr.ref, "--body-file", plain).data["id"] == first["id"]
    marker = f"<!-- {live_pr.initiative}:status -->"
    created = live("pr", "upsert-comment", live_pr.ref, "--marker", marker, "--body-file",
                   write(tmp_path, "v1.md", f"v1\n\n{marker}\n")).data
    updated = live("pr", "upsert-comment", live_pr.ref, "--marker", marker, "--body-file",
                   write(tmp_path, "v2.md", f"v2\n\n{marker}\n")).data
    assert updated["id"] == created["id"] and updated["body"].startswith("v2")
    assert [c["body"][:5] for c in snapshot(live, live_pr, "--comments")["comments"]] == ["Plain", "v2\n\n<"]


def test_checks_report_a_known_status_for_the_reviewed_head(live, live_pr):
    result = live("checks", "read", live_pr.ref, "--expected", live_pr.head).data
    assert result["status"] in {"absent", "pending", "passed", "failed"} and result["head"] == live_pr.head
    assert live("checks", "read", live_pr.ref, "--expected", "c" * 40, code=2).code == 2


def test_fetch_pins_head_and_base_under_a_private_namespace(live, live_pr):
    base = snapshot(live, live_pr)["base"]["sha"]
    args = ("pr", "fetch", live_pr.ref, "--expected", live_pr.head, "--base", base, "--checkout", live_pr.clone,
            "--remote", "origin", "--run-id", "run1")
    result = live(*args).data
    assert result["headRef"] == "refs/review/run1/head" and result["baseRef"] == "refs/review/run1/base"
    assert git(live_pr.clone, "rev-parse", result["headRef"]) == live_pr.head
    assert git(live_pr.clone, "rev-parse", result["baseRef"]) == base
    assert result["mergeBase"] == git(live_pr.clone, "merge-base", base, live_pr.head)
    assert "already exist" in live(*args, code=2).err


def test_checkout_switches_a_clean_checkout_to_the_reviewed_head(live, live_pr):
    base = snapshot(live, live_pr)["base"]["sha"]
    git(live_pr.clone, "switch", "-q", "main")
    result = live("pr", "checkout", live_pr.ref, "--expected", live_pr.head, "--base", base, "--checkout", live_pr.clone,
                  "--remote", "origin", cwd=live_pr.clone).data
    assert result["head"] == live_pr.head and git(live_pr.clone, "rev-parse", "HEAD") == live_pr.head
    elsewhere = live("pr", "checkout", live_pr.ref, "--expected", live_pr.head, "--base", base, "--checkout",
                     live_pr.clone, "--remote", "origin", cwd=live_pr.clone.parent, code=2)
    assert "verified checkout root" in elsewhere.err


def discussion(live, pull: Pull) -> dict:
    return live("review", "discussion", pull.ref).data


def agent_text(role: str, text: str) -> str:
    return f"{text}\n\n<!-- agent:{role}\n\n-->\n"


def test_review_thread_lifecycle_from_finding_to_resolution(live, live_pr, tmp_path):
    finding = write(tmp_path, "finding.md", agent_text("comment", "Please rename this."))
    inline = ("review", "inline", live_pr.ref, "--expected", live_pr.head, "--path", live_pr.path, "--line", 1,
              "--body-file", finding)
    posted = live(*inline).data
    assert live(*inline).data["id"] == posted["id"]

    state = discussion(live, live_pr)
    assert state["action"] == "proceed" and state["counts"]["pendingFirstPass"] == 1
    thread = state["threads"][0]
    assert thread["origin"] == "agent" and thread["anchor"]["path"] == live_pr.path and thread["anchor"]["line"] == 1

    snap = write(tmp_path, "snap1.json", json.dumps(thread["comments"]))
    answer = write(tmp_path, "answer.md", agent_text("reply", "Renamed."))
    reply = live("review", "reply", live_pr.ref, "--expected", live_pr.head, "--thread", thread["id"],
                 "--snapshot", snap, "--body-file", answer).data
    assert reply["body"].startswith("Renamed.")
    assert live("review", "reply", live_pr.ref, "--expected", live_pr.head, "--thread", thread["id"],
                "--snapshot", snap, "--body-file", answer).data["id"] == reply["id"]

    reconcile = discussion(live, live_pr)
    assert reconcile["counts"]["reconcile"] == 1 and reconcile["threads"][0]["mode"] == "follow-up"
    snap2 = write(tmp_path, "snap2.json", json.dumps(reconcile["threads"][0]["comments"]))
    resolved = live("review", "resolve", live_pr.ref, "--expected", live_pr.head, "--thread", thread["id"],
                    "--snapshot", snap2).data
    assert resolved == {"id": thread["id"], "isResolved": True}
    final = discussion(live, live_pr)
    assert final["action"] == "skip" and final["counts"]["resolved"] == 1


def test_review_refuses_to_resolve_a_human_thread_and_a_moved_head(live, live_pr, tmp_path):
    human = write(tmp_path, "human.md", "A plain human-style comment without markers.\n")
    live("review", "inline", live_pr.ref, "--expected", live_pr.head, "--path", live_pr.path, "--line", 1, "--body-file", human)
    thread = discussion(live, live_pr)["threads"][0]
    assert thread["origin"] == "human/unknown"
    snap = write(tmp_path, "snap.json", json.dumps(thread["comments"]))
    refused = live("review", "resolve", live_pr.ref, "--expected", live_pr.head, "--thread", thread["id"],
                   "--snapshot", snap, code=2)
    assert "answered agent-owned" in refused.err
    moved = live("review", "inline", live_pr.ref, "--expected", "c" * 40, "--path", live_pr.path, "--line", 1,
                 "--body-file", human, code=2)
    assert "changed" in moved.err


def test_publish_creates_then_updates_one_managed_draft(live, live_branch, cleanup, tmp_path):
    initiative = live_branch.initiative
    files = ["--rationale-file", write(tmp_path, "why.md", "- Live tests need a real PR.\n"),
             "--changes-file", write(tmp_path, "what.md", "Adds a live test file."),
             "--evidence-file", write(tmp_path, "proof.md", "Ran the live suite.")]
    args = ["pr", "publish", "--source-repository", LIVE_REPO, "--base", "main", "--head", live_branch.name,
            "--title", f"[{initiative}] test: publish live", "--initiative-id", initiative, *files,
            "--refs", f"{LIVE_REPO}#1"]
    created = live(*args).data
    cleanup(lambda: close_pull(created["number"]))
    assert created["created"] is True and created["is_draft"] is True and created["problems"] == []
    assert created["refs"] == [f"{LIVE_REPO}#1"] and created["first_body_id"] == initiative
    again = live(*args).data
    assert again["created"] is False and again["number"] == created["number"]
    read = live("pr", "read", "--source-repository", LIVE_REPO, "--head", live_branch.name,
                "--initiative-id", initiative, "--expect-refs", f"{LIVE_REPO}#1").data
    assert read["number"] == created["number"] and read["problems"] == [] and re.fullmatch(r"[0-9a-f]{40}", read["head_sha"])
    bad = live("pr", "read", "--source-repository", LIVE_REPO, "--number", created["number"],
               "--initiative-id", "OTHER-1", code=3)
    assert any("first body initiative" in problem for problem in bad.data["problems"])
