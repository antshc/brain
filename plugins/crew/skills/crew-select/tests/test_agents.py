import pytest

from crew_select.agents import discover_stack_agents, parse_scope


def test_parse_scope_reads_backtick_patterns_from_frontmatter_description_only():
    text = '---\nname: codey-py\ndescription: "Python: `*.py`, `pyproject.toml`. Implements changes."\n---\n\n**Scope**: `*.wrong`\n'
    assert parse_scope(text) == ["*.py", "pyproject.toml"]


def test_parse_scope_returns_empty_without_description_patterns():
    text = "---\nname: codey-py\ndescription: Python changes.\n---\n\n**Scope**: `*.py`\n"
    assert parse_scope(text) == []


def test_discover_stack_agents_skips_chorey(tmp_path):
    (tmp_path / "chorey.agent.md").write_text("# Chorey\n\nBody.\n")
    (tmp_path / "codey-py.agent.md").write_text("---\ndescription: 'Python: `*.py`'\n---\n")

    stacks = discover_stack_agents(tmp_path)

    assert stacks == {"py": ["*.py"]}


def test_discover_stack_agents_maps_every_installed_stack(tmp_path):
    (tmp_path / "codey-py.agent.md").write_text("---\ndescription: 'Python: `*.py`'\n---\n")
    (tmp_path / "codey-dotnet.agent.md").write_text("---\ndescription: 'C#/.NET: `*.cs`, `*.csproj`'\n---\n")
    (tmp_path / "codey-ai.agent.md").write_text("---\ndescription: 'Skills: `SKILL.md`, `*.agent.md`'\n---\n")

    stacks = discover_stack_agents(tmp_path)

    assert stacks == {"py": ["*.py"], "dotnet": ["*.cs", "*.csproj"], "ai": ["SKILL.md", "*.agent.md"]}


def test_discover_stack_agents_rejects_agent_without_file_patterns(tmp_path):
    (tmp_path / "codey-py.agent.md").write_text("---\ndescription: Python changes.\n---\n")

    with pytest.raises(ValueError, match="description has no file patterns"):
        discover_stack_agents(tmp_path)
