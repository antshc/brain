# The proof kit: what a proof is and the receipt that records it. It knows nothing of the app or of whatever runs it:
# everything it needs (revision, surfaces, API URL, the features map, the hints to suggest) is passed in.
from __future__ import annotations

from .features import Features, feature_names, features_for, prove_features, select_features, surfaces_for
from .receipt import Coverage, coverage, exit_code, is_stale
from .run import Revision, read_storage, run_proof, same
from .surfaces import ALL_SURFACES, SurfaceError, is_surface, observe, select_surfaces
from .types import Check, CheckFn, Feature, ProofKit, Prove, Receipt, Surface

__all__ = [
    "ALL_SURFACES", "Check", "CheckFn", "Coverage", "Feature", "Features", "ProofKit", "Prove", "Receipt", "Revision", "Surface", "SurfaceError",
    "coverage", "exit_code", "feature_names", "features_for", "is_stale", "is_surface", "observe", "prove_features", "read_storage", "run_proof",
    "same", "select_features", "select_surfaces", "surfaces_for",
]
