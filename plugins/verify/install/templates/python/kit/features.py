from __future__ import annotations

from collections.abc import Sequence

from .builder import Registry
from .types import Scenario


def feature_names(registry: Registry) -> list[str]:
    return list(registry.features)


# Every id a caller may select: feature, feature.sub-feature, feature.sub-feature.scenario.
def selectable_ids(registry: Registry) -> list[str]:
    ids: list[str] = []
    for feature in registry.features.values():
        ids.append(feature.id)
        for sub in feature.sub_features:
            ids.append(sub.id)
            ids.extend(scenario.id for scenario in sub.scenarios)
    return ids


# No ids means every scenario. An unknown id is the caller's mistake, so say what exists.
def select_scenarios(registry: Registry, ids: Sequence[str] = ()) -> list[Scenario]:
    scenarios = list(registry.scenarios.values())
    if not ids:
        return scenarios
    known = selectable_ids(registry)
    unknown = [item for item in ids if item not in known]
    if unknown:
        raise ValueError(f'Unknown id "{", ".join(unknown)}". Ids: {", ".join(known)}')
    wanted = set(ids)
    return [scenario for scenario in scenarios if wanted & {scenario.feature, scenario.sub_feature, scenario.id}]


# The features a set of changed files belongs to.
def features_for(registry: Registry, files: Sequence[str]) -> list[str]:
    return [name for name, feature in registry.features.items() if any(file.startswith(prefix) for prefix in feature.touches for file in files)]
