"""Keeps the registry, the feature maps and the app config in step. Run with: python3 -m pytest proof/test_features.py

Add your own adapter tests to proof/test_features.py; this file belongs to the mole and is replaced on upgrade.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, cast

import pytest
from playwright.sync_api import Page

from proof.app import APP
from proof.features import REGISTRY
from proof.kit import (
    ALL_SURFACES, Assessment, Flow, FlowContext, FlowStep, ProofCheck, ProofStep, Scenario, features_for, run_steps, select_scenarios, selectable_ids,
)

from .commands import COMMANDS, MOLE
from .runtime import ROOT, SURFACES

FEATURES = REGISTRY.features
NAMES = list(FEATURES)
SCENARIOS = list(REGISTRY.scenarios.values())
MAPS = ROOT / APP.feature_maps
BANNED = [re.compile(pattern) for pattern in (r"localStorage", r"querySelector", r"page\.locator", r"getByRole", r"get_by_role", r"\w\(\)", r"\*\*Evidence\*\*")] + list(APP.map_banned)
SECTIONS = ("Sub-features", "How to get to it (user POV)", "Driving it with Mole", "Gotchas")
LINE = re.compile(r"^\*{0,2}\((?P<sub>[a-z0-9-]+) \| (?P<scenario>[a-z0-9-]+)\):\*{0,2} (?P<body>.*)$")

MAP_FILES = sorted(file.name for file in MAPS.glob("*.md") if file.name != "README.md")
INDEX = (MAPS / "README.md").read_text()


def scenario_lines(name: str) -> dict[str, str]:
    lines: dict[str, str] = {}
    for line in (MAPS / f"{name}.md").read_text().splitlines():
        match = LINE.match(line)
        if match:
            lines[f"{name}.{match['sub']}.{match['scenario']}"] = match["body"]
    return lines


def proof_evidence(body: str) -> list[str]:
    """The evidence labels a map names after **Proof**, one group per check, in order."""
    return re.findall(r"\(([^()]*)\)", body.split("**Proof**", 1)[1])


def test_app_config_names_a_supported_set_of_surfaces() -> None:
    assert SURFACES, "APP.surfaces is empty"
    for surface in SURFACES:
        assert surface in ALL_SURFACES, f'APP.surfaces has the unknown surface "{surface}"'
    assert APP.source_paths, "APP.source_paths is empty: the revision would cover the whole repo"


def test_every_feature_has_a_map_and_every_map_has_a_feature() -> None:
    assert sorted(file.removesuffix(".md") for file in MAP_FILES) == sorted(FEATURES)


def test_a_feature_name_is_a_plain_word_that_no_built_in_command_already_uses() -> None:
    for name in NAMES:
        assert re.fullmatch(r"[a-z][a-z0-9-]*", name), f'"{name}" must be lowercase words joined by hyphens'
        assert name not in COMMANDS, f'"{name}" is a built-in mole command'


@pytest.mark.parametrize("name", NAMES)
def test_the_feature_only_uses_surfaces_this_repo_supports(name: str) -> None:
    feature = FEATURES[name]
    assert feature.surfaces, f"{name} has no surfaces"
    for surface in feature.surfaces:
        assert surface in SURFACES, f"{name} uses {surface}, which APP.surfaces does not list"
    assert feature.touches, f"{name} touches nothing, so `features --changed` can never select it"


@pytest.mark.parametrize("name", NAMES)
def test_the_map_has_its_four_sections_and_a_line_per_sub_feature(name: str) -> None:
    text = (MAPS / f"{name}.md").read_text()
    assert not text.startswith("---"), f"{name}.md has frontmatter: the registry is the source of truth, not the map"
    for section in SECTIONS:
        assert len(re.findall(rf"^## {re.escape(section)}$", text, re.M)) == 1, f'{name}.md needs exactly one "{section}" section'
    for sub in FEATURES[name].sub_features:
        bare = sub.id.split(".", 1)[1]
        assert re.search(rf"^- (?:\*\*)?{re.escape(bare)}\b", text, re.M), f"{name}.md does not list the sub-feature {bare}"


@pytest.mark.parametrize("name", NAMES)
def test_the_map_describes_exactly_the_scenarios_the_feature_registers(name: str) -> None:
    assert sorted(scenario_lines(name)) == sorted(scenario.id for scenario in FEATURES[name].scenarios)


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda scenario: scenario.id)
def test_the_map_line_states_given_when_then_and_proof(scenario: Scenario) -> None:
    body = scenario_lines(scenario.feature)[scenario.id]
    positions = [body.find(f"**{word}**") for word in ("Given", "When", "Then", "Proof")]
    assert all(position >= 0 for position in positions) and positions == sorted(positions), f"{scenario.id} needs Given, When, Then, Proof in that order"
    assert "|" not in body, f"{scenario.id} has a pipe in its text"


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda scenario: scenario.id)
def test_the_map_names_the_evidence_of_each_check_as_the_registry_declares_it(scenario: Scenario) -> None:
    declared = [" + ".join(adapter.label for adapter in check.evidence) for check in scenario.checks]
    assert proof_evidence(scenario_lines(scenario.feature)[scenario.id]) == declared


@pytest.mark.parametrize("name", NAMES)
def test_the_map_states_behavior_not_selectors_routes_or_wire_details(name: str) -> None:
    text = (MAPS / f"{name}.md").read_text()
    for banned in BANNED:
        assert not banned.search(text), f"{name}.md mentions {banned.pattern}: that belongs in a page, component or flow"


@pytest.mark.parametrize("name", NAMES)
def test_the_feature_map_index_links_its_map_and_its_run_command(name: str) -> None:
    assert f"({name}.md)" in INDEX, f"features/README.md does not link {name}.md"
    assert f"{MOLE} run {name}" in INDEX, f"features/README.md does not show the run command for {name}"


def test_changed_files_select_the_features_they_touch() -> None:
    for name, feature in FEATURES.items():
        assert name in features_for(REGISTRY, [f"{feature.touches[0]}x.file"])
    assert features_for(REGISTRY, ["no/such/place.txt"]) == []


def test_scenarios_are_selected_by_feature_sub_feature_or_scenario_and_no_id_means_all() -> None:
    assert [scenario.id for scenario in select_scenarios(REGISTRY)] == [scenario.id for scenario in SCENARIOS]
    for selected in selectable_ids(REGISTRY):
        assert select_scenarios(REGISTRY, [selected]), f"{selected} selects nothing"
    assert [scenario.id for scenario in select_scenarios(REGISTRY, [SCENARIOS[0].id])] == [SCENARIOS[0].id]


def test_an_unknown_id_is_refused_with_the_valid_ids() -> None:
    with pytest.raises(ValueError, match="Unknown id") as refused:
        select_scenarios(REGISTRY, ["no-such-id"])
    assert SCENARIOS[0].id in str(refused.value)


def test_every_flow_a_scenario_uses_can_be_run_by_hand_from_the_same_object() -> None:
    for scenario in SCENARIOS:
        for flow in scenario.flows:
            assert REGISTRY.flows[flow.id] is flow


# The unit tests below run the kit's step runner with a stub page: no browser, only the rules a receipt must keep.
class _Evidence:
    label = "stub"
    suffix = ".json"

    def __init__(self, name: str, *, fails: bool = False) -> None:
        self.name = name
        self.fails = fails

    def capture(self, context: FlowContext) -> Any:
        if self.fails:
            raise OSError("the source went away")
        return {"seen": True}


def _context() -> FlowContext:
    return FlowContext(page=cast(Page, None), app_url="http://app", api_url=None, fetch=cast(Any, None))


def _scenario(*steps: FlowStep | ProofStep) -> Scenario:
    return Scenario("demo.sub.one", tuple(steps), ("web",))


def _check(evidence: tuple[_Evidence, ...], passed: bool = True) -> ProofCheck:
    return ProofCheck("fact", evidence, lambda _: Assessment(passed, "expected", "actual"))


def test_a_check_without_evidence_gives_error_never_pass(tmp_path: Path) -> None:
    receipt = run_steps(_scenario(ProofStep((_check(()),))), _context(), directory=tmp_path)
    assert receipt.verdict == "ERROR"


def test_a_check_whose_evidence_cannot_be_captured_gives_error_and_keeps_the_failure(tmp_path: Path) -> None:
    receipt = run_steps(_scenario(ProofStep((_check((_Evidence("log", fails=True),)),))), _context(), directory=tmp_path)
    assert receipt.verdict == "ERROR"
    assert list(tmp_path.glob("*/log.error.json"))


def test_a_failing_check_keeps_its_evidence_and_later_steps_are_not_reached(tmp_path: Path) -> None:
    flow = Flow("demo.act", lambda _: None)
    receipt = run_steps(
        _scenario(ProofStep((_check((_Evidence("log"),), passed=False),)), FlowStep(flow), ProofStep((_check((_Evidence("log"),)),))),
        _context(), directory=tmp_path,
    )
    assert receipt.verdict == "FAIL"
    assert list(tmp_path.glob("*/log.json"))
    assert [entry.status for entry in receipt.trace] == ["failed", "not_reached", "not_reached"]


def test_a_source_that_changes_while_running_gives_a_stale_error(tmp_path: Path) -> None:
    revisions = iter(["one", "two", "two"])
    flow = Flow("demo.act", lambda _: None)
    receipt = run_steps(
        _scenario(FlowStep(flow), ProofStep((_check((_Evidence("log"),)),))), _context(), directory=tmp_path, revision=lambda: next(revisions),
    )
    assert receipt.verdict == "ERROR"
    assert receipt.error and "changed while running" in receipt.error
    assert receipt.trace[-1].status == "not_reached"


def test_a_passing_check_cites_its_own_evidence_on_disk(tmp_path: Path) -> None:
    receipt = run_steps(_scenario(ProofStep((_check((_Evidence("log"),)),))), _context(), directory=tmp_path)
    assert receipt.verdict == "PASS"
    assert [(tmp_path / reference.artifact).is_file() for reference in receipt.results[0].evidence] == [True]
