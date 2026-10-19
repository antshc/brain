from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from ..features import FEATURES
from .model import DriveCall, DriveHook, Feature, Prove, ProofKit, Surface
from .surfaces import SURFACES, select_surfaces

__all__ = ["FEATURES", "DriveCall", "DriveHook", "Feature", "feature_names", "features_for", "prove_features", "select_features", "surfaces_for"]


def feature_names() -> list[str]:
    return list(FEATURES)


# No names means every feature. An unknown name is the caller's mistake, so say what exists.
def select_features(names: Sequence[str] = ()) -> list[str]:
    unknown = [name for name in names if name not in FEATURES]
    if unknown:
        raise ValueError(f'Unknown feature "{", ".join(unknown)}". Features: {", ".join(feature_names())}')
    return list(dict.fromkeys(names)) or feature_names()


# The surfaces to run for these features. No names means every surface all of them share; a name a feature lacks is refused.
def surfaces_for(features: Sequence[str], names: Sequence[str] = ()) -> list[Surface]:
    shared = [surface for surface in SURFACES if all(surface in FEATURES[name].surfaces for name in features)]
    return select_surfaces(names, shared)


# Each feature runs on the surfaces the run asked for that it has.
def prove_features(names: Sequence[str] = ()) -> Prove:
    selected = select_features(names)

    def prove(kit: ProofKit) -> None:
        for name in selected:
            surfaces = [surface for surface in kit.surfaces if surface in FEATURES[name].surfaces]
            FEATURES[name].prove(replace(kit, surfaces=surfaces))

    return prove


# The features a set of changed files belongs to.
def features_for(files: Sequence[str]) -> list[str]:
    return [name for name in feature_names() if any(file.startswith(prefix) for prefix in FEATURES[name].touches for file in files)]
