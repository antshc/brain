from pathlib import Path
import re

import pytest


SKILLS = Path(__file__).resolve().parents[3] / "plugins/wf/skills"
ROOT = SKILLS / "draft-work"


@pytest.mark.parametrize("route", ["story", "task", "bug"])
def test_routes_disclose_their_procedure_and_template(route):
    entry = (ROOT / "SKILL.md").read_text()
    assert f"](playbooks/{route}.md)" in entry
    assert f"](templates/{route}-template.md)" in entry
    assert (ROOT / f"playbooks/{route}.md").is_file()
    assert (ROOT / f"templates/{route}-template.md").is_file()


def test_authoring_resources_are_local_and_directly_disclosed():
    entry = (ROOT / "SKILL.md").read_text()
    linked = {target.split("#", 1)[0] for target in re.findall(r"\]\(([^)]+)\)", entry)}
    resources = {path.relative_to(ROOT).as_posix() for folder in ("playbooks", "references", "templates")
                 for path in (ROOT / folder).glob("*.md")}
    assert resources <= linked
    for target in linked:
        assert (ROOT / target).resolve().is_relative_to(ROOT.resolve())
        assert (ROOT / target).is_file()
    assert not (SKILLS / "draft-artifact").exists()
    assert {path.stem for path in (ROOT / "playbooks").glob("*.md")} == {"story", "task", "bug"}


def test_work_normalization_preserves_sources_and_technical_evidence():
    entry = (ROOT / "SKILL.md").read_text()
    requirements = (ROOT / "references/requirements.md").read_text()
    assert "normalize" not in entry.split("---", 2)[1].lower()
    for phrase in ("verbatim", "structural relocation", "reproduction", "normalize"):
        assert phrase in entry
    for phrase in ("story outcomes", "task acceptance criteria", "Bug expected behavior",
                   "domain glossary", "Preserve the hierarchy", "actual observations",
                   "Never invent"):
        assert phrase in requirements
    assert "draft-document/" not in entry
    for route in ("story", "task", "bug"):
        assert "normalize" in (ROOT / f"playbooks/{route}.md").read_text()


def test_design_and_implement_delegate_one_task_to_the_work_author():
    design = SKILLS / "design"
    assert "`draft-work` skill" in (design / "playbooks/tasks.md").read_text()
    assert "`draft-work` skill" in (SKILLS / "implement/references/breakdown.md").read_text()
