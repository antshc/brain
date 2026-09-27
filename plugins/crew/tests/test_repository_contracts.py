from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CREW = ROOT / "plugins" / "crew"


def test_chorey_owns_safe_review_and_revert_contract():
    chorey = (CREW / "agents" / "chorey.agent.md").read_text(encoding="utf-8")

    assert "HARNESS_REPO_PATH" not in chorey
    assert "GOTCHAS_PATH" not in chorey
    assert chorey.index("### 2. Check Chore rules") < chorey.index("### 4. Review and clean up")
    assert "No confident match or any missing applicable skill makes the review `skipped`" in chorey
    assert "STATUS: complete | skipped" in chorey
    assert "provably behavior-preserving" in chorey
    assert "exact current content" in chorey
    assert "Restore every file REVIEW touched to its exact pre-review state" in chorey
    assert "/gotchas-memory" in chorey
    assert "When the skill is unavailable, perform no gotchas work" in chorey
    for field in ("STATUS:", "SUMMARY:", "FILES:", "GOTCHAS UPDATED:", "NOTES:"):
        assert field in chorey


def test_crew_agents_use_direct_skills_without_manual_path_discovery():
    standalone = (CREW / "skills" / "to-chorey" / "SKILL.md").read_text(encoding="utf-8")
    to_codey = (CREW / "skills" / "to-codey" / "SKILL.md").read_text(encoding="utf-8")
    chorey = (CREW / "agents" / "chorey.agent.md").read_text(encoding="utf-8")
    codey_agents = [
        path.read_text(encoding="utf-8") for path in (CREW / "agents").glob("codey-*.agent.md")
    ]
    ralph_dev = (ROOT / "plugins" / "ralph" / "skills" / "dev" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    codey_invocation = ralph_dev.split("## 3. Invoke implementation agent", 1)[1].split(
        "## 4. Distill", 1
    )[0]
    chorey_invocation = ralph_dev.split("## 6. Review (Chorey)", 1)[1].split(
        "## 7. Commit & push Chorey's cleanup", 1
    )[0]

    for text in [standalone, to_codey, codey_invocation, chorey_invocation, chorey, *codey_agents]:
        assert "## HARNESS" not in text
        assert "HARNESS_REPO_PATH" not in text
        assert "GOTCHAS_PATH" not in text
        assert ".github/instructions" not in text
    assert "resolve-harness" not in standalone
    assert "resolve-harness" not in to_codey
    assert all("/gotchas-memory" in agent for agent in codey_agents)
    assert "## BASELINE_COMMIT" in chorey_invocation


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
