from __future__ import annotations

from pathlib import Path

from lint_skill_descriptions import Skill, lint, redirect_targets, trigger_phrases


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
