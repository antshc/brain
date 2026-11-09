from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import FakeGitHub, git
from github_cli import implement_spec as spec
from github_cli.gh import Gh, GhError, Ref, UsageError

REPO = "acme/work"
SHA = "a" * 40


@pytest.mark.parametrize("value", ["", "  ", "a/b", "a\\b", "..", "a..b", ".hidden"])
def test_initiative_id_must_be_a_safe_path_component(value):
    with pytest.raises(UsageError):
        spec.validate_initiative_id(value)


def test_initiative_id_is_trimmed_and_read_from_the_title_prefix():
    assert spec.validate_initiative_id(" PAY-12 ") == "PAY-12"
    assert spec.initiative_id_of("PAY-12: Refunds: more") == "PAY-12"
    with pytest.raises(UsageError, match="no `<INITIATIVE_ID>:` prefix"):
        spec.initiative_id_of("Refunds")


def test_single_label_demands_exactly_one_non_empty_routing_label():
    assert spec.single_label(["spec", "repo:base:main"], "repo:base:") == "main"
    for labels in ([], ["repo:base:a", "repo:base:b"], ["repo:base:"]):
        with pytest.raises(UsageError, match="exactly one"):
            spec.single_label(labels, "repo:base:")


def test_ref_of_api_extracts_the_repository_or_fails():
    issue = {"repository_url": "https://api.github.com/repos/acme/work", "number": 4}
    assert spec.ref_of_api(issue) == Ref(REPO, 4)
    with pytest.raises(GhError, match="no resolvable repository"):
        spec.ref_of_api({"repository_url": "https://example.com/x", "number": 1, "html_url": "u"})


@pytest.mark.parametrize("value, ok", [("PAY-12", True), ("acme/work#5", True), ("#5", True), ("a.b_c", True),
                                       ("", False), ("a b", False), ("-x", False), ("a/b", False)])
def test_pr_initiative_accepts_ids_and_issue_references(value, ok):
    if ok:
        assert spec.pr_initiative(value) == value
    else:
        with pytest.raises(UsageError):
            spec.pr_initiative(value)


@pytest.mark.parametrize("title, ok", [
    ("[X-1] feat: add thing", True), ("[X-1] fix(api): repair", True), ("[X-1] feat(a.b-c)!: break", True),
    ("[X-1] Feat: caps", False), ("[X-1] feat:no space", False), ("X-1 feat: add", False), ("[Y-2] feat: add", False),
    ("[X-1] feat: ", False), ("[X-1] feat: two\nlines", False),
])
def test_pr_title_needs_the_initiative_prefix_and_a_conventional_subject(title, ok):
    assert spec.valid_pr_title(title, "X-1") is ok


def body(rationale="- Because\n", changes="Did it.", evidence="Tests pass.", refs=(), extra=""):
    return spec.build_body("X-1", rationale, changes, evidence, list(refs), extra)


def test_build_body_lays_out_the_managed_block():
    text = body(refs=["acme/work#2", "acme/work#3"], extra="Human note")
    assert text.startswith("[X-1]\n\n" + spec.BLOCK_BEGIN + "\n## Why\n\n- Because")
    assert "## References\n\nRefs acme/work#2\nRefs acme/work#3" in text
    assert text.rstrip().endswith("Human note") and spec.block_refs(text) == ["acme/work#2", "acme/work#3"]


@pytest.mark.parametrize("rationale", ["", "   \n", "plain prose", "- ok\nnot a bullet"])
def test_build_body_never_invents_rationale(rationale):
    with pytest.raises(UsageError, match="rationale must be non-empty"):
        body(rationale=rationale)


@pytest.mark.parametrize("kwargs", [{"changes": " "}, {"evidence": ""}])
def test_build_body_requires_changes_and_verification(kwargs):
    with pytest.raises(UsageError, match="must be non-empty"):
        body(**kwargs)


def test_build_body_rejects_reserved_markers_and_closing_keywords():
    with pytest.raises(UsageError, match="reserved"):
        body(changes=f"x {spec.BLOCK_END}")
    for phrase in ("Fixes #3", "closes acme/work#4", "Resolved: #5", "fixed #1", "RESOLVES #2"):
        with pytest.raises(UsageError, match="closing keyword"):
            body(changes=phrase)
    assert "prefixes #3" in body(changes="prefixes #3")


