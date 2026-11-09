"""Live: spec, ticket, graph, preflight, evidence and closure commands against antshc/brain.

Run with BRAIN_GH_LIVE=specs. Each test builds and removes its own spec; the shared routing labels
`repo:target:antshc/brain` and `repo:base:main` are ensured once and never deleted, because parallel
workers use them at the same time.
"""
from __future__ import annotations

import re

import pytest

from conftest import LIVE_REPO, eventually, ident

pytestmark = [pytest.mark.integration, pytest.mark.live("specs")]

ROUTING = {"repo:target:antshc/brain": "0e8a16", "repo:base:main": "c5def5"}


@pytest.fixture(scope="session")
def routing_labels(live):
    for name, color in ROUTING.items():
        live("label", "ensure", "--repo", LIVE_REPO, "--name", name, "--color", color)


@pytest.fixture
def initiative(run_id):
    return ident(run_id).upper()


def write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def spec_args(initiative, tmp_path, profile):
    args = ["spec", "create", "--profile", profile, "--tracker-repository", LIVE_REPO, "--source-repository", LIVE_REPO,
            "--base-branch", "main", "--initiative-id", initiative, "--summary", "Live spec",
            "--body-file", write(tmp_path, "spec.md", "Spec body\n")]
    return args + (["--source-note", "live test"] if profile == "implement-spec" else [])


def spec_listed(live, number: int) -> bool:
    issues = live("issue", "list", "--repo", LIVE_REPO, "--label", "spec", "--label", "repo:target:antshc/brain").data["issues"]
    return any(item["number"] == number for item in issues)


def test_design_spec_creates_one_labelled_spec_issue(live, routing_labels, track_issue, initiative, tmp_path):
    result = live(*spec_args(initiative, tmp_path, "design")).data
    track_issue(result["number"])
    labels = {item["name"] for item in live("issue", "read", f"{LIVE_REPO}#{result['number']}").data["labels"]}
    assert result["title"] == f"{initiative}: Live spec" and labels == {"spec", *ROUTING}
    # Duplicate detection reads a label-filtered list that lags a few seconds behind the create.
    eventually(lambda: spec_listed(live, result["number"]))
    again = live(*spec_args(initiative, tmp_path, "design"), code=2)
    assert "spec already exists" in again.err


@pytest.fixture
def spec_graph(live, routing_labels, track_issue, initiative, run_id, tmp_path):
    """An implement-spec issue with two tickets, the second blocked by the first."""
    spec = live(*spec_args(initiative, tmp_path, "implement-spec")).data
    assert spec["problems"] == []
    spec_ref = spec["spec"]
    track_issue(int(spec_ref.split("#")[1]))
    refs = []
    for number, title in enumerate(("first", "second"), 1):
        ticket = live("ticket", "create", "--spec", spec_ref, "--title", f"[{run_id}] {initiative} {title}",
                      "--body-file", write(tmp_path, f"t{number}.md", f"Ticket {title}\n")).data
        assert ticket["created"] is True and ticket["linked"] is True
        track_issue(int(ticket["ref"].split("#")[1]))
        refs.append(ticket["ref"])
    live("issue", "block", refs[1], "--by", refs[0])
    return spec_ref, refs


def test_ticket_create_is_idempotent_for_a_linked_title(live, spec_graph, run_id, initiative, tmp_path):
    spec_ref, refs = spec_graph
    again = live("ticket", "create", "--spec", spec_ref, "--title", f"[{run_id}] {initiative} first",
                 "--body-file", write(tmp_path, "again.md", "x\n")).data
    assert again == {"ref": refs[0], "created": False, "linked": True}


def test_graph_read_and_frontier_follow_native_blockers(live, spec_graph, tmp_path):
    spec_ref, (first, second) = spec_graph
    out = tmp_path / "graph"
    graph = live("graph", "read", "--spec", spec_ref, "--out", out).data
    assert sorted(t["ref"] for t in graph["tickets"]) == sorted([first, second])
    assert graph["frontier"]["ready"] == [first]
    assert graph["frontier"]["blocked"] == [{"ref": second, "unmet": [first]}]
    assert (out / "graph.json").is_file() and (out / "spec.json").is_file()
    after = live("graph", "frontier", "--graph", out / "graph.json", "--done", first).data
    assert after["ready"] == [second] and after["done"] == [first]


def test_preflight_pins_the_live_base_commit(live, spec_graph, fresh_clone, run_id):
    spec_ref, _ = spec_graph
    clone = fresh_clone("preflight")
    branch = f"feat/{ident(run_id)}"
    result = live("preflight", "--spec", spec_ref, "--harness-root", clone, "--pin-base", "--integration-branch", branch).data
    assert result["spec"] == spec_ref and result["source_repository"] == LIVE_REPO
    assert result["base_branch"] == "main" and result["integration_branch"] == branch
    assert re.fullmatch(r"[0-9a-f]{40}", result["base_commit"])
    assert result["source_root"] == str(clone) and result["run_dir"].endswith(f"brain.runs/{spec_ref.split('#')[1]}")


def test_preflight_rejects_a_checkout_of_another_repository(live, spec_graph, tmp_path):
    spec_ref, _ = spec_graph
    result = live("preflight", "--spec", spec_ref, "--harness-root", tmp_path, code=2)
    assert "not found and" in result.err or "not a primary checkout" in result.err


def test_evidence_and_workflow_closure_are_marked_and_idempotent(live, spec_graph, run_id, tmp_path):
    _, (first, _second) = spec_graph
    marker_run = ident(run_id)
    note = write(tmp_path, "evidence.md", "Verified by the live suite.\n")
    posted = live("issue", "comment", first, "--body-file", note, "--run-id", marker_run).data
    assert posted["problems"] == []
    assert live("issue", "comment", first, "--body-file", note, "--run-id", marker_run).data["id"] == posted["id"]
    closed = live("issue", "close", first, "--run-id", marker_run, "--evidence-comment", posted["id"]).data
    assert closed["state"] == "closed" and closed["state_reason"] == "completed"
    assert live("issue", "read", first).data["state"] == "closed"
    assert live("issue", "close", first, "--run-id", marker_run, "--evidence-comment", posted["id"]).code == 0
    assert live("issue", "comment", first, "--body-file", note, "--run-id", ident(run_id), code=2).code == 2


def test_plain_close_requires_a_reason_and_records_completion(live, spec_graph):
    _, (_first, second) = spec_graph
    assert live("issue", "close", second, code=2).code == 2
    closed = live("issue", "close", second, "--commit", "abc1234", "--branch", "feat/live").data
    assert closed["state_reason"] == "completed"
