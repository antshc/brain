from pathlib import Path

import pytest


SKILLS = Path(__file__).resolve().parents[3] / "plugins/wf/skills"
ROOT = SKILLS / "write"


@pytest.mark.parametrize("route", ["spec", "hld", "toi", "research", "bottom-line", "root-cause", "doc"])
def test_routes_disclose_their_procedure_and_template(route):
    entry = (ROOT / "SKILL.md").read_text()
    assert f"](playbooks/{route}.md)" in entry
    assert f"](templates/{route}-template.md)" in entry
    assert (ROOT / f"playbooks/{route}.md").is_file()
    assert (ROOT / f"templates/{route}-template.md").is_file()


def test_retired_document_resources_stay_removed():
    assert not (ROOT / "playbooks/handover.md").exists()
    assert not (ROOT / "playbooks/documentation.md").exists()


def test_document_normalization_is_local_and_preserves_implemented_behavior():
    entry = (ROOT / "references/artifacts.md").read_text()
    requirements = (ROOT / "references/requirements.md").read_text()
    writing = (ROOT / "SKILL.md").read_text()
    assert "`spec normalize`" in writing
    assert not (SKILLS / "write/references/solution-agnostic.md").exists()
    assert not (SKILLS / "write/references/solution-agnostic-terms.md").exists()
    assert "normalize" not in writing.split("argument-hint", 1)[0].lower()
    assert "`write normalize`" in entry
    assert "`spec normalize`" in entry
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
        assert "`write` skill" in (design / f"playbooks/{route}.md").read_text()
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
    assert "disable-model-invocation" not in entry.split("---", 2)[1]
    assert "Bottom line procedure" in research
    assert "do not recursively invoke this skill" in research
    assert "Report language" in research
    assert "| Document | `bottom-line` | A standalone conclusion" in entry
    assert not (SKILLS / "write/references/bottom-line.md").exists()
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
    assert "canonical URL" in template and "[REDACTED]" in template
    assert "`write` skill to write root-cause reports" in diagnostic
    assert not (SKILLS / "diagnosing-bugs/references/root-cause-report.md").exists()


def test_investigation_supplies_evidence_and_retains_delivery():
    router = (SKILLS / "research/SKILL.md").read_text()
    living = (SKILLS / "research/wayfinder/living-document.md").read_text()
    assert "`write` skill to write research reports" in router
    assert "Only the router writes reports" in router
    assert "Explore stays inline and bypasses report rendering" in router
    assert "`research update`" in living
    assert "`write` skill" in living
