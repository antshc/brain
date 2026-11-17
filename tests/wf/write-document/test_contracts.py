from pathlib import Path
import re

import pytest


SKILLS = Path(__file__).resolve().parents[3] / "plugins/wf/skills"
ROOT = SKILLS / "write-document"


@pytest.mark.parametrize("route", ["spec", "hld", "toi", "research", "bottom-line", "root-cause"])
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
    assert {path.stem for path in (ROOT / "playbooks").glob("*.md")} == {"spec", "hld", "toi", "research", "bottom-line", "root-cause"}
    assert not (ROOT / "playbooks/handover.md").exists()


def test_document_normalization_is_local_and_preserves_implemented_behavior():
    entry = (ROOT / "SKILL.md").read_text()
    requirements = (ROOT / "references/requirements.md").read_text()
    writing = (SKILLS / "writing/SKILL.md").read_text()
    assert "`write-document` skill" in writing
    assert "normalize" in writing
    assert not (SKILLS / "writing/references/solution-agnostic.md").exists()
    assert not (SKILLS / "writing/references/solution-agnostic-terms.md").exists()
    assert "normalize" not in entry.split("---", 2)[1].lower()
    assert "`write-document normalize`" in entry
    assert "`spec normalize`" in entry
    assert "write-work/" not in entry
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
        assert "`write-document` skill" in (design / f"playbooks/{route}.md").read_text()
    assert not (design / "templates/design-template.md").exists()
    hld = (design / "playbooks/hld.md").read_text()
    assert "Risk verification" in hld
    assert "publish-hld" in hld
    updates = (ROOT / "references/hld-updates.md").read_text()
    for phrase in ("Open Questions", "verbatim", "Idempotency", "Source Material"):
        assert phrase in updates


def test_report_ownership_and_bottom_line_reuse():
    entry = (ROOT / "SKILL.md").read_text()
    research = (ROOT / "playbooks/research.md").read_text()
    writing = (SKILLS / "writing/SKILL.md").read_text()
    assert "disable-model-invocation" not in entry.split("---", 2)[1]
    assert "Bottom line procedure" in research
    assert "do not recursively invoke this skill" in research
    assert "Report language" in research
    assert "`bottom-line` for a standalone conclusion" in writing
    assert not (SKILLS / "writing/references/bottom-line.md").exists()
    assert not (SKILLS.parent.parent.parent / "skills/engineering/bottom-line").exists()
    template = (ROOT / "templates/research-template.md").read_text()
    for heading in ("Bottom line", "What we did", "Open questions / decisions",
                    "Remaining work", "Next steps", "References"):
        assert f"## {heading}" in template
    bottom = (ROOT / "playbooks/bottom-line.md").read_text()
    for phrase in ("What did we find?", "So what?", "Now what?", "**Not confirmed**"):
        assert phrase in bottom
    assert "additional sections" in research
    assert "source coverage" in research


def test_root_cause_requires_confirmed_evidence_and_stays_print_only():
    procedure = (ROOT / "playbooks/root-cause.md").read_text()
    template = (ROOT / "templates/root-cause-template.md").read_text()
    diagnostic = (SKILLS / "diagnosing-bugs/SKILL.md").read_text()
    assert "At least one supplied hypothesis MUST be `confirmed`" in procedure
    assert "If none is confirmed, stop" in procedure
    assert "MUST NOT save the rendered summary to a file" in procedure
    assert "hypothesis log remains unchanged" in procedure
    assert "Run no probes" in procedure or "run no probes" in procedure
    assert "Every mechanism claim MUST cite re-checkable evidence" in template
    assert "canonical URL" in template and "<REDACTED>" in template
    assert "`write-document` skill to write root-cause reports" in diagnostic
    assert not (SKILLS / "diagnosing-bugs/references/root-cause-report.md").exists()


def test_investigation_supplies_evidence_and_retains_delivery():
    router = (SKILLS / "research/SKILL.md").read_text()
    living = (SKILLS / "research/wayfinder/living-document.md").read_text()
    assert "`write-document` skill to write research reports" in router
    assert "Only the router writes reports" in router
    assert "Explore stays inline and bypasses report rendering" in router
    assert "`research update`" in living
    assert "`write-document` skill" in living
    assert "`writing` skill" not in living
