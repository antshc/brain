from __future__ import annotations

import json

import pytest

REPO = "acme/work"


def test_issue_read_returns_the_issue_and_optionally_its_comments(run, fake):
    number = fake.add_issue("Slice", "Details")
    fake.add_comment(number, "first")
    plain = run("issue", "read", f"{REPO}#{number}", gh=fake)
    assert plain.data["title"] == "Slice" and "comments" not in plain.data
    full = run("issue", "read", f"{REPO}#{number}", "--comments", gh=fake)
    assert [c["body"] for c in full.data["comments"]] == ["first"]


@pytest.mark.parametrize("ref", ["12", "https://github.com/acme/work/pull/1", "acme/work"])
def test_issue_commands_demand_a_qualified_issue_reference(run, fake, ref):
    result = run("issue", "read", ref, gh=fake)
    assert result.code == 2 and fake.calls == []


def test_issue_read_missing_issue_is_a_tool_failure(run, fake):
    assert run("issue", "read", f"{REPO}#99", gh=fake).code == 1


def test_issue_list_skips_pull_requests_and_filters_by_every_label(run, fake):
    both = fake.add_issue("both", labels=("spec", "area"))
    fake.add_issue("one", labels=("spec",))
    fake.add_issue("a pull", labels=("spec", "area"), pull=True)
    result = run("issue", "list", "--repo", REPO, "--label", "spec", "--label", "area", gh=fake)
    assert [issue["number"] for issue in result.data["issues"]] == [both]


def test_issue_list_requires_a_valid_repository(run, fake):
    assert run("issue", "list", "--repo", "noslash", gh=fake).code == 2


def test_issue_create_writes_exact_body_and_labels_then_verifies(run, fake, body):
    text = "Line with `code`, \u00e9 and CRLF\r\n\n"
    result = run("issue", "create", "--repo", REPO, "--title", "Slice", "--body-file", body(text), "--label", "spec", gh=fake)
    assert result.code == 0 and result.data["created"] is True and result.data["problems"] == []
    stored = fake.issues[result.data["number"]]
    assert stored["body"] == text and [label["name"] for label in stored["labels"]] == ["spec"]


def test_issue_create_is_idempotent_for_an_identical_issue(run, fake, body):
    number = fake.add_issue("Slice", "Body\n", labels=("spec",))
    result = run("issue", "create", "--repo", REPO, "--title", "Slice", "--body-file", body("Body\n"), "--label", "spec", gh=fake)
    assert result.data["created"] is False and result.data["number"] == number
    assert fake.writes() == []


def test_issue_create_refuses_a_conflicting_or_ambiguous_title(run, fake, body):
    fake.add_issue("Slice", "Different\n", labels=("spec",))
    args = ("issue", "create", "--repo", REPO, "--title", "Slice", "--body-file", body("Body\n"), "--label", "spec")
    assert run(*args, gh=fake).code == 2
    fake.add_issue("Slice", "Body\n", labels=("spec",))
    assert run(*args, gh=fake).code == 2
    assert fake.writes() == []


def test_issue_create_ignores_same_title_under_other_labels(run, fake, body):
    fake.add_issue("Slice", "Body\n", labels=("other",))
    result = run("issue", "create", "--repo", REPO, "--title", "Slice", "--body-file", body("Body\n"), "--label", "spec", gh=fake)
    assert result.data["created"] is True and len(fake.issues) == 2


def test_issue_create_reports_a_verification_failure_after_the_write(run, fake, body):
    fake.fail("GET", r"issues/\d+$", "HTTP 502")
    result = run("issue", "create", "--repo", REPO, "--title", "T", "--body-file", body("B"), gh=fake)
    assert result.code == 1 and "created acme/work#1; verification failed" in result.err


def test_issue_create_flags_content_that_differs_after_create(run, fake, body):
    original = fake._create_issue

    def mangled(m, query, payload):
        status, issue = original(m, query, payload)
        issue["body"] = payload["body"].strip()
        return status, issue

    fake._create_issue = mangled
    result = run("issue", "create", "--repo", REPO, "--title", "T", "--body-file", body("B\n"), gh=fake)
    assert result.code == 3 and result.data["problems"] == ["issue differs after create"]


def test_issue_create_missing_body_file_is_a_usage_error(run, fake, tmp_path):
    result = run("issue", "create", "--repo", REPO, "--title", "T", "--body-file", tmp_path / "none.md", gh=fake)
    assert result.code == 2


def test_children_and_blockers_list_native_relations(run, fake):
    parent, child, blocker = (fake.add_issue(name) for name in ("parent", "child", "blocker"))
    fake.sub_issues[parent] = [fake.issues[child]["id"]]
    fake.blocked_by[child] = [fake.issues[blocker]["id"]]
    assert [i["number"] for i in run("issue", "children", f"{REPO}#{parent}", gh=fake).data["children"]] == [child]
    assert [i["number"] for i in run("issue", "blockers", f"{REPO}#{child}", gh=fake).data["blockers"]] == [blocker]


def test_link_child_links_once_and_is_idempotent(run, fake):
    parent, child = fake.add_issue("p"), fake.add_issue("c")
    args = ("issue", "link-child", f"{REPO}#{parent}", f"{REPO}#{child}")
    assert run(*args, gh=fake).data == {"parent": f"{REPO}#{parent}", "child": f"{REPO}#{child}", "linked": True}
    assert run(*args, gh=fake).code == 0
    assert fake.sub_issues[parent] == [fake.issues[child]["id"]]
    assert len([w for w in fake.writes() if w.startswith("POST")]) == 1


