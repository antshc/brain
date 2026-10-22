"""Proof kit independence tests (init-verify templates, both languages).

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

TEMPLATES = Path(__file__).resolve().parents[3] / "plugins" / "verify" / "skills" / "init-verify" / "templates"
KITS = {"typescript": ("kit", "*.ts"), "python": ("kit", "*.py")}
LEAVES_THE_KIT = {
    "typescript": re.compile(r"""from\s+["'](?!\./)"""),
    "python": re.compile(r"^\s*(?:from\s+(?:\.\.|mole|proof)|import\s+(?:mole|proof))", re.M),
}
RUNNER_TEXT = re.compile(r"pnpm (?:mole|prove)|python3 -m (?:mole|proof)|\bMOLE\b|mole doctor")


def kit_files(language: str) -> list[Path]:
    folder, pattern = KITS[language]
    return sorted((TEMPLATES / language / folder).glob(pattern))


def mole_files(language: str) -> list[Path]:
    return sorted((TEMPLATES / language / "mole").glob(KITS[language][1]))


@pytest.mark.parametrize("language", ["typescript", "python"])
class TestProofKitIndependence:
    """Feature: Proof Kit Independence"""

    def test_kit_imports_only_its_own_files(self, language: str) -> None:
        # Scenario: Kit imports only its own files
        files = kit_files(language)
        assert files
        for path in files:
            if language == "typescript":
                imports = [line for line in path.read_text().splitlines() if re.match(r"\s*(import|export)\b.*\bfrom\b", line)]
                outside = [line for line in imports if LEAVES_THE_KIT[language].search(line) and "@playwright/test" not in line and "node:" not in line]
                assert not outside, f"{path.name} imports outside the kit: {outside}"
            else:
                assert not LEAVES_THE_KIT[language].search(path.read_text()), f"{path.name} imports outside the kit"

    def test_kit_names_no_runner_command(self, language: str) -> None:
        # Scenario: Kit names no runner command
        for path in kit_files(language):
            assert not RUNNER_TEXT.search(path.read_text()), f"{path.name} mentions the runner"

    def test_mole_uses_the_kit(self, language: str) -> None:
        # Scenario: Mole uses the kit
        text = "".join(path.read_text() for path in mole_files(language))
        assert "proof/kit" in text or "proof.kit" in text
