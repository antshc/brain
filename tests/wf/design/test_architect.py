from pathlib import Path


ROOT = Path(__file__).resolve().parents[3] / "plugins/wf/skills"
DESIGN = ROOT / "design"
FACTORY = Path(__file__).resolve().parents[3] / "plugins/wf/install/assets/factory-mode"


def test_architect_checkpoint_is_opt_in_and_implementation_is_default():
    skill = (DESIGN / "SKILL.md").read_text()
    design = (DESIGN / "playbooks/architect.md").read_text()

    assert "checkpoint" in skill
    assert "**Default: no checkpoint.** Continue to Phase E automatically" in design
    assert "design-only handoff" in design
    assert "continue to Phase D instead" in design
    assert "**Checkpoint requested by the user:**" in design
    assert "stop and wait for the user" in design


def test_evidence_corrections_do_not_require_approval_without_checkpoint():
    evidence = (DESIGN / "references/evidence-routing.md").read_text()

    assert "without checkpoint" in evidence.lower()
    assert "with checkpoint" in evidence.lower()
    assert "review-log.md" in evidence


def test_factory_uses_one_autonomous_feature_flow_and_optional_checkpoint():
    playbook = (FACTORY / "playbooks/feature.md").read_text()
    skill = (FACTORY / "SKILL.md").read_text()
    help_text = (FACTORY / "help.md").read_text()

    assert "## Interactive" not in playbook
    assert "## Auto" not in playbook
    assert "Select mode" not in playbook
    assert "arena-agents=1" in playbook
    assert "`challenge-this` with `adversaries=3`" in playbook
    assert "design-only handoff" in playbook
    assert "forward `checkpoint` only when the user explicitly asks" in playbook
    assert playbook.index('use `spec` mode') < playbook.index('`implement` skill')
    assert "Auto adds" not in skill
    assert "architect auto" not in help_text
    assert "architect` vs `architect auto" not in help_text
    assert "Auto Address/Diagnose" not in (FACTORY / "references/post-implementation.md").read_text()


def test_design_playbook_does_not_route_to_feature():
    playbook = (FACTORY / "playbooks/design.md").read_text()
    assert "`feature` playbook" not in playbook
    assert "`architect` playbook" not in playbook
    assert "Next:" not in playbook

    review = (ROOT / "review/playbooks/code.md").read_text()
    assert "Feature playbook" not in review
    assert "Architect playbook" not in review
    assert "Workflow invocation:" not in review

def test_removed_factory_playbooks_have_no_stale_links():
    skill = (FACTORY / "SKILL.md").read_text()
    help_text = (FACTORY / "help.md").read_text()

    for name in ("investigation", "prototype", "refactoring"):
        assert not (FACTORY / f"playbooks/{name}.md").exists()
        assert f"playbooks/{name}.md" not in skill

    assert "/factory-mode prototype" not in help_text
    assert " investigation      " not in help_text
    assert " refactoring        " not in help_text