def test_link_child_rejects_self_parenting(run, fake):
    number = fake.add_issue("x")
    assert run("issue", "link-child", f"{REPO}#{number}", f"{REPO}#{number}", gh=fake).code == 2


def test_link_child_accepts_a_lost_response_when_the_link_exists(run, fake):
    parent, child = fake.add_issue("p"), fake.add_issue("c")
    fake.lose("POST", r"sub_issues$")
    assert run("issue", "link-child", f"{REPO}#{parent}", f"{REPO}#{child}", gh=fake).code == 0
    assert len(fake.sub_issues[parent]) == 1


def test_link_child_fails_loudly_when_the_link_cannot_be_confirmed(run, fake):
    parent, child = fake.add_issue("p"), fake.add_issue("c")
    fake.fail("POST", r"sub_issues$", "HTTP 422")
    result = run("issue", "link-child", f"{REPO}#{parent}", f"{REPO}#{child}", gh=fake)
    assert result.code == 1 and "unconfirmed" in result.err


def test_assign_claims_an_unassigned_open_issue(run, fake):
    number = fake.add_issue("x")
    result = run("issue", "assign", f"{REPO}#{number}", "--login", "alice", gh=fake)
    assert result.data == {"assignees": ["alice"], "problems": []}


def test_assign_resolves_me_through_the_authenticated_user(run, fake):
    number = fake.add_issue("x")
    assert run("issue", "assign", f"{REPO}#{number}", gh=fake).data["assignees"] == ["bot"]


def test_assign_is_idempotent_for_the_current_assignee(run, fake):
    number = fake.add_issue("x", assignees=("alice",))
    assert run("issue", "assign", f"{REPO}#{number}", "--login", "alice", gh=fake).code == 0
    assert fake.writes() == []


def test_assign_refuses_claimed_or_closed_issues(run, fake):
    taken = fake.add_issue("x", assignees=("bob",))
    closed = fake.add_issue("y", state="closed")
    for number in (taken, closed):
        result = run("issue", "assign", f"{REPO}#{number}", "--login", "alice", gh=fake)
        assert result.code == 2 and "no longer claimable" in result.err
    assert fake.writes() == []


def test_assign_reports_a_problem_when_the_write_does_not_stick(run, fake):
    number = fake.add_issue("x")
    fake._assign = lambda n, p, add: (0, fake.issues[n])
    result = run("issue", "assign", f"{REPO}#{number}", "--login", "alice", gh=fake)
    assert result.code == 3 and result.data["problems"] == ["assignment differs after write"]


def test_unassign_removes_only_the_named_login(run, fake):
    number = fake.add_issue("x", assignees=("alice", "bob"))
    assert run("issue", "unassign", f"{REPO}#{number}", "--login", "alice", gh=fake).data["assignees"] == ["bob"]
    assert run("issue", "unassign", f"{REPO}#{number}", "--login", "alice", gh=fake).code == 0


def test_label_ensure_creates_only_missing_labels(run, fake):
    fake.labels["existing"] = {"name": "existing", "color": "ffffff"}
    result = run("label", "ensure", "--repo", REPO, "--name", "fresh", "--color", "0e8a16", gh=fake)
    assert result.data == {"labels": ["fresh"], "created": ["fresh"], "missing": [], "problems": []}
    again = run("label", "ensure", "--repo", REPO, "--name", "fresh", "--color", "0e8a16", gh=fake)
    assert again.data["created"] == []


def test_label_ensure_reads_a_manifest_and_combines_it_with_a_name(run, fake, tmp_path):
    manifest = tmp_path / "labels.json"
    manifest.write_text(json.dumps([{"name": "a", "color": "aaaaaa"}, {"name": "b", "color": "bbbbbb"}]))
    result = run("label", "ensure", "--repo", REPO, "--manifest", manifest, "--name", "c", "--color", "cccccc", gh=fake)
    assert result.data["created"] == ["a", "b", "c"]
    clash = run("label", "ensure", "--repo", REPO, "--manifest", manifest, "--name", "a", "--color", "aaaaaa", gh=fake)
    assert clash.code == 2 and "already supplied" in clash.err


@pytest.mark.parametrize("color", ["", "12345", "gggggg", "#aaaaaa"])
def test_label_ensure_rejects_bad_colors_before_any_write(run, fake, color):
    flags = ["--color", color] if color else []
    assert run("label", "ensure", "--repo", REPO, "--name", "x", *flags, gh=fake).code == 2
    assert fake.writes() == []


def test_label_requires_a_name_or_manifest(run, fake):
    assert run("label", "ensure", "--repo", REPO, gh=fake).code == 2


def test_label_ensure_tolerates_a_create_race_but_not_a_real_failure(run, fake):
    fake.lose("POST", r"labels$")
    race = run("label", "ensure", "--repo", REPO, "--name", "raced", "--color", "aaaaaa", gh=fake)
    assert race.code == 0 and race.data["created"] == ["raced"]
    fake.fail("POST", r"labels$", "HTTP 403")
    assert run("label", "ensure", "--repo", REPO, "--name", "denied", "--color", "aaaaaa", gh=fake).code == 1


def test_label_verify_reports_missing_labels_without_writing(run, fake):
    fake.labels["present"] = {"name": "present", "color": "aaaaaa"}
    result = run("label", "verify", "--repo", REPO, "--name", "present", gh=fake)
    assert result.code == 0
    missing = run("label", "verify", "--repo", REPO, "--name", "absent", gh=fake)
    assert missing.code == 3 and missing.data["problems"] == ["missing label: absent"]
    assert fake.writes() == []
