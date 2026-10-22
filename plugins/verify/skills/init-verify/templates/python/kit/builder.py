from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from .surfaces import ALL_SURFACES, is_surface
from .types import Feature, Flow, FlowContext, FlowStep, ProofCheck, ProofStep, Scenario, ScenarioStep, SubFeature, Surface

SLUG = re.compile(r"[a-z][a-z0-9-]*")
FLOW_ID = re.compile(r"[a-z][a-z0-9-]*(\.[a-z][a-z0-9-]*)*")


@dataclass(frozen=True)
class Registry:
    features: Mapping[str, Feature]
    flows: Mapping[str, Flow]

    @property
    def scenarios(self) -> dict[str, Scenario]:
        return {scenario.id: scenario for feature in self.features.values() for scenario in feature.scenarios}


def flow(flow_id: str) -> Callable[[Callable[[FlowContext], None]], Flow]:
    """Name a function as a reusable flow: `@flow("catalog.open")`."""

    def wrap(run: Callable[[FlowContext], None]) -> Flow:
        if not FLOW_ID.fullmatch(flow_id):
            raise ValueError(f'Flow id "{flow_id}" must be lowercase words joined by hyphens, with dots between groups')
        return Flow(flow_id, run)

    return wrap


def _slug(kind: str, value: str) -> str:
    if not SLUG.fullmatch(value):
        raise ValueError(f'{kind} "{value}" must be lowercase words joined by hyphens')
    return value


class FeatureBuilder:
    """feature(...).sub_feature(...).scenario(...).flow(...).proof(...).build(): one chain per feature."""

    def __init__(self, name: str, *, touches: Sequence[str], surfaces: Sequence[Surface]) -> None:
        self._name = _slug("Feature", name)
        self._touches = tuple(touches)
        self._surfaces = tuple(dict.fromkeys(surfaces))
        unknown = [surface for surface in self._surfaces if not is_surface(surface)]
        if unknown or not self._surfaces:
            raise ValueError(f'Feature "{name}" needs surfaces from: {", ".join(ALL_SURFACES)}')
        if not self._touches:
            raise ValueError(f'Feature "{name}" touches nothing, so `features --changed` can never select it')
        self._subs: list[tuple[str, list[tuple[str, tuple[Surface, ...], list[ScenarioStep]]]]] = []

    def sub_feature(self, name: str) -> FeatureBuilder:
        self._subs.append((_slug("Sub-feature", name), []))
        return self

    def scenario(self, name: str, *, surfaces: Sequence[Surface] | None = None) -> FeatureBuilder:
        if not self._subs:
            raise ValueError(f'Scenario "{name}" needs a sub_feature() first')
        chosen = tuple(dict.fromkeys(surfaces)) if surfaces else self._surfaces
        outside = [surface for surface in chosen if surface not in self._surfaces]
        if outside:
            raise ValueError(f'Scenario "{name}" uses {", ".join(outside)}, which feature "{self._name}" does not list')
        self._subs[-1][1].append((_slug("Scenario", name), chosen, []))
        return self

    def _steps(self, what: str) -> list[ScenarioStep]:
        if not self._subs or not self._subs[-1][1]:
            raise ValueError(f"{what} needs a scenario() first")
        return self._subs[-1][1][-1][2]

    def flow(self, step: Flow) -> FeatureBuilder:
        self._steps(f'Flow "{step.id}"').append(FlowStep(step))
        return self

    def proof(self, *checks: ProofCheck) -> FeatureBuilder:
        self._steps("proof()").append(ProofStep(tuple(checks)))
        return self

    def build(self) -> Feature:
        if not self._subs:
            raise ValueError(f'Feature "{self._name}" has no sub-features')
        subs: list[SubFeature] = []
        seen_subs: set[str] = set()
        for sub_name, scenarios in self._subs:
            if sub_name in seen_subs:
                raise ValueError(f'Duplicate sub-feature "{self._name}.{sub_name}"')
            seen_subs.add(sub_name)
            if not scenarios:
                raise ValueError(f'Sub-feature "{self._name}.{sub_name}" has no scenarios')
            built: list[Scenario] = []
            seen: set[str] = set()
            for name, surfaces, steps in scenarios:
                scenario_id = f"{self._name}.{sub_name}.{name}"
                if name in seen:
                    raise ValueError(f'Duplicate scenario "{scenario_id}"')
                seen.add(name)
                built.append(_validated(Scenario(scenario_id, tuple(steps), surfaces)))
            subs.append(SubFeature(f"{self._name}.{sub_name}", tuple(built)))
        return Feature(self._name, tuple(subs), self._touches, self._surfaces)


def _validated(scenario: Scenario) -> Scenario:
    if not scenario.steps:
        raise ValueError(f'Scenario "{scenario.id}" has no steps')
    if not isinstance(scenario.steps[-1], ProofStep):
        raise ValueError(f'Scenario "{scenario.id}" must end with proof(): nothing after the last proof is observed')
    seen: set[str] = set()
    for step in scenario.steps:
        if not isinstance(step, ProofStep):
            continue
        if not step.checks:
            raise ValueError(f'Scenario "{scenario.id}" has a proof() with no checks')
        for check in step.checks:
            _slug("Check", check.id)
            if check.id in seen:
                raise ValueError(f'Scenario "{scenario.id}" repeats check "{check.id}"')
            seen.add(check.id)
            names = [adapter.name for adapter in check.evidence]
            if not names:
                raise ValueError(f'Check "{scenario.id}:{check.id}" declares no evidence: a check that proves nothing cannot pass')
            if len(set(names)) != len(names):
                raise ValueError(f'Check "{scenario.id}:{check.id}" declares the same evidence twice')
    return scenario


def feature(name: str, *, touches: Sequence[str], surfaces: Sequence[Surface]) -> FeatureBuilder:
    return FeatureBuilder(name, touches=touches, surfaces=surfaces)


def registry(*features: Feature, flows: Sequence[Flow] = ()) -> Registry:
    """The frozen registry the runner executes. Every flow a scenario uses is listed, so `flow <id>` can run it by hand."""
    by_name: dict[str, Feature] = {}
    for item in features:
        if item.id in by_name:
            raise ValueError(f'Duplicate feature "{item.id}"')
        by_name[item.id] = item
    known: dict[str, Flow] = {}
    for step in [*flows, *(used for item in features for scenario in item.scenarios for used in scenario.flows)]:
        if step.id in known and known[step.id] != step:
            raise ValueError(f'Two different flows share the id "{step.id}"')
        known[step.id] = step
    return Registry(by_name, known)
