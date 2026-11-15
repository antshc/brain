from __future__ import annotations

from pathlib import Path

import pytest

from lint_skill_descriptions import Skill, lint, main, read_skill, redirect_targets, trigger_phrases


def skill(name: str, description: str) -> Skill:
    return Skill(Path(f"plugins/wf/skills/{name}/SKILL.md"), name, description)


def test_extracts_quoted_trigger_phrases() -> None:
    description = "Do it. Use for 'where is', \"what calls\", the user's thing."
    assert trigger_phrases(description) == ["where is", "what calls"]


def test_extracts_all_redirect_targets() -> None:
    description = "Do it. Not for docs → `a`; stories → `b`."
    assert redirect_targets(description) == ["a", "b"]


def test_ignores_arrows_before_not_for() -> None:
    assert redirect_targets("Maps x → `a`. Use for 'y'.") == []


def test_flags_exact_duplicate_trigger() -> None:
    errors = lint([skill("a", "Use for 'how does this work'."), skill("b", "Use for 'how does this work'.")], {"a", "b"})
    assert len(errors) == 1 and "duplicates" in errors[0]


def test_flags_near_duplicate_trigger() -> None:
    errors = lint(
        [skill("a", "Use for 'how does this work'."), skill("b", "Use for 'how does this code work'.")],
        {"a", "b"},
    )
    assert len(errors) == 1


def test_allows_distinct_triggers() -> None:
    assert lint([skill("a", "Use for 'where is'."), skill("b", "Use for 'research X'.")], {"a", "b"}) == []


def test_same_skill_phrases_are_not_compared() -> None:
    assert lint([skill("a", "Use for 'fetch a PR', 'fetch the PR'.")], {"a"}) == []


def test_flags_missing_redirect_target() -> None:
    errors = lint([skill("a", "Not for x → `missing`.")], {"a"})
    assert len(errors) == 1 and "missing" in errors[0]


def test_flags_self_redirect() -> None:
    errors = lint([skill("a", "Not for x → `a`.")], {"a"})
    assert len(errors) == 1 and "itself" in errors[0]


def test_accepts_redirect_to_known_skill_outside_checked_set() -> None:
    assert lint([skill("a", "Not for x → `elsewhere`.")], {"a", "elsewhere"}) == []


def test_flags_overlong_description() -> None:
    errors = lint([skill("a", "x" * 301)], {"a"})
    assert len(errors) == 1 and "301" in errors[0]


@pytest.mark.parametrize("front", ["", "---\nname: a\n---\n", "---\nname: [a]\ndescription: x\n---\n", "---\n[]\n---\n", "---\nname: a\ndescription: ' '\n---\n", "---\nname: [\n---\n"])
def test_invalid_frontmatter_is_reported(tmp_path: Path, front: str) -> None:
    doc = tmp_path / "SKILL.md"
    doc.write_text(front + "# Skill\n")
    with pytest.raises(ValueError, match="frontmatter"):
        read_skill(tmp_path, Path("SKILL.md"))


def test_valid_folded_description_is_normalized(tmp_path: Path) -> None:
    (tmp_path / "SKILL.md").write_text("---\nname: a\ndescription: >-\n  First line.\n  Second line.\n---\n# A\n")
    assert read_skill(tmp_path, Path("SKILL.md")).description == "First line. Second line."


def test_main_reports_invalid_skill_without_stopping_other_checks(tmp_path: Path, monkeypatch, capsys) -> None:
    import lint_skill_descriptions as module
    root = tmp_path / "plugins/wf/skills"
    for name, front in [("invalid", ""), ("valid", "---\nname: valid\ndescription: Not for x → `missing`.\n---\n")]:
        folder = root / name
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text(front + "# Skill\n")
    monkeypatch.setattr(module, "tracked_skill_files", lambda repo: [file.relative_to(repo) for file in root.rglob("SKILL.md")])
    assert main(tmp_path) == 1
    errors = capsys.readouterr().err
    assert "frontmatter" in errors and "missing" in errors