def test_user_text_keeps_only_text_outside_the_managed_block():
    text = body(extra="Keep me")
    assert spec.user_text(text, "X-1") == "Keep me"
    assert spec.user_text("[X-1]\n\nInitiative: X-1\nMine\n", "X-1") == "Mine"
    assert spec.block_refs("no block") == []


def test_sorted_unique_orders_numerically_within_a_repository():
    assert spec.sorted_unique(["b/x#10", "a/x#2", "b/x#9", "a/x#2"]) == ["a/x#2", "b/x#9", "b/x#10"]


def test_split_diff_pairs_real_b_side_paths_with_their_text():
    diff = "diff --git a/old.py b/new.py\n+x\ndiff --git a/dir/f.txt b/dir/f.txt\n+y\n"
    assert spec.split_diff(diff) == [("new.py", "diff --git a/old.py b/new.py\n+x\n"),
                                     ("dir/f.txt", "diff --git a/dir/f.txt b/dir/f.txt\n+y\n")]
    assert spec.split_diff("preamble only\n") == []


def test_save_artifacts_names_files_by_number_and_type_and_replaces_old_output(tmp_path):
    directory = tmp_path / "artifacts"
    directory.mkdir()
    (directory / "stale.md").write_text("old")
    rows = spec.save_artifacts([
        {"number": 1, "name": "Design Plan (v2)!", "type": "generic", "body": "text"},
        {"number": 12, "name": "!!!", "type": "embedded_html", "body": None},
    ], directory)
    assert [Path(r["file"]).name for r in rows] == ["001-design-plan-v2.md", "012-artifact.html"]
    assert not (directory / "stale.md").exists()
    assert json.loads((directory / "index.json").read_text())[0]["name"] == "Design Plan (v2)!"


def test_find_cycles_reports_each_loop_and_ignores_unknown_blockers():
    assert spec.find_cycles({"a": ["b"], "b": ["a"], "c": ["missing"]}) == [["a", "b", "a"]]
    assert spec.find_cycles({"a": ["a"]}) == [["a", "a"]]
    assert spec.find_cycles({"a": ["b"], "b": []}) == []


def graph(*tickets):
    return {"spec": {"ref": f"{REPO}#1"}, "tickets": list(tickets)}


def ticket(number, state="open", reason=None, blockers=(), hitl=False):
    return {"ref": f"{REPO}#{number}", "state": state, "state_reason": reason, "hitl": hitl,
            "blocked_by": [{"ref": f"{REPO}#{b}", "state": "open", "state_reason": None} for b in blockers]}


def test_analyse_splits_ready_blocked_deferred_and_cycles():
    result = spec.analyse(graph(ticket(2), ticket(3, blockers=[2]), ticket(4, hitl=True), ticket(5, blockers=[4]),
                                ticket(6, blockers=[7]), ticket(7, blockers=[6])), set())
    assert result["ready"] == [f"{REPO}#2"]
    assert [b["ref"] for b in result["blocked"]] == [f"{REPO}#3", f"{REPO}#6", f"{REPO}#7"]
    assert {d["ref"]: d["reason"] for d in result["deferred"]} == {f"{REPO}#4": "hitl", f"{REPO}#5": f"blocked by {REPO}#4"}
    assert result["cycles"]


def test_analyse_needs_explicit_done_even_for_closed_tickets():
    closed = ticket(2, "closed", "completed")
    assert spec.analyse(graph(closed), set())["needs_resolution"][0]["reason"] == "unverified-closed"
    assert spec.analyse(graph(closed), {f"{REPO}#2"})["done"] == [f"{REPO}#2"]
    dropped = ticket(3, "closed", "not_planned")
    assert spec.analyse(graph(dropped), {f"{REPO}#3"})["needs_resolution"][0]["reason"] == "closed-without-completion"


def source_gh(fake: FakeGitHub, pinned: str | None = SHA) -> Gh:
    fake.stub(("gh", "repo", "view"), (0, json.dumps({"nameWithOwner": REPO, "defaultBranchRef": {"name": "main"}}), ""))
    fake.branches["main"] = pinned or "short"
    return Gh(fake)


