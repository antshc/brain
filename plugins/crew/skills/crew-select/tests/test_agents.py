from crew_select.agents import discover_stack_agents, parse_scope


def test_parse_scope_reads_backtick_globs_from_the_scope_line():
    text = "# Codey — Python Stack\n**Scope**: `*.py`, `pyproject.toml`\n\nBody.\n"
    assert parse_scope(text) == ["*.py", "pyproject.toml"]


def test_parse_scope_returns_empty_when_no_scope_line():
    text = "# Codey\n\nBody.\n"
    assert parse_scope(text) == []


def test_discover_stack_agents_skips_base_codey_and_chorey(tmp_path):
    (tmp_path / "codey.agent.md").write_text("# Codey\n\nBody.\n")
    (tmp_path / "chorey.agent.md").write_text("# Chorey\n\nBody.\n")
    (tmp_path / "codey-py.agent.md").write_text("# Codey — Python Stack\n**Scope**: `*.py`\n")

    stacks = discover_stack_agents(tmp_path)

    assert stacks == {"py": ["*.py"]}


def test_discover_stack_agents_maps_every_installed_stack(tmp_path):
    (tmp_path / "codey-py.agent.md").write_text("**Scope**: `*.py`\n")
    (tmp_path / "codey-dotnet.agent.md").write_text("**Scope**: `*.cs`, `*.csproj`\n")

    stacks = discover_stack_agents(tmp_path)

    assert stacks == {"py": ["*.py"], "dotnet": ["*.cs", "*.csproj"]}
