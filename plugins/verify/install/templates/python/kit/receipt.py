from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .builder import Registry
from .surfaces import ALL_SURFACES
from .types import ProofResult, Receipt, ReceiptVerdict, Scenario, Surface


def exit_code(verdict: str) -> int:
    """0 PASS, 1 FAIL, 2 can't tell."""
    return {"PASS": 0, "FAIL": 1}.get(verdict, 2)


# The verdict of several scenarios: "can't tell" outranks FAIL, because evidence that cannot be trusted must be fixed first.
def aggregate(receipts: Sequence[Receipt]) -> ReceiptVerdict:
    verdicts = {receipt.verdict for receipt in receipts}
    if not verdicts or "ERROR" in verdicts:
        return "ERROR"
    return "FAIL" if "FAIL" in verdicts else "PASS"


def is_stale(receipt_revision: str | None, revision: str | None) -> bool:
    """A receipt describes the revision it ran on; once the source moves on, it describes code that no longer exists."""
    return receipt_revision != revision


# A PASS needs its own persisted evidence: every declared source, cited by this check, present on disk.
def evidence_problem(result: ProofResult, declared: Sequence[str], directory: Path) -> str | None:
    if not result.evidence:
        return f'Check "{result.check}" has no evidence, so it cannot pass.'
    foreign = [reference.check for reference in result.evidence if reference.check != result.check]
    if foreign:
        return f'Check "{result.check}" cites evidence that belongs to "{foreign[0]}".'
    cited = [reference.source for reference in result.evidence]
    missing = [source for source in declared if source not in cited]
    if missing:
        return f'Check "{result.check}" has no evidence from {missing[0]}.'
    absent = [reference.artifact for reference in result.evidence if not (directory / reference.artifact).is_file()]
    if absent:
        return f'Evidence {absent[0]} for check "{result.check}" was not kept.'
    return None


# One verdict per scenario. PASS only when every check ran, passed, and kept its own evidence.
def scenario_verdict(scenario: Scenario, results: Sequence[ProofResult], directory: Path) -> tuple[ReceiptVerdict, str | None]:
    by_check = {result.check: result for result in results}
    for check in scenario.checks:
        result = by_check.get(check.id)
        if result is None:
            return "ERROR", f'Check "{check.id}" has no result.'
        if result.verdict == "PASS":
            problem = evidence_problem(result, [adapter.name for adapter in check.evidence], directory)
            if problem:
                return "ERROR", problem
    verdicts = {result.verdict for result in results}
    if "ERROR" in verdicts:
        return "ERROR", None
    if "FAIL" in verdicts:
        return "FAIL", None
    return ("ERROR", None) if "NOT_REACHED" in verdicts else ("PASS", None)


@dataclass(frozen=True)
class Coverage:
    partial: bool
    unrun: list[str]
    skipped_surfaces: list[Surface]


def coverage(registry: Registry, run: Sequence[Scenario]) -> Coverage:
    """What a run left unproved: scenarios it did not run, and surfaces only those scenarios exercise."""
    ran = {scenario.id for scenario in run}
    every = registry.scenarios
    return Coverage(
        partial=len(ran) < len(every),
        unrun=[scenario_id for scenario_id in every if scenario_id not in ran],
        skipped_surfaces=[
            surface for surface in ALL_SURFACES
            if any(surface in scenario.surfaces for scenario in every.values()) and not any(surface in scenario.surfaces for scenario in run)
        ],
    )