def test_verify_source_pins_the_base_commit_only_when_asked(fake):
    gh = source_gh(fake)
    assert spec.verify_source(gh, REPO, "main") == {"source_repository": REPO, "default_branch": "main"}
    assert spec.verify_source(gh, REPO, "main", pin_base=True)["base_commit"] == SHA


def test_verify_source_rejects_a_base_without_a_full_sha(fake):
    with pytest.raises(GhError, match="no valid base commit"):
        spec.verify_source(source_gh(fake, "short"), REPO, "main", pin_base=True)


def test_ensure_label_creates_only_when_missing(fake):
    created = []
    fake.stub(("gh", "label", "list"), (0, json.dumps([{"name": "other"}, {"name": "present"}]), ""))
    fake.stub(("gh", "label", "create"), lambda argv: created.append(argv) or (0, "", ""))
    gh = Gh(fake)
    assert spec.ensure_label(gh, REPO, "present") is False and created == []
    assert spec.ensure_label(gh, REPO, "fresh", color="0e8a16", description="d") is True
    assert created[0][-4:] == ["--color", "0e8a16", "--description", "d"]


def harness(tmp_path: Path, layout: str, origin: str = f"git@github.com:{REPO}.git") -> Path:
    root = tmp_path / "harness"
    checkout = root / "workspace" / "work" if layout == "split" else root
    checkout.mkdir(parents=True)
    git(checkout, "init", "-q")
    git(checkout, "remote", "add", "origin", origin)
    if layout == "split":
        root.joinpath(".git").mkdir()
    return root


def test_resolve_checkout_split_layout_puts_runs_beside_the_checkout(fake, tmp_path):
    root = harness(tmp_path, "split")
    result = spec.resolve_checkout(Gh(fake), root, REPO, 7)
    assert result["source_root"] == str(root / "workspace/work")
    assert result["run_dir"] == str(root / "workspace/work.runs/7")
    assert result["evidence_root"] == str(root / "workspace/work.evidence")


def test_resolve_checkout_single_repo_layout_places_runs_outside_the_checkout(fake, tmp_path):
    root = harness(tmp_path, "single")
    result = spec.resolve_checkout(Gh(fake), root, REPO, 7)
    assert result["source_root"] == str(root) and result["run_dir"] == str(tmp_path / "work.runs/7")


def test_resolve_checkout_uses_workspace_when_it_is_git_ignored(fake, tmp_path):
    root = harness(tmp_path, "single")
    (root / "workspace").mkdir()
    (root / ".gitignore").write_text("workspace/\n")
    assert spec.resolve_checkout(Gh(fake), root, REPO, 7)["run_dir"] == str(root / "workspace/work.runs/7")


def test_resolve_checkout_never_reuses_an_existing_run_directory(fake, tmp_path):
    root = harness(tmp_path, "single")
    (tmp_path / "work.runs/7").mkdir(parents=True)
    (tmp_path / "work.runs/7-2").mkdir()
    assert spec.resolve_checkout(Gh(fake), root, REPO, 7)["run_dir"] == str(tmp_path / "work.runs/7-3")
    assert spec.resolve_checkout(Gh(fake), root, REPO, None)["run_dir"] is None


@pytest.mark.parametrize("layout, origin, message", [
    ("single", "https://github.com/acme/other.git", "is not a primary checkout"),
    ("split", "https://github.com/acme/other.git", "does not match"),
])
def test_resolve_checkout_rejects_a_checkout_of_another_repository(fake, tmp_path, layout, origin, message):
    with pytest.raises(UsageError, match=message):
        spec.resolve_checkout(Gh(fake), harness(tmp_path, layout, origin), REPO, 1)


def test_resolve_checkout_rejects_a_workspace_without_the_checkout(fake, tmp_path):
    (tmp_path / "h/workspace").mkdir(parents=True)
    with pytest.raises(UsageError, match="is not a primary checkout"):
        spec.resolve_checkout(Gh(fake), tmp_path / "h", REPO, 1)


@pytest.fixture
def tracker(fake: FakeGitHub) -> FakeGitHub:
    def closer(argv):
        number = int(argv[3])
        fake.issues[number].update(state="closed", state_reason="completed")
        return 0, "", ""

    def commenter(argv):
        number = int(argv[3])
        ident = fake.add_comment(number, Path(argv[argv.index("--body-file") + 1]).read_text(encoding="utf-8"))
        return 0, f"https://github.com/{REPO}/issues/{number}#issuecomment-{ident}\n", ""

    fake.stub(("gh", "issue", "close"), closer)
    fake.stub(("gh", "issue", "comment"), commenter)
    return fake


