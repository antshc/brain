from pathlib import Path


ROOT = Path(__file__).resolve().parents[3] / "plugins/wf/skills"
ARCHITECT = ROOT / "architect"
FACTORY = ROOT / "factory-mode"


def test_architect_checkpoint_is_opt_in_and_implementation_is_default():
    skill = (ARCHITECT / "SKILL.md").read_text()
    design = (ARCHITECT / "design/design.md").read_text()

    assert "checkpoint" in skill
    assert "**Default: no checkpoint.** Continue to Phase E automatically" in design
    assert "design-only handoff" in design
    assert "continue to Phase D instead" in design
    assert "**Checkpoint requested by the user:**" in design
    assert "stop and wait for the user" in design


def test_evidence_corrections_do_not_require_approval_without_checkpoint():
    evidence = (ARCHITECT / "design/evidence-routing.md").read_text()

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
    assert "arena-agents=3" in playbook
    assert "design-only handoff" in playbook
    assert "forward `checkpoint` only when the user explicitly asks" in playbook
    assert playbook.index('`to-spec` skill') < playbook.index('`implement-spec` skill')
    assert "Auto adds" not in skill
    assert "architect auto" not in help_text
    assert "architect` vs `architect auto" not in help_text
    assert "Auto Address/Diagnose" not in (FACTORY / "references/post-implementation.md").read_text()


def test_other_playbooks_do_not_route_to_feature():
    for name in ("design", "prototype", "investigation", "refactoring"):
        playbook = (FACTORY / f"playbooks/{name}.md").read_text()
        assert "`feature` playbook" not in playbook
        assert "`architect` playbook" not in playbook
    assert "Next:" not in (FACTORY / "playbooks/design.md").read_text()
    assert "Hand the chosen direction" not in (FACTORY / "playbooks/prototype.md").read_text()
    assert "re-route" not in (FACTORY / "playbooks/investigation.md").read_text()
    assert "route to the" not in (FACTORY / "playbooks/refactoring.md").read_text()

    review = (ROOT.parents[1] / "review/skills/code-review/SKILL.md").read_text()
    assert "Feature playbook" not in review
    assert "Architect playbook" not in review
    assert "Workflow invocation:" not in review
