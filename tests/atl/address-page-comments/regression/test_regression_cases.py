"""Offline checks for the address-page-comments live regression: every case passes on a healthy
run's artifacts, fails on a broken one, and skips when its artifact is missing."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import apc_regression
import pytest
from cases import APPENDED_TEXT, CASES, DELETED_TEXT, EDIT_NEW, EDIT_OLD, RICH_TOKENS, evaluate

SEED = {
    "edit": {"id": "11", "marker": "m-edit"},
    "delete": {"id": "12", "marker": "m-delete"},
    "question": {"id": "13", "marker": "m-question"},
    "footer": {"id": "14", "marker": None},
}


def _span(marker: str, text: str) -> str:
    return f'<span class="annotation" data-annotation-id="{marker}" data-annotation-type="inlineComment">{text}</span>'


RICH = "\n".join(f'<div data-probe="{label}">{token}</div>' for label, token in RICH_TOKENS.items())
BEFORE = (
    f'<p data-local-id="a1">The {_span("m-edit", "retry limit")} is {EDIT_OLD}.</p>'
    f'<p data-local-id="a2">{_span("m-delete", "Legacy export")} runs nightly.</p>'
    f'<p data-local-id="a3">Logs {_span("m-question", "rotate daily")} and keep seven files.</p>\n{RICH}'
)
AFTER = (
    f'<p data-local-id="a1">The {_span("m-edit", "retry limit")} is {EDIT_NEW}.</p>'
    f'<p data-local-id="a3">Logs {_span("m-question", "rotate daily")} and keep seven files.</p>\n{RICH}'
    f'<p data-local-id="a4">{APPENDED_TEXT}</p>'
)
ATTACHMENTS = {"data": {"results": [
    {"id": f"att{n}", "title": title, "version": {"number": 1}}
    for n, title in enumerate(["regression-image.png", "regression-notes.txt", "regression-flow.drawio", "regression-sequence.drawio"])]}}


def _thread(name: str, anchor: str, target: str = "thread") -> dict:
    return {"id": SEED[name]["id"], "anchor": anchor, "replyTarget": target}


def healthy() -> dict:
    replies = {name: {"id": f"r-{name}", "sent": "Done.", "readBack": "Done.\n"} for name in ("edit", "question", "footer")}
    replies["page"] = {"id": "r-page", "sent": "", "readBack": "| x | [c](https://s/wiki/p?focusedCommentId=12) | Removed. |"}
    return {
        "seed": SEED,
        "before": BEFORE,
        "after": AFTER,
        "final": AFTER,
        "attachments-before": ATTACHMENTS,
        "attachments-after": copy.deepcopy(ATTACHMENTS),
        "gate-1": {"action": "proceed", "counts": {"pending": 4}, "threads": [
            _thread("edit", "anchored"), _thread("delete", "anchored"), _thread("question", "anchored"), _thread("footer", "page")]},
        "update": {"data": {"ok": True, "content": {"id": "42"}}},
        "gate-2": {"action": "proceed", "counts": {"pending": 4}, "threads": [
            _thread("edit", "anchored"), _thread("delete", "orphaned", "page"), _thread("question", "anchored"), _thread("footer", "page")]},
        "replies": replies,
        "gate-3": {"action": "skip", "counts": {"pending": 0, "answered": 4}, "threads": []},
        "final-comments": {"data": {"comments": [{"id": s["id"]} for s in SEED.values()]}},
    }


def _statuses(artifacts: dict) -> dict[str, str]:
    return {o.case.id: o.status for o in evaluate(artifacts)}


def test_healthy_run_passes_every_case():
    assert set(_statuses(healthy()).values()) == {"pass"}


def _break(path: tuple, value) -> dict:
    artifacts = copy.deepcopy(healthy())
    target = artifacts
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return artifacts


@pytest.mark.parametrize(("case_id", "path", "value"), [
    ("G1", ("gate-1", "action"), "skip"),
    ("E1", ("update",), {"ok": False, "error": "stale"}),
    ("E2", ("after",), AFTER.replace(EDIT_NEW, EDIT_OLD)),
    ("E2", ("after",), AFTER.replace(_span("m-edit", "retry limit"), "retry limit")),
    ("E3", ("after",), AFTER.replace("seven files", "7 files")),
    ("E4", ("after",), AFTER + f'<p data-local-id="a2">{DELETED_TEXT}</p>'),
    ("E5", ("after",), AFTER.replace(APPENDED_TEXT, "")),
    ("G2", ("gate-2", "threads"), [_thread("edit", "anchored"), _thread("delete", "anchored"), _thread("question", "anchored")]),
    ("R1", ("replies", "edit", "readBack"), ""),
    ("R2", ("replies", "page", "readBack"), "no link"),
    ("G3", ("gate-3", "action"), "proceed"),
    ("R3", ("final-comments", "data", "comments"), [{"id": "11"}]),
    ("P1", ("before",), BEFORE.replace('data-type="media-single"', "")),
    ("P2", ("final",), AFTER.replace('data-type="status"', 'data-type="text"')),
    ("P2", ("final",), AFTER.replace("<table", "")),
    ("P3", ("attachments-after", "data", "results"), ATTACHMENTS["data"]["results"][:3]),
    ("P3", ("attachments-before", "data", "results"), ATTACHMENTS["data"]["results"][1:]),
])
def test_broken_artifact_fails_its_case(case_id, path, value):
    assert _statuses(_break(path, value))[case_id] == "fail"


def test_missing_artifact_skips_dependent_cases():
    artifacts = healthy()
    del artifacts["after"]
    statuses = _statuses(artifacts)
    assert [cid for cid, s in statuses.items() if s == "skipped"] == ["E2", "E3", "E4", "E5"]


def test_build_edits_targets_annotated_nodes():
    edits = apc_regression.build_edits(BEFORE, SEED)
    assert edits[0] == {"name": "replaceNode", "localId": "a1", "value": BEFORE.split("</p>")[0].replace(EDIT_OLD, EDIT_NEW) + "</p>"}
    assert edits[1] == {"name": "deleteNode", "localId": "a2"}
    assert edits[2]["name"] == "appendNodeToEnd"


def test_verify_writes_checklist_and_results(tmp_path: Path):
    for name, value in healthy().items():
        suffix = ".html" if isinstance(value, str) else ".json"
        (tmp_path / f"{name}{suffix}").write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")
    (tmp_path / "run.json").write_text(json.dumps({"runId": "r", "space": "S", "title": "T", "pageId": "42"}), encoding="utf-8")
    outcomes = apc_regression.verify_run(tmp_path)
    assert all(o.status == "pass" for o in outcomes)
    assert f"{len(CASES)}/{len(CASES)} verified" in (tmp_path / "checklist.md").read_text(encoding="utf-8")
    assert len(json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))) == len(CASES)