def test_issue_close_posts_a_standard_comment_and_confirms_completion(run, tracker):
    number = tracker.add_issue("t")
    result = run("issue", "close", f"{REPO}#{number}", "--commit", "abc", "--branch", "feat/x", "--pr", "#9", gh=tracker)
    assert result.data == {"ref": f"{REPO}#{number}", "state": "closed", "state_reason": "completed"}
    close = next(call for call in tracker.calls if call[:3] == ["gh", "issue", "close"])
    assert close[close.index("--comment") + 1] == "Implemented in abc on feat/x (#9)."


def test_issue_close_needs_a_reason_to_close(run, tracker):
    number = tracker.add_issue("t")
    assert run("issue", "close", f"{REPO}#{number}", "--commit", "abc", gh=tracker).code == 2
    assert tracker.issues[number]["state"] == "open"


def test_issue_close_never_closes_human_in_the_loop_tickets(run, tracker):
    number = tracker.add_issue("t", labels=("hitl",))
    result = run("issue", "close", f"{REPO}#{number}", "--comment", "done", gh=tracker)
    assert result.code == 2 and "hitl" in result.err and tracker.issues[number]["state"] == "open"


def test_issue_close_reports_failure_when_the_tracker_did_not_close(run, tracker):
    number = tracker.add_issue("t")
    tracker.stub(("gh", "issue", "close"), (0, "", ""))
    result = run("issue", "close", f"{REPO}#{number}", "--comment", "done", gh=tracker)
    assert result.code == 1 and "not closed as completed" in result.err


def evidence(run, tracker, number, run_id="run-1", text="proof\n"):
    path = tracker_path(number, text)
    return run("issue", "comment", f"{REPO}#{number}", "--body-file", path, f"--run-id={run_id}", gh=tracker)


def tracker_path(number, text):
    import tempfile
    path = Path(tempfile.mkdtemp()) / f"e{number}.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_evidence_comment_is_marked_idempotent_and_never_duplicated(run, tracker):
    number = tracker.add_issue("t")
    first = evidence(run, tracker, number)
    assert first.code == 0 and first.data["problems"] == []
    stored = tracker.comments[first.data["id"]]["body"]
    assert stored.endswith(f"<!-- implement-spec:evidence run-1 {Ref(REPO, number).key} -->")
    again = evidence(run, tracker, number)
    assert again.data["id"] == first.data["id"] and len(tracker.comments) == 1


def test_evidence_comment_refuses_changed_content_closed_or_hitl_issues(run, tracker):
    number = tracker.add_issue("t")
    evidence(run, tracker, number)
    assert "differs from the recorded body" in evidence(run, tracker, number, text="other\n").err
    closed = tracker.add_issue("c", state="closed")
    assert "is closed" in evidence(run, tracker, closed).err
    hitl = tracker.add_issue("h", labels=("hitl",))
    assert "never post evidence" in evidence(run, tracker, hitl).err


@pytest.mark.parametrize("run_id", ["bad run", "-x", "a--b", "a_b", "a-"])
def test_evidence_run_id_is_validated(run, tracker, run_id):
    number = tracker.add_issue("t")
    assert evidence(run, tracker, number, run_id).code == 2 and tracker.comments == {}


def test_workflow_closure_needs_the_marked_evidence_comment(run, tracker):
    number = tracker.add_issue("t")
    comment = evidence(run, tracker, number).data["id"]
    base = ("issue", "close", f"{REPO}#{number}", "--run-id", "run-1")
    assert run(*base, gh=tracker).code == 2
    assert run(*base, "--evidence-comment", comment + 1, gh=tracker).code == 2
    assert run(*base, "--evidence-comment", comment, "--commit", "abc", gh=tracker).code == 2
    assert run(*base, "--evidence-comment", comment, gh=tracker).data["state"] == "closed"
    assert run(*base, "--evidence-comment", comment, gh=tracker).code == 0  # already closed as completed


