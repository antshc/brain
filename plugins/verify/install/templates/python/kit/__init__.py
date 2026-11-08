# The proof kit: what a scenario is, how it runs, and the receipt that records it. It knows nothing of the app or of whatever runs it:
# everything it needs (revision, API URL, fetch, the registry, the hints to suggest) is passed in.
from __future__ import annotations

from .builder import FeatureBuilder, Registry, feature, flow, registry
from .evidence import (
    ApiResponse, BrowserSnapshot, Collectors, ConsoleLog, EvidenceError, NetworkLog, Screenshot, StorageState, capture, now_iso, read_storage,
)
from .features import feature_names, features_for, select_scenarios, selectable_ids
from .matchers import contains_item, count_matches, field_satisfies, matches_fields, same
from .receipt import Coverage, aggregate, coverage, evidence_problem, exit_code, is_stale, scenario_verdict
from .run import Revision, run_scenario, run_steps
from .surfaces import ALL_SURFACES, is_surface, select_surfaces
from .types import (
    Assessment, EventWindow, EvidenceAdapter, EvidenceRef, Feature, Fetch, Flow, FlowContext, FlowStep, HttpAnswer, Observations, ProofCheck,
    ProofResult, ProofStep, Receipt, ReceiptVerdict, Scenario, ScenarioStep, Settle, SubFeature, Surface, SurfaceError, TraceEntry, Var, Verdict,
)

__all__ = [
    "ALL_SURFACES", "ApiResponse", "Assessment", "BrowserSnapshot", "Collectors", "ConsoleLog", "Coverage", "EventWindow", "EvidenceAdapter",
    "EvidenceError", "EvidenceRef", "Feature", "FeatureBuilder", "Fetch", "Flow", "FlowContext", "FlowStep", "HttpAnswer", "NetworkLog",
    "Observations", "ProofCheck", "ProofResult", "ProofStep", "Receipt", "ReceiptVerdict", "Registry", "Revision", "Scenario", "ScenarioStep",
    "Screenshot", "Settle", "StorageState", "SubFeature", "Surface", "SurfaceError", "TraceEntry", "Var", "Verdict",
    "aggregate", "capture", "contains_item", "count_matches", "coverage", "evidence_problem", "exit_code", "feature", "feature_names",
    "features_for", "field_satisfies", "flow", "is_stale", "is_surface", "matches_fields", "now_iso", "read_storage", "registry", "run_scenario",
    "run_steps", "same", "scenario_verdict", "select_scenarios", "select_surfaces", "selectable_ids",
]
