from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import replace

from .surfaces import select_surfaces
from .types import Feature, ProofKit, Prove, Surface

# Features by name. The caller owns the map; the kit only reads it.
Features = Mapping[str, Feature]


def feature_names(features: Features) -> list[str]:
    return list(features)


# No names means every feature. An unknown name is the caller's mistake, so say what exists.
def select_features(features: Features, names: Sequence[str] = ()) -> list[str]:
    unknown = [name for name in names if name not in features]
    if unknown:
        raise ValueError(f'Unknown feature "{", ".join(unknown)}". Features: {", ".join(features)}')
    return list(dict.fromkeys(names)) or feature_names(features)


# The surfaces to run for these features. No names means every supported surface all of them share; a name a feature lacks is refused.
def surfaces_for(features: Features, selected: Sequence[str], supported: Sequence[Surface], names: Sequence[str] = ()) -> list[Surface]:
    shared = [surface for surface in supported if all(surface in features[name].surfaces for name in selected)]
    return select_surfaces(names, shared)


# Each feature runs on the surfaces the run asked for that it has.
def prove_features(features: Features, names: Sequence[str] = ()) -> Prove:
    selected = select_features(features, names)

    def prove(kit: ProofKit) -> None:
        for name in selected:
            surfaces = [surface for surface in kit.surfaces if surface in features[name].surfaces]
            features[name].prove(replace(kit, surfaces=surfaces))

    return prove


# The features a set of changed files belongs to.
def features_for(features: Features, files: Sequence[str]) -> list[str]:
    return [name for name in features if any(file.startswith(prefix) for prefix in features[name].touches for file in files)]
