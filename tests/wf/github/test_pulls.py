from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import BASE, HEAD, FakeGitHub, git

REPO = "acme/work"
DIFF = (
    "diff --git a/src/a.py b/src/a.py\n--- a/src/a.py\n+++ b/src/a.py\n@@ -1 +1 @@\n-old\n+new\n"
    "diff --git a/docs/b b.md b/docs/b b.md\n--- a/docs/b b.md\n+++ b/docs/b b.md\n@@ -1 +1 @@\n-x\n+y\n"
)


@pytest.fixture
def pr(fake: FakeGitHub) -> str:
    number = fake.add_pull(title="Subject", body="Existing")
    return f"{REPO}#{number}"


def test_pr_snapshot_reads_metadata_and_optional_threads(run, fake, pr):
    number = int(pr.split("#")[1])
    fake.add_comment(number, "discussion")
    fake.review_comments[7] = {"id": 7, "pull": number, "body": "inline"}
    plain = run("pr", "snapshot", pr, gh=fake)
    assert plain.data["head"]["sha"] == HEAD and "comments" not in plain.data
    full = run("pr", "snapshot", pr, "--inline", "--comments", gh=fake)
    assert [c["body"] for c in full.data["comments"]] == ["discussion"]
    assert [c["body"] for c in full.data["inlineComments"]] == ["inline"]


def test_pr_commands_reject_issue_urls(run, fake):
    assert run("pr", "snapshot", "https://github.com/acme/work/issues/1", gh=fake).code == 2


def test_pr_find_returns_the_single_match_or_none(run, fake):
    fake.stub(("gh", "pr", "list"), (0, json.dumps([{"number": 3}]), ""))
    assert run("pr", "find", "--repo", REPO, "--head", "feat/x", gh=fake).data == {"pullRequest": {"number": 3}}
    fake.stub(("gh", "pr", "list"), (0, "[]", ""))
    assert run("pr", "find", "--repo", REPO, "--head", "feat/x", gh=fake).data == {"pullRequest": None}
    fake.stub(("gh", "pr", "list"), (0, json.dumps([{"number": 1}, {"number": 2}]), ""))
    assert run("pr", "find", "--repo", REPO, "--head", "feat/x", gh=fake).code == 2


def test_pr_diff_returns_the_diff_for_the_pinned_head_and_base(run, fake, pr):
    fake.stub(("gh", "pr", "diff"), (0, DIFF, ""))
    result = run("pr", "diff", pr, "--expected", HEAD, "--base", BASE, gh=fake)
    assert result.data == {"diff": DIFF, "head": HEAD, "base": BASE}


@pytest.mark.parametrize("expected, base", [("c" * 40, BASE), (HEAD, "c" * 40)])
def test_pr_diff_refuses_a_moved_head_or_base(run, fake, pr, expected, base):
    result = run("pr", "diff", pr, "--expected", expected, "--base", base, gh=fake)
    assert result.code == 2 and "changed" in result.err
    assert not any(call[:3] == ["gh", "pr", "diff"] for call in fake.calls)


def test_pr_diff_refuses_a_head_that_moves_while_the_diff_is_read(run, fake, pr):
    number = int(pr.split("#")[1])

    def moving(argv):
        fake.pulls[number]["head"]["sha"] = "c" * 40
        return 0, DIFF, ""

    fake.stub(("gh", "pr", "diff"), moving)
    assert run("pr", "diff", pr, "--expected", HEAD, "--base", BASE, gh=fake).code == 2


def test_pr_diff_refuses_a_closed_pull_request(run, fake):
    number = fake.add_pull(state="closed")
    assert run("pr", "diff", f"{REPO}#{number}", "--expected", HEAD, "--base", BASE, gh=fake).code == 2


def test_diff_split_writes_one_file_per_changed_path_and_a_manifest(run, fake):
    fake.stub(("gh", "pr", "diff"), (0, DIFF, ""))
    result = run("pr", "diff-split", "--pr", f"{REPO}#1", gh=fake)
    out = Path(result.data["diff_dir"])
    try:
        assert result.data["files"] == 2
        manifest = dict(line.split("\t") for line in Path(result.data["manifest"]).read_text().splitlines())
        assert manifest == {"src/a.py": "src_a.py", "docs/b b.md": "docs_b b.md"}
        assert (out / "src_a.py").read_text().startswith("diff --git a/src/a.py")
    finally:
        shutil.rmtree(out)


