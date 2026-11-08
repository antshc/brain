from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
FACTORY = REPO / "skills/engineering/factory-mode"


def test_stories_is_factory_playbook_not_standalone_skill():
    assert not (REPO / "plugins/wf/skills/to-stories/SKILL.md").exists()
    playbook = FACTORY / "playbooks/stories.md"
    assert playbook.is_file()
    assert "[playbooks/stories.md](playbooks/stories.md)" in (FACTORY / "SKILL.md").read_text()
    assert "/factory-mode stories" in (FACTORY / "help.md").read_text()


def test_stories_preserves_approval_and_output_contract():
    text = (FACTORY / "playbooks/stories.md").read_text()
    assert text.index("**Propose breakdown**") < text.index("**Draft each body**")
    assert "wait for explicit approval" in text
    assert "exactly once per approved row" in text
    assert "`draft-artifact` skill" in text
    assert "**Jira ID:**" in text
    assert "**Epic ID:**" in text
    assert "**Blocked by:**" in text
    for field in ("Deployable kind", "Functional slice", "Business rules",
                  "Source Acceptance criteria", "Depends on"):
        assert field in text


def test_current_guidance_has_no_standalone_stories_invocation():
    for relative in (
        "README.md",
        "plugins/wf/README.md",
        "plugins/wf/skills/design/SKILL.md",
        "plugins/wf/skills/design/playbooks/spec.md",
        "plugins/skill/skills/doc-flow/references/subflow-template.md",
        "docs/plans/idea-to-implementation-flow.md",
    ):
        text = (REPO / relative).read_text()
        assert "/to-stories" not in text, relative
        assert "skills/to-stories/" not in text, relative
