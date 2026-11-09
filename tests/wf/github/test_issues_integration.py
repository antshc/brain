"""Live: issue, label, comment, assignment, hierarchy, dependency and artifact commands against antshc/brain.

Run with BRAIN_GH_LIVE=issues. Every issue and label created here is removed at session end.
"""
from __future__ import annotations

import uuid

import pytest

from conftest import LIVE_REPO, eventually, gh_live, quiet

pytestmark = [pytest.mark.integration, pytest.mark.live("issues")]


def ref(issue: dict) -> str:
    return f"{LIVE_REPO}#{issue['number']}"


@pytest.fixture
def label(live, cleanup, run_id):
    """A label unique to the test, so no test depends on, or pollutes, another test's issue lists."""
    name = f"{run_id}-{uuid.uuid4().hex[:6]}"
    result = live("label", "ensure", "--repo", LIVE_REPO, "--name", name, "--color", "0e8a16", "--description", "live test")
    assert result.data["created"] == [name]
    cleanup(lambda: quiet("label", "delete", name, "-R", LIVE_REPO, "--yes"))
    return name


def test_label_ensure_is_idempotent_and_verify_reports_missing(live, label, run_id):
    again = live("label", "ensure", "--repo", LIVE_REPO, "--name", label, "--color", "0e8a16")
    assert again.data["created"] == [] and again.data["labels"] == [label]
    assert live("label", "verify", "--repo", LIVE_REPO, "--name", label).data["missing"] == []
    missing = live("label", "verify", "--repo", LIVE_REPO, "--name", f"{run_id}-absent", code=3)
    assert missing.data["problems"] == [f"missing label: {run_id}-absent"]


def test_issue_create_read_list_and_reconcile(live, live_issue, label):
    text = "Body with `code`, quotes \" ' and \u00e9.\n"
    issue = live_issue("create", text, (label,))
    assert issue["created"] is True and issue["problems"] == []
    read = live("issue", "read", ref(issue)).data
    assert read["body"].replace("\r\n", "\n") == text and [item["name"] for item in read["labels"]] == [label]
    listed = eventually(lambda: live("issue", "list", "--repo", LIVE_REPO, "--label", label).data["issues"])
    assert [item["number"] for item in listed] == [issue["number"]]

    body = gh_live("issue", "view", str(issue["number"]), "-R", LIVE_REPO, "--json", "body", "--jq", ".body")
    assert body.strip() == text.strip()


def test_issue_create_returns_the_existing_issue_instead_of_a_duplicate(live, live_issue, label, tmp_path):
    first = live_issue("dedupe", "Same body\n", (label,))
    # The label-filtered list that reconciliation reads lags a few seconds behind a create.
    eventually(lambda: live("issue", "list", "--repo", LIVE_REPO, "--label", label).data["issues"])
    path = tmp_path / "again.md"
    path.write_text("Same body\n")
    title = first["title"]
    again = live("issue", "create", "--repo", LIVE_REPO, "--title", title, "--body-file", path, "--label", label).data
    assert again["created"] is False and again["number"] == first["number"]
    conflict = tmp_path / "conflict.md"
    conflict.write_text("Different body\n")
    result = live("issue", "create", "--repo", LIVE_REPO, "--title", title, "--body-file", conflict, "--label", label, code=2)
    assert "conflicting issue" in result.err


def test_issue_read_with_comments_and_missing_issue(live, live_issue):
    issue = live_issue("comments")
    assert live("issue", "read", ref(issue), "--comments").data["comments"] == []
    missing = live("issue", "read", f"{LIVE_REPO}#999999", code=1)
    assert "failed" in missing.err


def test_post_comment_is_idempotent_and_upsert_updates_in_place(live, live_issue, tmp_path):
    issue = live_issue("post-comment")
    note = tmp_path / "note.md"
    note.write_text("Plain note\n")
    first = live("issue", "post-comment", ref(issue), "--body-file", note).data
    assert live("issue", "post-comment", ref(issue), "--body-file", note).data["id"] == first["id"]

    marker = f"<!-- {issue['title'].split(']')[0][1:]}:status -->"
    status = tmp_path / "status.md"
    status.write_text(f"v1\n\n{marker}\n")
    created = live("issue", "upsert-comment", ref(issue), "--body-file", status, "--marker", marker).data
    status.write_text(f"v2\n\n{marker}\n")
    updated = live("issue", "upsert-comment", ref(issue), "--body-file", status, "--marker", marker).data
    assert updated["id"] == created["id"] and updated["body"].startswith("v2")
    bodies = [c["body"] for c in live("issue", "read", ref(issue), "--comments").data["comments"]]
    assert len(bodies) == 2 and bodies[0] == "Plain note\n" and bodies[1].startswith("v2")


