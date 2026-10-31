"""Live round-trip regression: checks a real run directory produced by
`plugins/atl/regression/run-regression.prompt.md`. Skipped unless `ATL_REGRESSION_RUN` names it.

    ATL_REGRESSION_RUN=plugins/atl/regression/runs/<runId> python3 -m pytest tests/atl/regression -k integration
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from capabilities import CAPABILITIES, evaluate
from regression import load_artifacts

RUN_DIR = os.environ.get("ATL_REGRESSION_RUN")

pytestmark = pytest.mark.skipif(not RUN_DIR, reason="ATL_REGRESSION_RUN not set; no live run to check")


@pytest.fixture(scope="module")
def outcomes() -> dict:
    _, artifacts = load_artifacts(Path(RUN_DIR))
    return {outcome.capability.id: outcome for outcome in evaluate(artifacts)}


@pytest.mark.parametrize("capability", CAPABILITIES, ids=[c.id for c in CAPABILITIES])
def test_live_round_trip_integration(outcomes, capability):
    outcome = outcomes[capability.id]
    assert outcome.status == "pass", f"{capability.id} {capability.title}: {outcome.detail}"
