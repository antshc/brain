"""Offline checks of the round-trip regression harness: the fixture survives the real
`map-markdown-adf` round trip, every capability check detects its construct, and each run's
checklist starts unchecked and is ticked only by verified evidence."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from capabilities import CAPABILITIES, body
from regression import FIXTURE, main, verify_run

IDS = [capability.id for capability in CAPABILITIES]


def test_capability_ids_are_unique():
    assert len(IDS) == len(set(IDS))


def test_init_creates_a_unique_titled_page_and_an_all_unchecked_checklist(tmp_path, capsys):
    assert main(["init", "--space", "TEST", "--runs-dir", str(tmp_path)]) == 0
    run = json.loads(capsys.readouterr().out)
    run_dir = Path(run["runDir"])

    page = (run_dir / "page.md").read_text(encoding="utf-8")
    assert page.startswith(f"# {run['title']}\n")
    assert run["title"].endswith(run["runId"])
    assert (run_dir / "assets" / "regression-image.png").is_file()
    checklist = (run_dir / "checklist.md").read_text(encoding="utf-8")
    assert checklist.count("- [ ] **") == len(CAPABILITIES)
    assert "- [x]" not in checklist
    assert "`TEST`" in checklist


@pytest.mark.parametrize("capability", CAPABILITIES, ids=IDS)
def test_every_capability_passes_on_a_healthy_round_trip(simulated_run, capability):
    outcome = {o.capability.id: o for o in verify_run(simulated_run)}[capability.id]
    assert outcome.status == "pass", outcome.detail


def test_verify_ticks_every_item_and_exits_zero_on_a_healthy_run(simulated_run, capsys):
    assert main(["verify", "--run", str(simulated_run)]) == 0
    checklist = (simulated_run / "checklist.md").read_text(encoding="utf-8")
    assert checklist.count("- [x] **") == len(CAPABILITIES)
    assert f"{len(CAPABILITIES)}/{len(CAPABILITIES)} verified" in checklist
    results = json.loads((simulated_run / "results.json").read_text(encoding="utf-8"))
    assert {r["status"] for r in results} == {"pass"}


@pytest.mark.parametrize(
    ("capability_id", "needle", "replacement"),
    [
        ("M01", "<!-- adf:toc -->", ""),
        ("M05", "[**bold link**](https://example.com/bold-link)", "**bold link**"),
        ("M07", "🔴[Red]", "Red"),
        ("L03", "3. ordered three", "1. ordered three"),
        ("B02", "> [!WARNING]", "> WARNING"),
        ("B05", "<details>", ""),
        ("T02", "multi line<br>cell a2", "multi line cell a2"),
        ("T03", "<!-- adf:wide-table -->", ""),
        ("D01", "```mermaid\n%% diagram-id: regression-flow", "```\n%% diagram-id: regression-flow"),
        ("C01", '<!-- adf:comment id="anchor-1" -->', ""),
    ],
)
def test_a_lost_construct_fails_only_its_capability(simulated_run, capability_id, needle, replacement):
    fetched = simulated_run / "fetched-1.md"
    text = fetched.read_text(encoding="utf-8")
    assert needle in text
    fetched.write_text(text.replace(needle, replacement), encoding="utf-8")

    outcome = {o.capability.id: o for o in verify_run(simulated_run)}[capability_id]

    assert outcome.status == "fail"
    checklist = (simulated_run / "checklist.md").read_text(encoding="utf-8")
    assert f"- [ ] **{capability_id}**" in checklist
    assert "FAIL:" in checklist


def test_ignored_block_reaching_confluence_fails(simulated_run):
    fetched = simulated_run / "fetched-1.md"
    fetched.write_text(fetched.read_text(encoding="utf-8") + "\nLOCAL-ONLY-NOTE leaked\n", encoding="utf-8")
    assert {o.capability.id: o.status for o in verify_run(simulated_run)}["F02"] == "fail"


def test_republish_drift_fails_idempotence(simulated_run):
    fetched = simulated_run / "fetched-2.md"
    fetched.write_text(fetched.read_text(encoding="utf-8").replace("cell b1", "cell b1 changed"), encoding="utf-8")
    outcome = {o.capability.id: o for o in verify_run(simulated_run)}["R04"]
    assert outcome.status == "fail"
    assert "cell b1 changed" in outcome.detail


def test_detached_comment_on_republish_fails(simulated_run):
    publish = simulated_run / "publish-2.json"
    result = json.loads(publish.read_text(encoding="utf-8"))
    result["orphanedComments"] = [{"id": "1", "markerRef": "m", "selection": "s"}]
    publish.write_text(json.dumps(result), encoding="utf-8")
    assert {o.capability.id: o.status for o in verify_run(simulated_run)}["R02"] == "fail"


def test_changed_attachment_bytes_fail(simulated_run):
    (simulated_run / "fetched-1.md.assets" / "regression-notes.txt").write_text("other", encoding="utf-8")
    assert {o.capability.id: o.status for o in verify_run(simulated_run)}["A02"] == "fail"


def test_missing_artifacts_are_skipped_and_verify_exits_nonzero(simulated_run, capsys):
    for name in ("publish-2.json", "fetched-2.md"):
        (simulated_run / name).unlink()

    assert main(["verify", "--run", str(simulated_run)]) == 1
    summary = json.loads(capsys.readouterr().out)
    assert set(summary["skipped"]) == {"R01", "R02", "R03", "R04", "R05"}
    assert "SKIPPED: artifact not produced" in (simulated_run / "checklist.md").read_text(encoding="utf-8")


def test_body_strips_comments_and_normalizes_asset_dirs():
    text = "x](fetched-2.md.assets/a.png)\n\n<!-- adf:ignore:start -->\n## Comments\n- c\n<!-- adf:ignore:end -->\n"
    assert body(text) == "x](ASSETS/a.png)\n"


def test_fixture_exercises_every_adf_only_construct():
    import subprocess
    import sys

    from conftest import CONVERTER

    report = json.loads(
        subprocess.run(
            [sys.executable, str(CONVERTER), "detect-adf-only"],
            input=FIXTURE.read_text(encoding="utf-8"),
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    kinds = {construct["kind"] for construct in report["constructs"]}
    # inlineComment anchors are added on Confluence by the run itself, not in the source.
    assert kinds == {"toc", "status", "panel", "wideTable", "tableLayout", "breakout", "expand"}


@pytest.mark.parametrize("content", ["", "{not json"])
def test_an_empty_or_broken_step_output_counts_as_not_produced(simulated_run, content):
    (simulated_run / "publish-2.json").write_text(content, encoding="utf-8")
    statuses = {o.capability.id: o.status for o in verify_run(simulated_run)}
    assert statuses["R01"] == statuses["R02"] == statuses["R03"] == "skipped"
