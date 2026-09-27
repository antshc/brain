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
    assert (harness / ".crew/CHORE-py.md").exists()
    assert (harness / ".crew/GOTCHAS.md").exists()
    assert len(first["created"]) == 6
    assert len(first["skipped"]) == 1
    assert not second["created"]
    assert len(second["skipped"]) == 7
    assert not (harness / ".crew/CODE-py.md").exists()
    assert not (harness / ".crew/VERIFY-py.md").exists()
