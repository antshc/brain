"""Unit tests for skill-invocation resolution.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from modules.repo_consistency.skill_invocations import find_dangling_skill_invocations


def _write_skill(root: Path, plugin: str, name: str, body: str) -> None:
    skill_dir = root / "plugins" / plugin / "skills" / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: test skill.\n---\n\n{body}\n", encoding="utf-8"
    )


class TestSkillInvocationResolution:
    """Feature: Skill Invocation Resolution"""

    def test_skill_invocation_naming_an_existing_skill_is_not_reported(self, tmp_path):
        # Scenario: Skill invocation naming an existing skill is not reported
        _write_skill(tmp_path, "demo", "target", "# Target\nDoes things.")
        _write_skill(tmp_path, "demo", "caller", "Run `/target` skill.")

        violations = find_dangling_skill_invocations(tmp_path)

        assert violations == []

    def test_skill_invocation_naming_a_nonexistent_skill_is_reported(self, tmp_path):
        # Scenario: Skill invocation naming a nonexistent skill is reported
        _write_skill(tmp_path, "demo", "caller", "Run `/ghost-skill` skill.")

        violations = find_dangling_skill_invocations(tmp_path)

        assert len(violations) == 1
        assert violations[0].file.endswith("caller/SKILL.md")
        assert "ghost-skill" in violations[0].message

    def test_skill_invocation_naming_a_generated_skill_template_is_not_reported(self, tmp_path):
        # Scenario: Skill invocation naming a generated skill template is not reported
        _write_skill(tmp_path, "demo", "caller", "Run `/generated` skill.")
        template = tmp_path / "plugins/demo/skills/caller/adapter.SKILL.template.md"
        template.write_text("---\nname: generated\ndescription: generated skill.\n---\n", encoding="utf-8")

        assert find_dangling_skill_invocations(tmp_path) == []

    def test_template_body_text_does_not_declare_a_generated_skill(self, tmp_path):
        # Scenario: Template body text does not declare a generated skill
        _write_skill(tmp_path, "demo", "caller", "Run `/ghost` skill.")
        template = tmp_path / "plugins/demo/skills/caller/ghost.SKILL.template.md"
        template.write_text("# Sketch\nname: ghost\n", encoding="utf-8")

        violations = find_dangling_skill_invocations(tmp_path)

        assert len(violations) == 1
        assert "ghost" in violations[0].message

    def test_backticked_filesystem_paths_are_not_skill_invocations(self, tmp_path):
        # Scenario: Backticked filesystem paths are not skill invocations
        _write_skill(
            tmp_path,
            "demo",
            "caller",
            "Never root a command at `/usr`, `/opt`, `/etc`, or `/home`.",
        )

        violations = find_dangling_skill_invocations(tmp_path)

        assert violations == []


class TestRepositorySkillInvocationConsistency:
    """Feature: Skill Invocation Resolution"""

    def test_current_repository_has_no_dangling_skill_invocations(self, repo_root):
        # Scenario: Current repository has no dangling skill invocations
        violations = find_dangling_skill_invocations(repo_root)

        assert violations == [], "\n".join(str(v) for v in violations)


class TestWfSkillInvocationLoading:
    """Feature: WF Skill Invocation Loading"""

    @pytest.mark.parametrize("location", ["SKILL.md", "references/worker.md", "templates/body.md", "playbooks/code.md", "assets/nested/prompt.md"])
    def test_canonical_calls_resolve_in_every_wf_document(self, tmp_path, location):
        # Scenario: Canonical calls resolve in every WF document
        _write_skill(tmp_path, "wf", "target", "# Target")
        doc = tmp_path / "plugins/wf/skills/caller" / location
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text("<!-- *Load and follow the `target` skill to test the target behavior.* -->")
        assert find_dangling_skill_invocations(tmp_path) == []

    @pytest.mark.parametrize("call", ["Run `target` skill to test.", "*Use `target` skill to test.*", "*Load and follow the `/target` skill to test.*", "Load and follow the `target` skill to test.", "*Load and follow the `target` skill.*", "*Run `target` tactic **Inspect***", "*Load and follow the `target` skill to test."])
    def test_noncanonical_wf_calls_are_reported(self, tmp_path, call):
        # Scenario: Noncanonical WF calls are reported
        _write_skill(tmp_path, "wf", "target", "# Target")
        _write_skill(tmp_path, "wf", "caller", call)
        assert find_dangling_skill_invocations(tmp_path)

    def test_each_call_on_one_line_is_checked(self, tmp_path):
        # Scenario: Each call on one line is checked
        _write_skill(tmp_path, "wf", "caller", "*Load and follow the `ghost` skill to test.* *Load and follow the `missing` skill to test.*")
        violations = find_dangling_skill_invocations(tmp_path)
        assert len(violations) == 2
        assert "ghost" in violations[0].message
        assert "missing" in violations[1].message

    def test_declared_external_skills_are_resolved(self, tmp_path):
        # Scenario: Declared external skills are resolved
        _write_skill(tmp_path, "wf", "caller", "<!-- skill-dependency: external; discovered from the host roster -->\n*Load and follow the `external` skill to test the service.*")
        assert find_dangling_skill_invocations(tmp_path) == []

    def test_canonical_calls_resolve_generated_skill_names(self, tmp_path):
        # Scenario: Canonical calls resolve generated skill names
        _write_skill(tmp_path, "wf", "caller", "*Load and follow the `generated` skill to test the service.*")
        template = tmp_path / "plugins/wf/skills/caller/generated.SKILL.template.md"
        template.write_text("---\nname: generated\ndescription: Test the generated service.\n---\n")
        assert find_dangling_skill_invocations(tmp_path) == []

    def test_dynamic_calls_require_resolution_instructions(self, tmp_path):
        # Scenario: Dynamic calls require resolution instructions
        _write_skill(tmp_path, "wf", "caller", "*Load and follow the `skill-name` skill to <task>*")
        assert find_dangling_skill_invocations(tmp_path)
        caller = tmp_path / "plugins/wf/skills/caller/SKILL.md"
        caller.write_text("Resolve the exact skill name and description before rendering; never emit placeholders literally. *Load and follow the `skill-name` skill to <task>*")
        assert find_dangling_skill_invocations(tmp_path) == []

    def test_dynamic_resolution_does_not_excuse_legacy_wording(self, tmp_path):
        # Scenario: Dynamic resolution does not excuse legacy wording
        _write_skill(tmp_path, "wf", "caller", "Resolve the exact skill name and description; never emit placeholders literally. *Run `skill-name` skill to <task>*")
        assert find_dangling_skill_invocations(tmp_path)

    def test_next_call_does_not_close_an_unterminated_invocation(self, tmp_path):
        # Scenario: Next call does not close an unterminated invocation
        _write_skill(tmp_path, "wf", "target", "# Target")
        _write_skill(tmp_path, "wf", "caller", "*Load and follow the `target` skill to test. *Load and follow the `target` skill to test.*")
        assert len(find_dangling_skill_invocations(tmp_path)) == 1

    def test_human_commands_guards_and_filesystem_paths_are_ignored(self, tmp_path):
        # Scenario: Human commands guards and filesystem paths are ignored
        _write_skill(tmp_path, "wf", "caller", "Ask the user to run `/missing` skill.\nNever invoke `missing` skill.\nDo not use `missing` skill.\n`/caller code` selects a route.\nUse `/usr` for files.\nUse `data` as the result field.")
        assert find_dangling_skill_invocations(tmp_path) == []

    @pytest.mark.parametrize("folder", ["_backup", "_in-progress", "docs/kbs"])
    def test_excluded_folders_do_not_supply_or_require_skills(self, tmp_path, folder):
        # Scenario: Excluded folders do not supply or require skills
        hidden = tmp_path / "plugins/wf" / folder / "SKILL.md"
        hidden.parent.mkdir(parents=True)
        hidden.write_text("---\nname: hidden\n---\nRun `/ghost` skill.")
        _write_skill(tmp_path, "wf", "caller", "*Load and follow the `hidden` skill to test.*")
        violations = find_dangling_skill_invocations(tmp_path)
        assert len(violations) == 1
        assert "hidden" in violations[0].message

    def test_non_wf_legacy_callers_keep_their_existing_policy(self, tmp_path):
        # Scenario: Non WF legacy callers keep their existing policy
        _write_skill(tmp_path, "other", "caller", "Run `/caller` skill.")
        assert find_dangling_skill_invocations(tmp_path) == []
