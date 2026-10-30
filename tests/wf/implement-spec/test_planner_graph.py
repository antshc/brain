from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import spec_gh


SPEC = "acme/specs#1"
A, B, C = (f"acme/shop#{number}" for number in (2, 3, 4))


def graph() -> dict:
    return {
        "spec": {"ref": SPEC}, "problems": [],
        "tickets": [
            {"ref": ref, "state": "open", "state_reason": None, "hitl": False, "blocked_by": []}
            for ref in (A, B, C)
        ],
    }


def plan() -> dict:
    return {"status": "completed", "result": {
        "specRef": SPEC,
        "tickets": [{"ref": A, "blockers": []}, {"ref": B, "blockers": [A]}, {"ref": C, "blockers": [B]}],
    }}


def paths(tmp_path: Path, native: dict, planner: dict) -> list[str]:
    for name, value in (("graph.json", native), ("planner.json", planner)):
        (tmp_path / name).write_text(json.dumps(value), encoding="utf-8")
    return ["graph", "frontier", "--graph", str(tmp_path / "graph.json"),
            "--planner", str(tmp_path / "planner.json"), "--out", str(tmp_path / "effective-graph.json")]


def test_inferred_dependencies_survive_tracker_refresh_and_incremental_completion(tmp_path, capsys):
    native, planner = graph(), plan()
    args = paths(tmp_path, native, planner)
    original = (tmp_path / "graph.json").read_bytes()
    for done, expected in (([], [A]), ([A], [B]), ([A, B], [C])):
        # A tracker refresh has no knowledge of run-local inferred edges.
        (tmp_path / "graph.json").write_bytes(original)
        assert spec_gh.main(args + (["--done", *done] if done else [])) == 0
        assert json.loads(capsys.readouterr().out)["ready"] == expected
        saved = json.loads((tmp_path / "effective-graph.json").read_text())
        assert saved["frontier"]["ready"] == expected
        assert saved["tickets"][1]["blocked_by"][0]["ref"] == A
        assert (tmp_path / "graph.json").read_bytes() == original


def test_native_edges_survive_planner_omissions_and_inputs_stay_unchanged():
    native, planner = graph(), plan()
    native["tickets"][1]["blocked_by"] = [{"ref": A, "state": "open", "state_reason": None}]
    planner["result"]["tickets"][1]["blockers"] = []
    before = copy.deepcopy((native, planner))
    effective = spec_gh.effective_graph(native, planner)
    assert effective["tickets"][1]["blocked_by"] == native["tickets"][1]["blocked_by"]
    assert (native, planner) == before


def test_inferred_edges_propagate_hitl_transitively():
    native = graph()
    native["tickets"][0]["hitl"] = True
    result = spec_gh.analyse(spec_gh.effective_graph(native, plan()), set())
    assert result["ready"] == []
    assert {item["ref"] for item in result["deferred"]} == {A, B, C}


def test_new_dependency_cycle_rejected_before_effective_graph_is_replaced(tmp_path, capsys):
    native, planner = graph(), plan()
    native["tickets"][0]["blocked_by"] = [{"ref": B, "state": "open", "state_reason": None}]
    args = paths(tmp_path, native, planner)
    output = tmp_path / "effective-graph.json"
    output.write_text("previous valid graph")
    assert spec_gh.main(args) == 2
    assert "cycle" in capsys.readouterr().err.lower()
    assert output.read_text() == "previous valid graph"


@pytest.mark.parametrize("mutation", [
    lambda p: p.update(status="failed"),
    lambda p: p["result"].update(specRef="other/specs#1"),
    lambda p: p["result"]["tickets"].pop(),
    lambda p: p["result"]["tickets"].append(p["result"]["tickets"][0]),
    lambda p: p["result"]["tickets"][0].update(blockers=["missing/repo#99"]),
    lambda p: p["result"]["tickets"][0].update(blockers=A),
    lambda p: p["result"]["tickets"][0].update(blockers=[None]),
    lambda p: p["result"]["tickets"][0].update(blockers=[A]),
    lambda p: p["result"]["tickets"][1].update(blockers=[A, A]),
    lambda p: p["result"]["tickets"].append({"ref": "other/repo#8", "blockers": []}),
])
def test_invalid_or_stale_planner_result_stops_before_writing(tmp_path, capsys, mutation):
    planner = plan()
    mutation(planner)
    args = paths(tmp_path, graph(), planner)
    assert spec_gh.main(args) == 2
    assert capsys.readouterr().err
    assert not (tmp_path / "effective-graph.json").exists()


def test_known_external_blocker_preserves_fetched_state():
    native, planner = graph(), plan()
    external = {"ref": "external/repo#9", "state": "closed", "state_reason": "not_planned"}
    native["tickets"][0]["blocked_by"] = [external]
    planner["result"]["tickets"][0]["blockers"] = [external["ref"]]
    result = spec_gh.analyse(spec_gh.effective_graph(native, planner), set())
    assert result["ready"] == []
    assert result["needs_resolution"] == [{"ref": A, "blocker": external["ref"], "state_reason": "not_planned"}]


@pytest.mark.parametrize("target", ["graph.json", "planner.json"])
def test_output_cannot_overwrite_native_graph_or_planner(tmp_path, capsys, target):
    args = paths(tmp_path, graph(), plan())
    before = (tmp_path / target).read_bytes()
    args[-1] = str(tmp_path / target)
    assert spec_gh.main(args) == 2
    assert "overwrite" in capsys.readouterr().err
    assert (tmp_path / target).read_bytes() == before


def test_targeted_reanalysis_changes_only_updated_recommendations():
    native, planner = graph(), plan()
    revised = copy.deepcopy(planner)
    revised["result"]["tickets"][2]["blockers"] = [A]
    result = spec_gh.analyse(spec_gh.effective_graph(native, revised), {A})
    assert result["ready"] == [B, C]
    assert planner["result"]["tickets"][2]["blockers"] == [B]