def test_workflow_closure_preserves_a_cancelled_ticket(run, tracker):
    number = tracker.add_issue("t")
    comment = evidence(run, tracker, number).data["id"]
    tracker.issues[number].update(state="closed", state_reason="not_planned")
    result = run("issue", "close", f"{REPO}#{number}", "--run-id", "run-1", "--evidence-comment", comment, gh=tracker)
    assert result.code == 2 and "closed without completion" in result.err


def test_issue_edit_body_flags_a_body_that_differs_afterwards(run, tracker, body):
    number = tracker.add_issue("t", body="old")
    tracker.stub(("gh", "issue", "edit"), lambda argv: tracker.issues[number].update(body="new\n") or (0, "", ""))
    assert run("issue", "edit-body", f"{REPO}#{number}", "--body-file", body("new\n"), gh=tracker).code == 0
    tracker.stub(("gh", "issue", "edit"), (0, "", ""))
    tracker.issues[number]["body"] = "old"
    assert run("issue", "edit-body", f"{REPO}#{number}", "--body-file", body("new\n"), gh=tracker).code == 3


def checkpoint(**changes) -> dict:
    ticket_ref = f"{REPO}#2"
    data = {"run": {"id": "run-1", "specRef": f"{REPO}#1", "sourceRepository": REPO, "baseBranch": "main",
                    "baseCommit": SHA, "integrationBranch": "feat/x", "worktreePath": "/w", "mode": "sequential"},
            "tickets": {Ref(REPO, 2).key: {"ref": ticket_ref, "branch": "feat/x-2"}}}
    for key, value in changes.items():
        target = data["run"] if key in data["run"] or key == "maxParallel" else data
        target[key] = value
    return data


def save(run, tmp_path, data):
    source = tmp_path / "in.json"
    source.write_text(json.dumps(data))
    return run("run", "checkpoint", "--run-dir", tmp_path / "run", "--input", source)


@pytest.mark.parametrize("change, message", [
    ({"id": ""}, "missing run identity"), ({"baseCommit": "short"}, "invalid checkpoint run id or base SHA"),
    ({"id": "Bad Id"}, "invalid checkpoint run id"), ({"mode": "wild"}, "invalid checkpoint execution mode"),
    ({"mode": "sequential", "maxParallel": 2}, "invalid checkpoint execution mode"),
    ({"mode": "parallel", "maxParallel": 0}, "invalid checkpoint execution mode"),
    ({"tickets": []}, "keyed by ticket key"), ({"tickets": {"wrong": {"ref": f"{REPO}#2"}}}, "does not match ticket identity"),
])
def test_checkpoint_rejects_invalid_identity_or_shape(run, tmp_path, change, message):
    result = save(run, tmp_path, checkpoint(**change))
    assert result.code == 2 and message in result.err
    assert not (tmp_path / "run/publication-checkpoint.json").exists()


def test_checkpoint_requires_distinct_worker_branches(run, tmp_path):
    two = {Ref(REPO, 2).key: {"ref": f"{REPO}#2", "branch": "w"}, Ref(REPO, 3).key: {"ref": f"{REPO}#3", "branch": "w"}}
    assert "distinct" in save(run, tmp_path, checkpoint(tickets=two)).err
    same = {Ref(REPO, 2).key: {"ref": f"{REPO}#2", "branch": "feat/x"}}
    assert "distinct" in save(run, tmp_path, checkpoint(tickets=same)).err


def test_checkpoint_is_append_only_for_recorded_worker_state(run, tmp_path):
    assert save(run, tmp_path, checkpoint()).code == 0
    grown = checkpoint()
    grown["tickets"][Ref(REPO, 3).key] = {"ref": f"{REPO}#3"}
    assert save(run, tmp_path, grown).code == 0
    shrunk = checkpoint()
    assert "preserve run identity and recorded tickets" in save(run, tmp_path, shrunk).err
    moved = checkpoint()
    moved["tickets"][Ref(REPO, 2).key]["branch"] = "other"
    moved["tickets"][Ref(REPO, 3).key] = {"ref": f"{REPO}#3"}
    assert "preserve recorded worker branch" in save(run, tmp_path, moved).err
    changed = checkpoint(baseBranch="develop")
    changed["tickets"][Ref(REPO, 3).key] = {"ref": f"{REPO}#3"}
    assert "preserve run identity" in save(run, tmp_path, changed).err


def planner(*rows, spec_ref=f"{REPO}#1", status="completed"):
    return {"status": status, "result": {"specRef": spec_ref, "tickets": [{"ref": r, "blockers": b} for r, b in rows]}}


