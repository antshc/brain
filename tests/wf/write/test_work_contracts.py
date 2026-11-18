from pathlib import Path

import pytest


SKILLS = Path(__file__).resolve().parents[3] / "plugins/wf/skills"
ROOT = SKILLS / "write"


@pytest.mark.parametrize("route", ["story", "task", "bug"])
def test_routes_disclose_their_procedure_and_template(route):
    entry = (ROOT / "SKILL.md").read_text()
    assert f"](playbooks/{route}.md)" in entry
    assert f"](templates/{route}-template.md)" in entry
    assert (ROOT / f"playbooks/{route}.md").is_file()
    assert (ROOT / f"templates/{route}-template.md").is_file()


def test_work_normalization_preserves_sources_and_technical_evidence():
    entry = (ROOT / "references/artifacts.md").read_text()
    requirements = (ROOT / "references/requirements.md").read_text()
    assert "normalize" not in (ROOT / "SKILL.md").read_text().split("argument-hint", 1)[0].lower()
    for phrase in ("verbatim", "structural relocation", "reproduction", "normalize"):
        assert phrase in entry
    for phrase in ("story outcomes", "task acceptance criteria", "Bug expected behavior",
                   "domain glossary", "Preserve the hierarchy", "actual observations",
                   "Never invent"):
        assert phrase in requirements
    for route in ("story", "task", "bug"):
        assert "normalize" in (ROOT / f"playbooks/{route}.md").read_text()


def test_design_and_implement_delegate_one_task_to_the_work_author():
    design = SKILLS / "design"
    assert "`write` skill" in (design / "playbooks/tasks.md").read_text()
    assert "`write` skill" in (SKILLS / "implement/references/breakdown.md").read_text()
