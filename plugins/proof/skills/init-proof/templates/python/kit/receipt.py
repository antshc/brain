from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .features import Features
from .surfaces import ALL_SURFACES
from .types import Receipt, Surface


def exit_code(receipt: Receipt) -> int:
    """0 PASS, 1 FAIL, 2 can't tell."""
    return {"PASS": 0, "FAIL": 1}.get(receipt.verdict, 2)


def is_stale(receipt_revision: str | None, revision: str | None) -> bool:
    """A receipt describes the revision it ran on; once the source moves on, it describes code that no longer exists."""
    return receipt_revision != revision


@dataclass(frozen=True)
class Coverage:
    partial_features: bool
    skipped_surfaces: list[Surface]


def coverage(features: Features, run_features: Sequence[str], run_surfaces: Sequence[Surface]) -> Coverage:
    """What a run left unproved: a feature subset, and surfaces the proved features have but the run skipped."""
    return Coverage(
        partial_features=len(run_features) < len(features),
        skipped_surfaces=[
            surface for surface in ALL_SURFACES
            if surface not in run_surfaces and any(name in features and surface in features[name].surfaces for name in run_features)
        ],
    )
