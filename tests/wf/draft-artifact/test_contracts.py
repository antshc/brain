from pathlib import Path
import re

import pytest


SKILLS = Path(__file__).resolve().parents[3] / "plugins/wf/skills"
ROOT = SKILLS / "draft-artifact"


@pytest.mark.parametrize("route", ["story", "task", "bug", "spec", "hld", "toi"])
def test_routes_disclose_their_procedure_and_template(route):
    entry = (ROOT / "SKILL.md").read_text()
    assert f"](playbooks/{route}.md)" in entry
    assert f"](templates/{route}-template.md)" in entry
    assert (ROOT / f"playbooks/{route}.md").is_file()
    assert (ROOT / f"templates/{route}-template.md").is_file()


def test_all_authoring_resources_are_local_and_directly_disclosed():
    entry = (ROOT / "SKILL.md").read_text()
    linked = {target.split("#", 1)[0] for target in re.findall(r"\]\(([^)]+)\)", entry)}
    resources = {path.relative_to(ROOT).as_posix() for folder in ("playbooks", "references", "templates")
                 for path in (ROOT / folder).glob("*.md")}
    assert resources <= linked
    for path in (ROOT / "playbooks").glob("*.md"):
        assert not path.read_text().startswith("---")
    assert not (ROOT / "tactics").exists()


def test_normalization_ownership_and_protected_technical_sections():
    entry = (ROOT / "SKILL.md").read_text()
    writing = (SKILLS / "writing-style/SKILL.md").read_text()
    assert not (SKILLS / "writing-style/references/solution-agnostic.md").exists()
    assert not (SKILLS / "writing-style/references/solution-agnostic-terms.md").exists()
    assert "`draft-artifact` skill" in writing
    assert "normalize" in writing
    assert "normalize" not in entry.split("---", 2)[1].lower()
    for phrase in ("verbatim", "structural relocation", "reproduction", "normalize"):
        assert phrase in entry
    requirements = (ROOT / "references/requirements.md").read_text()
    assert "domain glossary" in requirements
    assert "Preserve the hierarchy" in requirements


def test_design_delegates_authoring_and_retains_risk_and_publication_control():
    design = SKILLS / "design"
    for route in ("spec", "hld", "tickets"):
        assert "`draft-artifact` skill" in (design / f"playbooks/{route}.md").read_text()
    assert not (design / "templates/design-template.md").exists()
    hld = (design / "playbooks/hld.md").read_text()
    assert "Risk verification" in hld
    assert "publish-hld" in hld
    updates = (ROOT / "references/hld-updates.md").read_text()
    for phrase in ("Open Questions", "verbatim", "Idempotency", "Source Material"):
        assert phrase in updates