def test_diff_split_disambiguates_colliding_names_and_rejects_empty_diffs(run, fake):
    colliding = "diff --git a/a/b b/a/b\n+1\ndiff --git a/a_b b/a_b\n+2\n"
    fake.stub(("gh", "pr", "diff"), (0, colliding, ""))
    result = run("pr", "diff-split", "--pr", f"{REPO}#1", gh=fake)
    try:
        names = [line.split("\t")[1] for line in Path(result.data["manifest"]).read_text().splitlines()]
        assert len(set(names)) == 2
    finally:
        shutil.rmtree(result.data["diff_dir"])
    fake.stub(("gh", "pr", "diff"), (0, "", ""))
    assert run("pr", "diff-split", "--pr", f"{REPO}#1", gh=fake).code == 1


def test_diff_split_pinned_mode_needs_both_pins_and_checks_the_snapshot(run, fake, pr):
    fake.stub(("gh", "pr", "diff"), (0, DIFF, ""))
    assert run("pr", "diff-split", "--pr", pr, "--expected", HEAD, gh=fake).code == 2
    assert run("pr", "diff-split", "--pr", pr, "--expected", "c" * 40, "--base", BASE, gh=fake).code == 2
    result = run("pr", "diff-split", "--pr", pr, "--expected", HEAD, "--base", BASE, gh=fake)
    shutil.rmtree(result.data["diff_dir"])
    assert result.code == 0


def test_diff_split_tells_the_caller_to_discard_a_snapshot_that_moved(run, fake, pr):
    number = int(pr.split("#")[1])
    seen = []

    def diff(argv):
        seen.append(1)
        fake.pulls[number]["head"]["sha"] = "c" * 40
        return 0, DIFF, ""

    fake.stub(("gh", "pr", "diff"), diff)
    result = run("pr", "diff-split", "--pr", pr, "--expected", HEAD, "--base", BASE, gh=fake)
    assert result.code == 1 and "discard snapshot" in result.err
    shutil.rmtree(result.err.split("discard snapshot at ")[1].split(":")[0])


def post(run, fake, pr, text, body, *extra, action="comment"):
    return run("pr", action, pr, "--body-file", body(text), *extra, gh=fake)


def test_pr_comment_creates_once_and_reuses_an_identical_comment(run, fake, pr, body):
    first = post(run, fake, pr, "Hello\n", body)
    assert first.code == 0 and first.data["body"] == "Hello\n"
    second = post(run, fake, pr, "Hello\n", body)
    assert second.data["id"] == first.data["id"] and len(fake.comments) == 1


def test_pr_comment_requires_an_existing_pull_request(run, fake, body):
    assert post(run, fake, f"{REPO}#99", "x", body).code == 1


def test_upsert_updates_the_marked_comment_in_place(run, fake, pr, body):
    marker = "<!-- agent:status -->"
    first = post(run, fake, pr, f"v1\n\n{marker}\n", body, "--marker", marker, action="upsert-comment")
    second = post(run, fake, pr, f"v2\n\n{marker}\n", body, "--marker", marker, action="upsert-comment")
    assert second.data["id"] == first.data["id"] and second.data["body"].startswith("v2")
    assert len(fake.comments) == 1


@pytest.mark.parametrize("text", ["no marker at all\n", "inline <!-- m --> marker\n", "<!-- m -->extra\n"])
def test_upsert_demands_the_exact_standalone_marker_line(run, fake, pr, body, text):
    marker = "<!-- m -->"
    assert post(run, fake, pr, text, body, "--marker", marker, action="upsert-comment").code == 2
    assert post(run, fake, pr, "<!-- m -->\n", body, "--marker", "m", action="upsert-comment").code == 2
    assert fake.writes() == []


def test_upsert_refuses_to_edit_another_authors_comment(run, fake, pr, body):
    marker = "<!-- m -->"
    fake.add_comment(int(pr.split("#")[1]), f"theirs\n{marker}", login="someone-else")
    result = post(run, fake, pr, f"mine\n{marker}", body, "--marker", marker, action="upsert-comment")
    assert result.code == 2 and "another author" in result.err
    assert "theirs" in next(iter(fake.comments.values()))["body"]


def test_comment_writes_refuse_duplicate_marked_comments(run, fake, pr, body):
    marker = "<!-- m -->"
    for text in ("a", "b"):
        fake.add_comment(int(pr.split("#")[1]), f"{text}\n{marker}")
    assert post(run, fake, pr, f"c\n{marker}", body, "--marker", marker, action="upsert-comment").code == 2


