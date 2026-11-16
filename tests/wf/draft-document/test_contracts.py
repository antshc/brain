from pathlib import Path
import re

import pytest


SKILLS = Path(__file__).resolve().parents[3] / "plugins/wf/skills"
ROOT = SKILLS / "draft-document"


@pytest.mark.parametrize("route", ["spec", "hld", "toi"])
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
    assert {path.stem for path in (ROOT / "playbooks").glob("*.md")} == {"spec", "hld", "toi"}
    assert not (ROOT / "playbooks/handover.md").exists()


def test_document_normalization_is_local_and_preserves_implemented_behavior():
    entry = (ROOT / "SKILL.md").read_text()
    requirements = (ROOT / "references/requirements.md").read_text()
    writing = (SKILLS / "writing-style/SKILL.md").read_text()
    assert "`draft-document` skill" in writing
    assert "normalize" in writing
    assert not (SKILLS / "writing-style/references/solution-agnostic.md").exists()
    assert not (SKILLS / "writing-style/references/solution-agnostic-terms.md").exists()
    assert "normalize" not in entry.split("---", 2)[1].lower()
    assert "`draft-document normalize`" in entry
    assert "`spec normalize`" in entry
    assert "draft-work/" not in entry
    for phrase in ("verbatim", "structural relocation", "normalize"):
        assert phrase in entry
    for phrase in ("domain glossary", "Preserve the hierarchy", "TOI",
                   "implemented behavior", "HLD decisions", "Never invent"):
        assert phrase in requirements
    for route in ("spec", "hld", "toi"):
        assert "normalize" in (ROOT / f"playbooks/{route}.md").read_text()


def test_design_retains_risk_and_publication_control():
    design = SKILLS / "design"
    for route in ("spec", "hld"):
        assert "`draft-document` skill" in (design / f"playbooks/{route}.md").read_text()
    assert not (design / "templates/design-template.md").exists()
    hld = (design / "playbooks/hld.md").read_text()
    assert "Risk verification" in hld
    assert "publish-hld" in hld
    updates = (ROOT / "references/hld-updates.md").read_text()
    for phrase in ("Open Questions", "verbatim", "Idempotency", "Source Material"):
        assert phrase in updates