def test_upsert_rejects_a_body_without_the_marker(live, live_issue, tmp_path):
    issue = live_issue("marker")
    note = tmp_path / "n.md"
    note.write_text("no marker\n")
    result = live("issue", "upsert-comment", ref(issue), "--body-file", note, "--marker", "<!-- m -->", code=2)
    assert "standalone comment marker" in result.err
    assert live("issue", "read", ref(issue), "--comments").data["comments"] == []


def test_assign_and_unassign_the_authenticated_user(live, live_issue):
    issue = live_issue("assign")
    login = gh_live("api", "user", "--jq", ".login").strip()
    assert live("issue", "assign", ref(issue)).data == {"assignees": [login], "problems": []}
    assert live("issue", "assign", ref(issue)).data["assignees"] == [login]
    assert live("issue", "unassign", ref(issue)).data["assignees"] == []


def test_sub_issue_link_and_children_listing(live, live_issue):
    parent, child = live_issue("parent"), live_issue("child")
    linked = live("issue", "link-child", ref(parent), ref(child)).data
    assert linked == {"parent": ref(parent), "child": ref(child), "linked": True}
    assert live("issue", "link-child", ref(parent), ref(child)).code == 0
    children = live("issue", "children", ref(parent)).data["children"]
    assert [item["number"] for item in children] == [child["number"]]
    assert "own child" in live("issue", "link-child", ref(parent), ref(parent), code=2).err


def test_blocked_by_dependencies_are_recorded_and_listed(live, live_issue):
    blocked, blocker = live_issue("blocked"), live_issue("blocker")
    added = live("issue", "block", ref(blocked), "--by", ref(blocker)).data
    assert added["added"] == [ref(blocker)] and added["blocked_by"] == [ref(blocker)]
    assert live("issue", "block", ref(blocked), "--by", ref(blocker)).data["added"] == []
    listed = live("issue", "blockers", ref(blocked)).data["blockers"]
    assert [item["number"] for item in listed] == [blocker["number"]]


def test_issue_edit_body_replaces_the_body_and_verifies(live, live_issue, tmp_path):
    issue = live_issue("edit", "before\n")
    path = tmp_path / "after.md"
    path.write_text("after\n")
    assert live("issue", "edit-body", ref(issue), "--body-file", path).data["problems"] == []
    assert live("issue", "read", ref(issue)).data["body"].strip() == "after"


@pytest.fixture
def artifact_issue(live, live_issue):
    issue = live_issue("artifacts")
    probe = live("artifact", "list", ref(issue), code=None)
    if probe.code:
        pytest.skip(f"issue artifacts unavailable in {LIVE_REPO}: {probe.err.strip()}")
    return issue


def test_artifact_put_list_get_and_idempotent_rewrite(live, artifact_issue, tmp_path):
    issue = artifact_issue
    path = tmp_path / "plan.md"
    path.write_text("# Plan\n\nv1\n")
    args = ("artifact", "put", ref(issue), "--name", "Live plan", "--type", "generic", "--body-file", path)
    first = live(*args).data
    assert first["name"] == "Live plan" and first["body"].strip().endswith("v1")
    assert live(*args).data["number"] == first["number"]
    path.write_text("# Plan\n\nv2\n")
    assert live(*args).data["body"].strip().endswith("v2")
    listed = live("artifact", "list", ref(issue)).data["artifacts"]
    assert [item["name"] for item in listed] == ["Live plan"]
    assert live("artifact", "get", ref(issue), first["number"]).data["body"].strip().endswith("v2")
    assert live("artifact", "get", ref(issue), 999, code=2).code == 2
    clash = live("artifact", "put", ref(issue), "--name", "Live plan", "--type", "embedded_html", "--body-file", path, code=2)
    assert "conflicts" in clash.err
