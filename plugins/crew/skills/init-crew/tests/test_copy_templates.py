import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "copy_templates.py"
spec = importlib.util.spec_from_file_location("copy_templates", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_copy_templates_targets_codebase_and_preserves_existing_files(tmp_path):
    harness = tmp_path / "harness"
    codebase = tmp_path / "codebase"
    harness.mkdir()
    codebase.mkdir()
    existing = codebase / ".github" / "instructions" / "python.instructions.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("custom rules\n")

    first = module.copy_missing(harness, codebase, ["py", "dotnet", "ai"])
    second = module.copy_missing(harness, codebase, ["py", "dotnet", "ai"])

    assert existing.read_text() == "custom rules\n"
    assert (codebase / ".github/instructions/dotnet.instructions.md").read_text().startswith("---\napplyTo:")
    assert (codebase / ".github/instructions/ai-authoring.instructions.md").exists()
    assert (harness / ".github/skills/chore-ai/SKILL.md").exists()
    assert (harness / ".github/skills/chore-dotnet/SKILL.md").exists()
    assert (harness / ".github/skills/chore-py/SKILL.md").exists()
    assert (harness / ".github/skills/gotchas-memory/SKILL.md").exists()
    assert (harness / ".github/skills/gotchas-memory/GOTCHAS.md").exists()
    assert len(first["created"]) == 7
    assert len(first["skipped"]) == 1
    assert not second["created"]
    assert len(second["skipped"]) == 8
    assert not (harness / ".crew/CODE-py.md").exists()
    assert not (harness / ".crew/VERIFY-py.md").exists()


def test_copy_templates_preserves_existing_repository_skills_and_memory(tmp_path):
    harness = tmp_path / "harness"
    codebase = tmp_path / "codebase"
    harness.mkdir()
    codebase.mkdir()
    rules = harness / ".github/skills/chore-py/SKILL.md"
    memory_skill = harness / ".github/skills/gotchas-memory/SKILL.md"
    memory = harness / ".github/skills/gotchas-memory/GOTCHAS.md"
    for path, content in (
        (rules, "repository Python rules\n"),
        (memory_skill, "repository memory locator\n"),
        (memory, "repository directive\n"),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    result = module.copy_missing(harness, codebase, ["py"])

    assert rules.read_text() == "repository Python rules\n"
    assert memory_skill.read_text() == "repository memory locator\n"
    assert memory.read_text() == "repository directive\n"
    assert len(result["created"]) == 1
    assert set(result["skipped"]) == {str(rules), str(memory_skill), str(memory)}