def test_post_comment_after_a_lost_response_does_not_duplicate(run, fake, pr, body):
    fake.lose("POST", r"comments$")
    assert post(run, fake, pr, "Hello\n", body).code == 1
    assert post(run, fake, pr, "Hello\n", body).code == 0
    assert len(fake.comments) == 1


def test_issue_comment_commands_write_to_issues(run, fake, body):
    number = fake.add_issue("x")
    result = run("issue", "post-comment", f"{REPO}#{number}", "--body-file", body("note\n"), gh=fake)
    assert result.code == 0 and fake.comments[result.data["id"]]["issue"] == number
    with pytest.raises(SystemExit):
        run("issue", "upsert-comment", f"{REPO}#{number}", "--body-file", body("note\n"), gh=fake)


def test_comment_write_that_does_not_match_after_the_write_is_an_error(run, fake, pr, body):
    original = fake._route

    def tampering(method, endpoint, payload, fields):
        status, result = original(method, endpoint, payload, fields)
        if method == "GET" and "issues/comments/" in endpoint:
            result = {**result, "body": "tampered"}
        return status, result

    fake._route = tampering
    result = post(run, fake, pr, "real\n", body)
    assert result.code == 1 and "differs after write" in result.err


def checks(fake, rows=None, stderr=""):
    fake.stub(("gh", "pr", "checks"), (0 if rows else 1, json.dumps(rows) if rows else "", stderr))


@pytest.mark.parametrize("rows, status", [
    ([{"name": "a", "bucket": "pass"}, {"name": "b", "bucket": "skipping"}], "passed"),
    ([{"name": "a", "bucket": "pass"}, {"name": "b", "bucket": "pending"}], "pending"),
    ([{"name": "a", "bucket": "fail"}, {"name": "b", "bucket": "pending"}], "failed"),
    ([{"name": "a", "bucket": "cancel"}], "failed"),
    ([{"name": "a", "bucket": "unheard-of"}], "pending"),
])
def test_checks_summarise_the_worst_bucket(run, fake, pr, rows, status):
    checks(fake, rows)
    result = run("checks", "read", pr, "--expected", HEAD, gh=fake)
    assert result.data["status"] == status and result.data["head"] == HEAD


def test_checks_distinguish_no_checks_from_a_failed_read(run, fake, pr):
    checks(fake, None, "no checks reported on the 'feat/x' branch")
    assert run("checks", "read", pr, "--expected", HEAD, gh=fake).data["status"] == "absent"
    checks(fake, None, "HTTP 500")
    assert run("checks", "read", pr, "--expected", HEAD, gh=fake).code == 1


def test_checks_refuse_a_head_other_than_the_expected_one(run, fake, pr):
    checks(fake, [{"name": "a", "bucket": "pass"}])
    assert run("checks", "read", pr, "--expected", "c" * 40, gh=fake).code == 2


def open_args(body, head=HEAD, **overrides):
    values = {"--repo": REPO, "--head": "feat/x", "--base": "main", "--expected": head, "--title": "[X-1] feat: add",
              "--body-file": body("Body\n"), **overrides}
    return ["pr", "open", *[part for item in values.items() for part in item], "--draft"]


def test_pr_open_creates_a_draft_and_verifies_it(run, fake, body):
    fake.branches["feat/x"] = HEAD
    result = run(*open_args(body), gh=fake)
    assert result.code == 0 and result.data["draft"] is True and result.data["body"] == "Body\n"
    assert len(fake.pulls) == 1


def test_pr_open_reuses_an_identical_pull_request(run, fake, body):
    fake.branches["feat/x"] = HEAD
    first = run(*open_args(body), gh=fake)
    second = run(*open_args(body), gh=fake)
    assert second.data["number"] == first.data["number"] and len(fake.pulls) == 1


def test_pr_open_refuses_a_pull_request_that_differs(run, fake, body):
    fake.branches["feat/x"] = HEAD
    run(*open_args(body), gh=fake)
    result = run(*open_args(body, **{"--title": "[X-1] feat: other"}), gh=fake)
    assert result.code == 2 and "differs" in result.err


def test_pr_open_refuses_a_branch_that_moved_or_is_missing(run, fake, body):
    fake.branches["feat/x"] = "c" * 40
    assert run(*open_args(body), gh=fake).code == 2
    assert fake.writes() == []
    assert run(*open_args(body, **{"--head": "missing"}), gh=fake).code == 1