@pytest.mark.parametrize("plan, message", [
    (planner(status="failed"), "status completed"),
    (planner((f"{REPO}#2", []), (f"{REPO}#3", []), spec_ref="acme/work#9"), "specRef must match"),
    (planner((f"{REPO}#2", [])), "missing tickets"),
    (planner((f"{REPO}#2", []), (f"{REPO}#2", [])), "duplicate planner ticket"),
    (planner((f"{REPO}#2", [f"{REPO}#2"]), (f"{REPO}#3", [])), "self dependency"),
    (planner((f"{REPO}#2", [f"{REPO}#3", f"{REPO}#3"]), (f"{REPO}#3", [])), "duplicate planner blockers"),
    (planner((f"{REPO}#2", ["acme/other#1"]), (f"{REPO}#3", [])), "unknown planner blocker"),
    (planner((f"{REPO}#2", [f"{REPO}#3"]), (f"{REPO}#3", [f"{REPO}#2"])), "dependency cycles"),
    (planner((f"{REPO}#8", []), (f"{REPO}#2", []), (f"{REPO}#3", [])), "unknown or duplicate"),
])
def test_effective_graph_rejects_invalid_planner_output(plan, message):
    with pytest.raises(UsageError, match=message):
        spec.effective_graph(graph(ticket(2), ticket(3)), plan)


def test_effective_graph_adds_planner_edges_without_mutating_the_native_graph():
    native = graph(ticket(2), ticket(3))
    effective = spec.effective_graph(native, planner((f"{REPO}#2", []), (f"{REPO}#3", [f"{REPO}#2"])))
    assert effective["tickets"][1]["blocked_by"][0]["source"] == "planner"
    assert native["tickets"][1]["blocked_by"] == []


def pr_read(fake, run, *, title="[X-1] feat: add", body_text=None, draft=True, expect=()):
    body_text = body_text if body_text is not None else body(refs=["acme/work#2"])
    view = {"url": "https://github.com/acme/work/pull/5", "title": title, "body": body_text, "headRefOid": SHA,
            "isDraft": draft, "baseRefName": "main", "headRefName": "feat/x", "state": "OPEN"}
    fake.stub(("gh", "pr", "view"), (0, json.dumps(view), ""))
    fake.stub(("gh", "pr", "checks"), (0, json.dumps([{"name": "ci", "bucket": "pass"}]), ""))
    flags = [part for ref in expect for part in ("--expect-refs", ref)]
    return run("pr", "read", "--source-repository", REPO, "--number", 5, "--initiative-id", "X-1", *flags, gh=fake)


def test_pr_read_reports_a_clean_managed_draft(run, fake):
    result = pr_read(fake, run, expect=["acme/work#2"])
    assert result.code == 0 and result.data["problems"] == [] and result.data["refs"] == ["acme/work#2"]
    assert result.data["checks"]["status"] == "passed" and result.data["head_sha"] == SHA


@pytest.mark.parametrize("kwargs, problem", [
    ({"title": "[X-1] Feat: Caps"}, "title lacks the expected initiative"),
    ({"title": "no prefix"}, "title lacks the expected initiative"),
    ({"draft": False}, "PR is not draft"),
    ({"body_text": "[OTHER-1]\n\nbody"}, "first body initiative is 'OTHER-1'"),
    ({"expect": ["acme/work#9"]}, "missing managed references"),
])
def test_pr_read_flags_each_deviation_with_exit_3(run, fake, kwargs, problem):
    result = pr_read(fake, run, **kwargs)
    assert result.code == 3 and any(problem in item for item in result.data["problems"])


def test_pr_read_accepts_the_legacy_prefix_layout(run, fake):
    result = pr_read(fake, run, title="X-1: legacy title", body_text="X-1\n\nold body")
    assert result.code == 0 and result.data["problems"] == []


def test_pr_read_resolves_the_open_pr_by_head_and_fails_without_one(run, fake):
    fake.stub(("gh", "pr", "list"), (0, "[]", ""))
    result = run("pr", "read", "--source-repository", REPO, "--head", "feat/x", gh=fake)
    assert result.code == 2 and "no open PR found" in result.err
    assert run("pr", "read", "--source-repository", REPO, gh=fake).code == 2
