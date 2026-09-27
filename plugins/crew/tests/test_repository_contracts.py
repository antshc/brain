from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CREW = ROOT / "plugins" / "crew"


def test_chorey_owns_safe_review_and_revert_contract():
    chorey = (CREW / "agents" / "chorey.agent.md").read_text(encoding="utf-8")

    assert ".github/skills/chore-<stack>-rules/SKILL.md" in chorey
    assert "Chorey not configured" in chorey
    assert "provably behavior-preserving" in chorey
    assert "exact current content" in chorey
    assert "Restore every file REVIEW touched to its exact pre-review state" in chorey
    assert "/gotchas-memory" in chorey


def test_initializer_offers_rules_skills_and_preserves_repository_rules_during_merge():
    initializer = (CREW / "skills" / "init-crew" / "SKILL.md").read_text(encoding="utf-8")

    assert "Present the available `chore-<stack>-rules` skills" in initializer
    assert "preserve all repository-authored wording and conflicting repository rules" in initializer
    assert "add only non-conflicting shipped rules" in initializer


def test_ralph_delegates_review_to_chorey_without_naming_its_internals():
    ralph_dev = (ROOT / "plugins" / "ralph" / "skills" / "dev" / "SKILL.md").read_text(encoding="utf-8")

    assert "run the `chorey` agent" in ralph_dev


def test_removed_review_skill_has_no_live_references():
    removed_tokens = ("crew" + "-review", "match_changed_" + "files.py", "review_" + "scopes.json")
    source_suffixes = {".md", ".json", ".py"}

    for path in ROOT.rglob("*"):
        if path == Path(__file__) or not path.is_file() or path.suffix not in source_suffixes:
            continue
        text = path.read_text(encoding="utf-8")
        for token in removed_tokens:
            assert token not in text, f"{path.relative_to(ROOT)} still references {token}"
