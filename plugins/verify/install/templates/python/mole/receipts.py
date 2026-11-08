from __future__ import annotations

import json
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from proof.features import REGISTRY
from proof.kit import Receipt, Scenario, aggregate, coverage, is_stale

from .commands import MOLE


# What the agent must still do before it may report: a subset of scenarios or surfaces is not a full proof.
def coverage_notes(run: Sequence[Scenario]) -> list[str]:
    result = coverage(REGISTRY, run)
    notes = []
    if result.partial:
        notes.append(f"Only {len(run)} of {len(REGISTRY.scenarios)} scenarios ran. Run {MOLE} run with no id before you report.")
    if result.skipped_surfaces:
        notes.append(f"No scenario of the {', '.join(result.skipped_surfaces)} surface ran, so it is not proved. Run {MOLE} run with no id before you report.")
    return notes


# One verdict for the whole run, with each scenario's receipt inside. `next` collects what each receipt says to do.
def summarize(receipts: Sequence[Receipt], notes: Sequence[str] = ()) -> dict[str, Any]:
    first = receipts[0] if receipts else None
    return {
        "verdict": aggregate(receipts),
        "revision": first.revision if first else None,
        "app": first.app if first else None,
        "at": first.at if first else None,
        "scenarios": [receipt.to_json() for receipt in receipts],
        "next": [step for receipt in receipts if receipt.verdict != "PASS" for step in receipt.next_steps] + list(notes)
        or ["Every selected scenario passed on this revision. Read the evidence of each before you report."],
    }


def _name(scenario: str) -> str:
    return re.sub(r"[^A-Za-z0-9.-]", "-", scenario)


# `latest/<scenario>.json` is what doctor and `receipts` read. The history is appended, never overwritten: failures stay next to the final green.
def save_receipt(directory: Path, receipt: Receipt) -> str:
    data = json.dumps(receipt.to_json(), indent=2, default=str)
    latest = directory / "receipts" / "latest"
    history = directory / "receipts" / "history"
    latest.mkdir(parents=True, exist_ok=True)
    history.mkdir(parents=True, exist_ok=True)
    (latest / f"{_name(receipt.scenario)}.json").write_text(data)
    (history / f"{re.sub(r'[:.]', '-', receipt.at)}-{_name(receipt.scenario)}-{receipt.revision or 'unknown'}.json").write_text(data)
    return data


def write_summary(path: Path, summary: dict[str, Any]) -> str:
    data = json.dumps(summary, indent=2, default=str)
    path.write_text(data)
    return data


# Per scenario: has it been proved, and is that proof about the code that is there now?
def receipt_states(directory: Path, scenarios: Sequence[Scenario], source: str | None) -> list[dict[str, Any]]:
    states: list[dict[str, Any]] = []
    for scenario in scenarios:
        path = directory / "receipts" / "latest" / f"{_name(scenario.id)}.json"
        if not path.exists():
            states.append({"scenario": scenario.id, "status": "none yet", "next": f"{MOLE} run {scenario.id}"})
            continue
        receipt = json.loads(path.read_text())
        if is_stale(receipt["revision"], source):
            states.append({
                "scenario": scenario.id,
                "status": f"STALE: the last receipt says {receipt['verdict']} for {receipt['revision']}, but the source is now {source}. That proof is for code that no longer exists.",
                "next": f"{MOLE} run {scenario.id}",
            })
            continue
        state: dict[str, Any] = {"scenario": scenario.id, "status": f"{receipt['verdict']} for the current source ({source}) at {receipt['at']}"}
        if receipt["verdict"] != "PASS":
            state["next"] = receipt["next"][0]
        states.append(state)
    return states


# For doctor: one line, and where to look for the rest.
def proof_status(directory: Path, source: str | None) -> dict[str, Any]:
    states = receipt_states(directory, list(REGISTRY.scenarios.values()), source)
    if not states:
        return {"status": "no scenarios are defined", "next": "Add a feature in proof/features/"}
    unproved = [state for state in states if not state["status"].startswith("PASS")]
    if not unproved:
        return {"status": f"PASS for the current source ({source}): all {len(states)} scenarios"}
    first = unproved[0]
    return {"status": f"{len(unproved)} of {len(states)} scenarios are not proved on the current source. {first['scenario']}: {first['status']}", "next": first["next"]}