def test_pr_open_refuses_ambiguous_matches(run, fake, body):
    fake.branches["feat/x"] = HEAD
    fake.add_pull(head_ref="feat/x")
    fake.add_pull(head_ref="feat/x")
    assert run(*open_args(body), gh=fake).code == 2


@pytest.fixture
def snapshot(fake: FakeGitHub, repo: Path, tmp_path: Path):
    """A real checkout plus a bare remote that serves refs/pull/N/head and the base commit."""
    fake.remote_url = f"https://github.com/{REPO}.git"
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "switch", "-qc", "feat/x")
    (repo / "f.txt").write_text("f")
    git(repo, "add", "f.txt")
    git(repo, "commit", "-qm", "change")
    head = git(repo, "rev-parse", "HEAD")
    bare = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    git(repo, "remote", "add", "origin", str(bare))
    git(repo, "push", "-q", "origin", f"{base}:refs/heads/main", f"{head}:refs/pull/5/head")
    fake._number = 4
    fake.add_pull(head=head, base=base)
    return repo, head, base


def fetch_args(repo, head, base, run_id="run1"):
    return ["pr", "fetch", f"{REPO}#5", "--expected", head, "--base", base, "--checkout", repo, "--remote", "origin",
            f"--run-id={run_id}"]


def test_pr_fetch_pins_head_and_base_under_a_private_namespace(run, fake, snapshot):
    repo, head, base = snapshot
    result = run(*fetch_args(repo, head, base), gh=fake)
    assert result.data == {"head": head, "base": base, "mergeBase": base, "headRef": "refs/review/run1/head",
                           "baseRef": "refs/review/run1/base"}
    assert git(repo, "rev-parse", "refs/review/run1/head") == head
    again = run(*fetch_args(repo, head, base), gh=fake)
    assert again.code == 2 and "already exist" in again.err


@pytest.mark.parametrize("run_id", ["../x", "a b", "-x", ""])
def test_pr_fetch_rejects_unsafe_run_ids(run, fake, snapshot, run_id):
    repo, head, base = snapshot
    assert run(*fetch_args(repo, head, base, run_id), gh=fake).code == 2


def test_pr_fetch_refuses_a_head_that_moved_before_fetching(run, fake, snapshot):
    repo, head, base = snapshot
    assert run(*fetch_args(repo, "c" * 40, base), gh=fake).code == 2
    assert git(repo, "for-each-ref", "refs/review") == ""


def test_pr_fetch_reports_partial_refs_when_the_head_moves_afterwards(run, fake, snapshot):
    repo, head, base = snapshot
    stub_calls = []

    def moved(argv):
        stub_calls.append(argv)
        fake.pulls[5]["head"]["sha"] = "c" * 40
        return subprocess.run(argv, capture_output=True, text=True).returncode, "", ""

    fake.stub(("fetch", "--no-tags"), moved)
    result = run(*fetch_args(repo, head, base), gh=fake)
    assert result.code == 1 and "reconcile refs/review/run1/head" in result.err


def test_pr_checkout_requires_the_verified_clean_checkout_root(run, fake, snapshot, monkeypatch, tmp_path):
    repo, head, base = snapshot
    args = ["pr", "checkout", f"{REPO}#5", "--expected", head, "--base", base, "--checkout", repo, "--remote", "origin"]
    fake.stub(("gh", "pr", "checkout"), (0, "", ""))
    monkeypatch.chdir(tmp_path)
    assert "verified checkout root" in run(*args, gh=fake).err
    monkeypatch.chdir(repo)
    (repo / "dirty.txt").write_text("x")
    assert "dirty" in run(*args, gh=fake).err
    (repo / "dirty.txt").unlink()
    assert run(*args, gh=fake).data == {"checkout": str(repo), "head": head}


def test_pr_checkout_refuses_when_the_checked_out_head_differs(run, fake, snapshot, monkeypatch):
    repo, head, base = snapshot
    monkeypatch.chdir(repo)
    git(repo, "switch", "-q", "--detach", base)
    fake.stub(("gh", "pr", "checkout"), (0, "", ""))
    args = ["pr", "checkout", f"{REPO}#5", "--expected", head, "--base", base, "--checkout", repo, "--remote", "origin"]
    assert "differs from the reviewed head" in run(*args, gh=fake).err
