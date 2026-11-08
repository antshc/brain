"""Integration: spec_gh.py runs as a real subprocess against a stateful fake `gh` and a real git checkout."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
FAKE_GH = HERE / "fake_gh.py"
TOOL = HERE.parents[2] / "plugins" / "wf" / "skills" / "implement-spec" / "scripts" / "spec_gh.py"

pytestmark = pytest.mark.integration


def issue(state: dict, repo: str, title: str, labels: list[str], blocked_by=(), parent: str | None = None) -> str:
    state["next_id"] += 1
    number = state["counters"].get(repo, 0) + 1
    state["counters"][repo] = number
    key = f"{repo}#{number}"
    state["issues"][key] = {
        "id": state["next_id"], "number": number, "title": title, "body": f"body of {title}", "state": "open",
        "state_reason": None, "labels": [{"name": name} for name in labels],
        "repository_url": f"https://api.github.com/repos/{repo}", "html_url": f"https://github.com/{repo}/issues/{number}",
        "_sub": [], "_blocked_by": [state["issues"][ref]["id"] for ref in blocked_by],
    }
    if parent:
        state["issues"][parent]["_sub"].append(state["issues"][key]["id"])
    return key


def seed(extra_spec_labels=()) -> dict:
    state = {
        "next_id": 1000, "counters": {}, "issues": {}, "comments": {}, "prs": [], "checks": {}, "default_repo": "acme/specs",
        "repos": {"acme/specs": {"default": "main", "branches": ["main"]}, "acme/shop": {"default": "main", "branches": ["main", "release/1"]}},
        "labels": {"acme/specs": []},
    }
    labels = ["spec", "repo:target:acme/shop", "repo:base:main", *extra_spec_labels]
    state["labels"]["acme/specs"] = list(labels) + ["hitl"]
    spec = issue(state, "acme/specs", "PAY-12: Refunds", labels)
    target = ["repo:target:acme/shop"]
    t2 = issue(state, "acme/specs", "slice one", target, parent=spec)
    t3 = issue(state, "acme/specs", "slice two", target, blocked_by=[t2], parent=spec)
    t4 = issue(state, "acme/specs", "needs human", target + ["hitl"], parent=spec)
    issue(state, "acme/specs", "after human", target, blocked_by=[t4], parent=spec)
    return state


class Sandbox:
    def __init__(self, root: Path, state: dict) -> None:
        self.root = root
        self.state_file = root / "state.json"
        self.state_file.write_text(json.dumps(state))
        bin_dir = root / "bin"
        bin_dir.mkdir()
        shim = bin_dir / "gh"
        shim.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{FAKE_GH}" "$@"\n')
        shim.chmod(0o755)
        self.harness = root / "harness"
        checkout = self.harness / "workspace" / "shop"
        checkout.mkdir(parents=True)
        for repo in (self.harness, checkout):
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(checkout), "remote", "add", "origin", "git@github.com:acme/shop.git"], check=True)
        self.run_dir = root / "run"
        self.env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "FAKE_GH_STATE": str(self.state_file),
                    "PYTHONDONTWRITEBYTECODE": "1"}

    def state(self) -> dict:
        return json.loads(self.state_file.read_text())

    def write_state(self, state: dict) -> None:
        self.state_file.write_text(json.dumps(state))

    def file(self, name: str, text: str) -> str:
        path = self.root / name
        path.write_text(text)
        return str(path)

    def tool(self, *args: str, cwd: Path | None = None) -> tuple[int, dict | None, str]:
        done = subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, env=self.env, cwd=cwd or self.harness)
        return done.returncode, (json.loads(done.stdout) if done.stdout.strip() else None), done.stderr


@pytest.fixture
def sandbox(tmp_path: Path) -> Sandbox:
    return Sandbox(tmp_path, seed())


SPEC = "acme/specs#1"
PR_ARGS = ["--source-repository", "acme/shop", "--base", "main", "--head", "feat/pay-12", "--initiative-id", "PAY-12"]


def test_graph_read_saves_every_spec_artifact_across_pages(tmp_path: Path):
    state = seed()
    state["artifacts"] = {SPEC: [
        {"id": 5000 + n, "number": n, "type": "plan" if n == 1 else "generic", "name": f"part {n}", "body": f"content {n}",
         "html_url": f"https://github.com/acme/specs/issues/1/artifacts/{n}", "updated_at": None}
        for n in range(1, 103)
    ]}
    box = Sandbox(tmp_path, state)
    code, graph, err = box.tool("graph", "read", "--spec", SPEC, "--out", str(box.run_dir))
    assert code == 0, err
    records = graph["spec"]["artifacts"]
    assert [r["number"] for r in records] == list(range(1, 103))
    assert Path(records[-1]["file"]).read_text() == "content 102"
    assert json.loads((box.run_dir / "spec.json").read_text())["artifacts"] == records


def test_full_run_lifecycle(sandbox: Sandbox):
    code, pre, err = sandbox.tool("preflight", "--spec", SPEC)
    assert code == 0, err
    assert (pre["source_repository"], pre["base_branch"], pre["initiative_id"]) == ("acme/shop", "main", "PAY-12")
    assert pre["integration_branch"] == "feat/PAY-12"
    assert pre["source_root"].endswith("workspace/shop") and pre["run_dir"].endswith("workspace/shop.runs/1")

    code, graph, err = sandbox.tool("graph", "read", "--spec", SPEC, "--out", str(sandbox.run_dir))
    assert code == 0, err
    frontier = graph["frontier"]
    assert frontier["ready"] == ["acme/specs#2"]
    assert frontier["blocked"] == [{"ref": "acme/specs#3", "unmet": ["acme/specs#2"]}]
    assert {d["ref"]: d["reason"] for d in frontier["deferred"]} == {
        "acme/specs#4": "hitl", "acme/specs#5": "blocked by acme/specs#4"}
    assert json.loads(Path(graph["tickets"][0]["file"]).read_text())["comments"] == []

    code, after_done, err = sandbox.tool("graph", "frontier", "--graph", str(sandbox.run_dir / "graph.json"), "--done", "acme/specs#2")
    assert code == 0, err
    assert after_done["ready"] == ["acme/specs#3"]

    evidence = sandbox.file("evidence.md", "tests passed")
    assert sandbox.tool("issue", "comment", "acme/specs#2", "--body-file", evidence)[0] == 0
    code, closed, err = sandbox.tool("issue", "close", "acme/specs#2", "--commit", "abc123", "--branch", "feat/pay-12", "--pr", "http://pr")
    assert code == 0 and closed["state_reason"] == "completed", err
    code, graph, _ = sandbox.tool("graph", "read", "--spec", SPEC, "--out", str(sandbox.run_dir))
    assert graph["frontier"]["done"] == [] and graph["frontier"]["ready"] == []
    assert any(item["reason"] == "unverified-closed" for item in graph["frontier"]["needs_resolution"])

    rationale = sandbox.file("why.md", "- Prevent duplicate charges when customers retry timed-out payments.\n")
    title = ["--title", "PAY-12: Refunds"]
    code, pr, err = sandbox.tool("pr", "publish", *PR_ARGS, *title, "--rationale-file", rationale,
                                 "--closes", "acme/specs#2", "--refs", SPEC)
    assert code == 0, err
    assert pr["created"] and pr["is_draft"] and pr["first_body_id"] == "PAY-12" and pr["checks"]["status"] == "absent"
    state = sandbox.state()
    state["prs"][0]["body"] += "\nMy own note\n"
    state["checks"][str(pr["number"])] = [{"name": "ci", "bucket": "pending"}]
    sandbox.write_state(state)

    code, pr, err = sandbox.tool("pr", "publish", *PR_ARGS, *title, "--rationale-file", rationale, "--closes", "acme/specs#3")
    assert code == 0, err
    body = sandbox.state()["prs"][0]["body"]
    assert not pr["created"] and pr["checks"]["status"] == "pending"
    assert body.splitlines()[0] == "PAY-12"
    assert "Closes acme/specs#2" in body and "Closes acme/specs#3" in body and "Refs acme/specs#1" in body
    assert "My own note" in body and body.count("PAY-12\n") == 1

    code, read, err = sandbox.tool("pr", "read", "--source-repository", "acme/shop", "--head", "feat/pay-12",
                                   "--initiative-id", "PAY-12", "--expect-closes", "acme/specs#2", "--expect-closes", "acme/specs#3")
    assert code == 0 and read["problems"] == [], err
    code, read, _ = sandbox.tool("pr", "read", "--source-repository", "acme/shop", "--number", str(pr["number"]),
                                 "--expect-closes", "acme/specs#99")
    assert code == 3 and "missing Closes" in read["problems"][0]

    verdict = sandbox.file("verdict.md", "pass")
    code, comment, err = sandbox.tool("issue", "comment", SPEC, "--body-file", verdict)
    assert code == 0 and comment["problems"] == [], err
    code, final, err = sandbox.tool("issue", "close", SPEC, "--comment", "All gates passed.")
    assert code == 0 and final["state"] == "closed", err


def test_hitl_guards(sandbox: Sandbox):
    code, _, err = sandbox.tool("issue", "close", "acme/specs#4", "--comment", "x")
    assert code == 2 and "hitl" in err
    assert sandbox.state()["issues"]["acme/specs#4"]["state"] == "open"
    rationale = sandbox.file("why.md", "- Reason.\n")
    code, _, err = sandbox.tool("pr", "publish", *PR_ARGS, "--title", "PAY-12: X", "--rationale-file", rationale, "--closes", "acme/specs#4")
    assert code == 2 and sandbox.state()["prs"] == []


def test_planner_dependencies_survive_real_graph_refresh_without_tracker_writes(sandbox: Sandbox):
    before = sandbox.state()
    output = str(sandbox.run_dir / "effective-graph.json")
    for _ in range(2):
        code, native, err = sandbox.tool("graph", "read", "--spec", SPEC, "--out", str(sandbox.run_dir))
        assert code == 0, err
        assert native["frontier"]["ready"] == ["acme/specs#2"]
        planner = {"status": "completed", "result": {
            "specRef": SPEC,
            "tickets": [
                {"ref": item["ref"], "blockers": ["acme/specs#4"] if item["ref"] == "acme/specs#2" else []}
                for item in native["tickets"]
            ],
        }}
        planner_file = sandbox.file("planner.json", json.dumps(planner))
        code, frontier, err = sandbox.tool("graph", "frontier", "--graph", str(sandbox.run_dir / "graph.json"),
                                          "--planner", planner_file, "--out", output)
        assert code == 0, err
        assert frontier["ready"] == []
        assert {item["ref"] for item in frontier["deferred"]} == {f"acme/specs#{number}" for number in (2, 3, 4, 5)}
        saved = json.loads(Path(output).read_text())
        assert saved["frontier"] == frontier
        assert saved["tickets"][0]["blocked_by"][0]["source"] == "planner"
    assert sandbox.state() == before


def test_pr_publish_rejects_missing_rationale_and_bad_title(sandbox: Sandbox):
    empty = sandbox.file("why.md", "Added a check in PaymentService.\n")
    code, _, err = sandbox.tool("pr", "publish", *PR_ARGS, "--title", "PAY-12: X", "--rationale-file", empty)
    assert code == 2 and "rationale" in err
    good = sandbox.file("good.md", "- Reason.\n")
    code, _, err = sandbox.tool("pr", "publish", *PR_ARGS, "--title", "No prefix", "--rationale-file", good)
    assert code == 2 and "title must start" in err
    assert sandbox.state()["prs"] == []


def test_non_draft_pr_is_reported_as_problem(sandbox: Sandbox):
    rationale = sandbox.file("why.md", "- Reason.\n")
    assert sandbox.tool("pr", "publish", *PR_ARGS, "--title", "PAY-12: X", "--rationale-file", rationale)[0] == 0
    state = sandbox.state()
    state["prs"][0]["isDraft"] = False
    sandbox.write_state(state)
    code, read, _ = sandbox.tool("pr", "read", "--source-repository", "acme/shop", "--number", "1", "--initiative-id", "PAY-12")
    assert code == 3 and read["problems"] == ["PR is not draft"]


def test_plan_flow_creates_spec_tickets_and_blockers_idempotently(tmp_path: Path):
    state = seed()
    state["issues"], state["counters"], state["labels"] = {}, {}, {"acme/specs": []}
    box = Sandbox(tmp_path, state)
    plan = box.file("plan.md", "# Refunds\n\nDo the thing.\n")
    code, spec, err = box.tool("spec", "create", "--source-repository", "acme/shop", "--base-branch", "release/1",
                               "--initiative-id", "PAY-12", "--summary", "Refunds\nplan", "--body-file", plan,
                               "--source-note", "plan.md", "--tracker-repository", "acme/specs")
    assert code == 0 and spec["problems"] == [], err
    after = box.state()
    assert set(after["labels"]["acme/specs"]) == {"spec", "repo:target:acme/shop", "repo:base:release/1"}
    assert after["issues"][spec["spec"]]["title"] == "PAY-12: Refunds plan"
    assert after["issues"][spec["spec"]]["body"].endswith("Source: plan.md\n")

    refs = []
    for title in ("slice one", "slice two"):
        body = box.file(f"{title}.md", f"body {title}")
        args = ("ticket", "create", "--spec", spec["spec"], "--title", title, "--body-file", body)
        code, first, err = box.tool(*args)
        assert code == 0 and first["created"], err
        code, again, err = box.tool(*args)
        assert code == 0 and not again["created"] and again["ref"] == first["ref"], err
        refs.append(first["ref"])
    code, linked, err = box.tool("issue", "block", refs[1], "--by", refs[0])
    assert code == 0 and linked["added"] == [refs[0]], err
    assert box.tool("issue", "block", refs[1], "--by", refs[0])[1]["added"] == []

    code, graph, err = box.tool("graph", "read", "--spec", spec["spec"], "--out", str(box.run_dir))
    assert code == 0, err
    assert [t["ref"] for t in graph["tickets"]] == refs and graph["frontier"]["ready"] == [refs[0]]
    edited = box.file("edited.md", "new body")
    assert box.tool("issue", "edit-body", refs[0], "--body-file", edited)[1]["problems"] == []


def test_exit_codes_for_routing_and_github_failures(tmp_path: Path):
    state = seed(extra_spec_labels=["repo:target:other/repo"])
    box = Sandbox(tmp_path, state)
    code, _, err = box.tool("preflight", "--spec", SPEC)
    assert code == 2 and "exactly one" in err
    code, _, err = box.tool("preflight", "--spec", "acme/specs#404")
    assert code == 1 and "404" in err
    code, _, err = box.tool("preflight", "--spec", SPEC, "--source-repository", "acme/shop", "--base-branch", "missing")
    assert code == 1 and "404" in err
    code, _, err = box.tool("preflight", "--spec", SPEC, "--source-repository", "acme/shop", "--base-branch", "main",
                            "--harness-root", str(tmp_path / "nowhere"))
    assert code == 2 and "not found" in err


def test_preflight_defaults_harness_root_from_cwd_and_run_dir_never_collides(sandbox: Sandbox):
    (sandbox.harness / "workspace" / "shop.runs" / "1").mkdir(parents=True)
    code, pre, err = sandbox.tool("preflight", "--spec", "https://github.com/acme/specs/issues/1", cwd=sandbox.harness)
    assert code == 0, err
    assert pre["run_dir"].endswith("shop.runs/1-2") and pre["harness_root"] == str(sandbox.harness.resolve())


def test_pr_diff_split_end_to_end(sandbox: Sandbox):
    state = sandbox.state()
    state["diff"] = "diff --git a/src/a.py b/src/a.py\n+++ b/src/a.py\n+y\ndiff --git a/README.md b/README.md\n+++ b/README.md\n+z\n"
    sandbox.write_state(state)
    code, result, err = sandbox.tool("pr", "diff-split", "--pr", "https://github.com/acme/shop/pull/9")
    assert code == 0 and result["files"] == 2, err
    out = Path(result["diff_dir"])
    try:
        assert (out / "_manifest.tsv").read_text().splitlines() == ["src/a.py\tsrc_a.py", "README.md\tREADME.md"]
        assert "+y" in (out / "src_a.py").read_text()
        assert not str(out).startswith(str(sandbox.harness))
    finally:
        import shutil
        shutil.rmtree(out)
    state["diff"] = ""
    sandbox.write_state(state)
    assert sandbox.tool("pr", "diff-split", "--pr", "9")[0] == 1


def test_plan_preflight_is_read_only_and_rejects_invalid_execution_options(sandbox):
    before = sandbox.state()
    args = ("preflight", "--source-repository", "acme/shop", "--base-branch", "main", "--initiative-id", "PAY-12")
    code, _, err = sandbox.tool(*args, "--mode", "invalid")
    assert code == 2 and "mode" in err
    code, _, err = sandbox.tool(*args, "--max-parallel", "0", "--mode", "parallel")
    assert code == 2 and "max-parallel" in err
    code, pre, err = sandbox.tool(*args)
    assert code == 0, err
    assert pre["spec"] is None and pre["source_root"].endswith("workspace/shop")
    assert sandbox.state() == before


def test_graph_uses_distinct_snapshot_keys_for_same_number_across_repositories(sandbox):
    state = sandbox.state()
    refs = [issue(state, repo, title, [], parent=SPEC)
            for repo, title in (("a_b/c", "first"), ("a/b_c", "second"))]
    sandbox.write_state(state)
    code, graph, err = sandbox.tool("graph", "read", "--spec", SPEC, "--out", str(sandbox.run_dir))
    assert code == 0, err
    tickets = [ticket for ticket in graph["tickets"] if ticket["ref"] in refs]
    assert len({ticket["key"] for ticket in tickets}) == 2
    for ticket in tickets:
        path = Path(ticket["file"])
        assert path.stem == ticket["key"]
        assert json.loads(path.read_text())["ref"] == ticket["ref"]


@pytest.mark.parametrize("lost_command", ["pr create", "issue comment", "issue close"])
def test_publication_recovers_lost_response_without_duplicate_writes(sandbox, lost_command):
    ref = "acme/specs#2"
    rationale = sandbox.file("why.md", "- Prevent duplicate charges.\n")
    evidence = sandbox.file("evidence.md", "tests passed")
    publish = ("pr", "publish", *PR_ARGS, "--title", "PAY-12: Refunds",
               "--rationale-file", rationale, "--closes", ref)
    comment = ("issue", "comment", ref, "--body-file", evidence, "--run-id", "run-1")
    state = sandbox.state()
    state["lose_response"] = lost_command
    sandbox.write_state(state)

    def retry(args):
        code, result, err = sandbox.tool(*args)
        if " ".join(args[:2]) == {"pr create": "pr publish"}.get(lost_command, lost_command):
            assert code == 1 and "lost response" in err
            code, result, err = sandbox.tool(*args)
        assert code == 0, err
        return result

    retry(publish)
    posted = retry(comment)
    close = ("issue", "close", ref, "--run-id", "run-1", "--evidence-comment", str(posted["id"]))
    assert retry(close)["state_reason"] == "completed"
    state = sandbox.state()
    assert len(state["prs"]) == len(state["comments"]) == 1


def test_preflight_fetches_exact_sha_and_worktree_uses_it_after_base_advances(sandbox):
    upstream = sandbox.root / "upstream" / "acme" / "shop.git"
    upstream.parent.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(upstream)], check=True)
    checkout = sandbox.harness / "workspace" / "shop"

    def git(repo, *args):
        return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()

    git(checkout, "remote", "set-url", "origin", str(upstream))
    git(upstream, "-c", "user.name=Test", "-c", "user.email=test@example.com",
        "commit", "-q", "--allow-empty", "-m", "initial")
    pinned = git(upstream, "rev-parse", "HEAD")
    state = sandbox.state()
    state["branch_heads"] = {"acme/shop:main": pinned}
    sandbox.write_state(state)
    code, pre, err = sandbox.tool("preflight", "--spec", SPEC, "--pin-base")
    assert code == 0, err
    assert pre["base_commit"] == pinned

    git(upstream, "-c", "user.name=Test", "-c", "user.email=test@example.com",
        "commit", "-q", "--allow-empty", "-m", "advanced")
    tip = git(upstream, "rev-parse", "HEAD")
    worktree = sandbox.root / "integration"
    git(checkout, "worktree", "add", "-b", pre["integration_branch"], str(worktree), pre["base_commit"])
    assert git(worktree, "rev-parse", "HEAD") == pinned != tip
    assert git(worktree, "merge-base", "--is-ancestor", pinned, "HEAD") == ""


def test_checkpoint_persists_progress_and_refuses_changed_identity(sandbox):
    code, graph, err = sandbox.tool("graph", "read", "--spec", SPEC, "--out", str(sandbox.run_dir))
    assert code == 0, err
    ticket = graph["tickets"][0]
    run = {"id": "run-1", "specRef": SPEC, "sourceRepository": "acme/shop", "baseBranch": "main",
           "baseCommit": "a" * 40, "integrationBranch": "feat/PAY-12", "worktreePath": str(sandbox.root / "wt"),
           "mode": "sequential", "maxParallel": None}
    data = {"run": run, "tickets": {ticket["key"]: {"ref": ticket["ref"], "commit": "b" * 40}}}

    def checkpoint():
        return sandbox.tool("run", "checkpoint", "--run-dir", str(sandbox.run_dir),
                            "--input", sandbox.file("checkpoint-input.json", json.dumps(data)))

    code, result, err = checkpoint()
    assert code == 0, err
    saved = Path(result["file"])
    assert json.loads(saved.read_text()) == data
    data["tickets"][ticket["key"]]["pushedHead"] = "b" * 40
    assert checkpoint()[0] == 0
    previous = saved.read_bytes()
    run["integrationBranch"] = "feat/wrong"
    assert checkpoint()[0] == 2
    assert saved.read_bytes() == previous
