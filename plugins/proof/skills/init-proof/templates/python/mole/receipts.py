from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from proof.features import FEATURES
from proof.kit import Receipt, Surface, coverage, is_stale

from .commands import MOLE


# What the agent must still do before it may report: a subset of features or surfaces is not a full proof.
def coverage_notes(run_features: list[str], run_surfaces: list[Surface]) -> list[str]:
    result = coverage(FEATURES, run_features, run_surfaces)
    notes = []
    if result.partial_features:
        notes.append(f"Only {', '.join(run_features)} was proved. Run {MOLE} prove with no --feature before you report.")
    if result.skipped_surfaces:
        notes.append(f"The {', '.join(result.skipped_surfaces)} surface did not run, so it is not proved. Run {MOLE} prove with no --surface before you report.")
    return notes


def write_receipt(path: Path, receipt: Receipt) -> str:
    data = json.dumps(receipt.to_json(), indent=2, default=str)
    path.write_text(data)
    return data


# `latest` is what doctor reads. The history is appended, never overwritten: failures stay next to the final green.
def save_receipt(directory: Path, latest: Path, receipt: Receipt) -> str:
    (directory / "receipts").mkdir(parents=True, exist_ok=True)
    data = write_receipt(latest, receipt)
    (directory / "receipts" / f"{re.sub(r'[:.]', '-', receipt.at)}-{receipt.revision or 'unknown'}.json").write_text(data)
    return data


# Is the last receipt about the code that is there now? For doctor.
def proof_status(latest: Path, source: str | None) -> dict[str, Any]:
    if not latest.exists():
        return {"status": "none yet", "next": f"{MOLE} prove"}
    receipt = json.loads(latest.read_text())
    if is_stale(receipt["revision"], source):
        return {
            "status": f"STALE: the last receipt says {receipt['verdict']} for {receipt['revision']}, but the source is now {source}. That proof is for code that no longer exists.",
            "next": f"{MOLE} prove",
        }
    proved = receipt.get("features")
    surfaces = receipt.get("surfaces")
    result = coverage(FEATURES, proved if proved is not None else list(FEATURES), surfaces or [])
    status = f"{receipt['verdict']} for the current source ({source}) at {receipt['at']}"
    if proved and result.partial_features:
        status += f", only {', '.join(proved)}: run {MOLE} prove for all"
    if surfaces and result.skipped_surfaces:
        status += f", only the {', '.join(surfaces)} surface: run {MOLE} prove with no --surface"
    return {"status": status, **({} if receipt["verdict"] == "PASS" else {"next": receipt["next"][0]})}
