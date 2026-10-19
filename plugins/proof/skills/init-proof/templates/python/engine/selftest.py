"""Keeps the registry, the feature maps and the app config in step. Run with: python3 -m pytest proof/test_features.py

Add your own adapter tests to proof/test_features.py; this file is the engine's and is replaced on upgrade.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from ..app import APP
from .commands import COMMANDS, MOLE
from .model import ALL_SURFACES
from .registry import FEATURES, feature_names, features_for, select_features, surfaces_for
from .runtime import ROOT
from .surfaces import SURFACES, select_surfaces

MAPS = ROOT / APP.feature_maps
BANNED = [re.compile(pattern) for pattern in (r"localStorage", r"querySelector", r"page\.locator", r"getByRole", r"get_by_role")] + list(APP.map_banned)


def frontmatter(file: str) -> dict[str, str | list[str]]:
    """The frontmatter of a map: `key: value` lines, and `key:` followed by `  - item` lines."""
    match = re.match(r"^---\r?\n(.*?)\r?\n---", (MAPS / file).read_text(), re.S)
    assert match, f"{file} has no frontmatter"
    data: dict[str, str | list[str]] = {}
    items: list[str] | None = None
    for line in match.group(1).splitlines():
        item = re.match(r"^\s+-\s+(.*)$", line)
        if item and items is not None:
            items.append(item.group(1).strip())
            continue
        pair = re.match(r"^(\w+):\s*(.*)$", line)
        if not pair:
            continue
        if pair.group(2):
            data[pair.group(1)] = pair.group(2).strip()
            items = None
        else:
            items = data[pair.group(1)] = []
    return data


MAP_FILES = sorted(file.name for file in MAPS.glob("*.md") if file.name != "README.md")
INDEX = (MAPS / "README.md").read_text()


def test_app_config_names_a_supported_set_of_surfaces() -> None:
    assert SURFACES, "APP.surfaces is empty"
    for surface in SURFACES:
        assert surface in ALL_SURFACES, f'APP.surfaces has the unknown surface "{surface}"'
    assert APP.source_paths, "APP.source_paths is empty: the revision would cover the whole repo"


def test_every_feature_has_a_map_and_every_map_has_a_feature() -> None:
    assert sorted(file.removesuffix(".md") for file in MAP_FILES) == sorted(FEATURES)


def test_a_feature_name_is_a_plain_word_that_no_built_in_command_already_uses() -> None:
    for name in feature_names():
        assert re.fullmatch(r"[a-z][a-z0-9-]*", name), f'"{name}" must be lowercase words joined by hyphens'
        assert name not in COMMANDS, f'"{name}" is a built-in mole command'


@pytest.mark.parametrize("name", feature_names())
def test_the_map_names_its_feature_files_surfaces_and_proof_command(name: str) -> None:
    data = frontmatter(f"{name}.md")
    assert data["feature"] == name
    assert data["prove"] == f"{MOLE} prove --feature {name}"
    assert data["touches"] == FEATURES[name].touches
    assert data["surfaces"] == FEATURES[name].surfaces


@pytest.mark.parametrize("name", feature_names())
def test_the_feature_only_uses_surfaces_this_repo_supports(name: str) -> None:
    feature = FEATURES[name]
    assert feature.surfaces, f"{name} has no surfaces"
    for surface in feature.surfaces:
        assert surface in SURFACES, f"{name} uses {surface}, which APP.surfaces does not list"
    assert feature.touches, f"{name} touches nothing, so `features --changed` can never select it"


@pytest.mark.parametrize("name", feature_names())
def test_the_map_states_a_contract_not_selectors_routes_or_wire_details(name: str) -> None:
    text = (MAPS / f"{name}.md").read_text()
    for banned in BANNED:
        assert not banned.search(text), f"{name}.md mentions {banned.pattern}: that belongs in the surface adapter"
    assert re.search(r"^## Contract$", text, re.M), f"{name}.md has no Contract section"
    assert len(re.findall(r"^## Driving it$", text, re.M)) == 1, f'{name}.md needs exactly one "Driving it" block'


@pytest.mark.parametrize("name", feature_names())
def test_the_feature_map_index_links_its_map_and_its_proof_command(name: str) -> None:
    assert f"({name}.md)" in INDEX, f"features/README.md does not link {name}.md"
    assert f"{MOLE} prove --feature {name}" in INDEX, f"features/README.md does not show the proof command for {name}"


def test_changed_files_select_the_features_they_touch() -> None:
    for name, feature in FEATURES.items():
        assert name in features_for([f"{feature.touches[0]}x.file"])
    assert features_for(["no/such/place.txt"]) == []


def test_an_unknown_feature_is_refused_and_no_names_means_all() -> None:
    with pytest.raises(ValueError, match='Unknown feature "no-such-feature"'):
        select_features(["no-such-feature"])
    assert select_features() == feature_names()


def test_surface_is_validated_against_the_surfaces_a_feature_has() -> None:
    with pytest.raises(ValueError, match='Unknown surface "ftp"'):
        surfaces_for(feature_names(), ["ftp"])
    assert select_surfaces([], ["web"]) == ["web"]
    with pytest.raises(ValueError, match='no "api" surface'):
        select_surfaces(["api"], ["web"])
