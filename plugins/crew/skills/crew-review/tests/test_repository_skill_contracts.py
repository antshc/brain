from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
CREW = ROOT / "plugins" / "crew"


def test_review_requires_repository_local_chore_rules_skills_without_default_fallback():
    review = (CREW / "skills" / "crew-review" / "SKILL.md").read_text(encoding="utf-8")

    assert ".github/skills/chore-<stack>-rules/SKILL.md" in review
    assert "Chorey not configured" in review
    assert "Default review checklist" not in review
    assert "CHORE-<stack>.md" not in review


def test_initializer_offers_rules_skills_and_preserves_repository_rules_during_merge():
    initializer = (CREW / "skills" / "init-crew" / "SKILL.md").read_text(encoding="utf-8")

    assert "Present the available `chore-<stack>-rules` skills" in initializer
    assert "preserve all repository-authored wording and conflicting repository rules" in initializer
    assert "add only non-conflicting shipped rules" in initializer


def test_chorey_uses_gotchas_memory_and_handles_missing_rules_safely():
    chorey = (CREW / "agents" / "chorey.agent.md").read_text(encoding="utf-8")

    assert ".github/skills/gotchas-memory/GOTCHAS.md" in chorey
    assert "/gotchas-memory" in chorey
    assert "FILES: none — Chorey not configured" in chorey


def test_ralph_delegates_review_to_chorey_without_naming_its_internal_skill():
    ralph_dev = (ROOT / "plugins" / "ralph" / "skills" / "dev" / "SKILL.md").read_text(encoding="utf-8")

    assert "run the `chorey` agent" in ralph_dev
    assert "/crew-review" not in ralph_dev
