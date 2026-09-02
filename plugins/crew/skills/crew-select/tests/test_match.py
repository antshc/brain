from crew_select.match import select_stacks

SCOPES = {
    "py": ["*.py", "pyproject.toml"],
    "dotnet": ["*.cs", "*.csproj"],
    "ai": ["*.agent.md", "SKILL.md"],
}


def test_empty_change_set_returns_no_match():
    result = select_stacks([], SCOPES)

    assert result == {"matched": [], "primary": None, "detail": {}}


def test_no_matching_files_returns_no_match():
    result = select_stacks(["README.md", "Makefile"], SCOPES)

    assert result["matched"] == []
    assert result["primary"] is None


def test_single_stack_match_becomes_primary():
    result = select_stacks(["app/main.py"], SCOPES)

    assert result["matched"] == ["py"]
    assert result["primary"] == "py"


def test_several_matches_with_a_clear_primary():
    result = select_stacks(["app/a.py", "app/b.py", "app/c.py", "Service.csproj"], SCOPES)

    assert result["matched"] == ["dotnet", "py"]
    assert result["primary"] == "py"


def test_tied_match_counts_break_by_ascending_stack_id():
    result = select_stacks(["a.py", "Service.csproj"], SCOPES)

    assert result["matched"] == ["dotnet", "py"]
    assert result["primary"] == "dotnet"


def test_path_claimed_by_two_stacks_reports_both():
    scopes = {"py": ["*.md"], "ai": ["*.md"]}

    result = select_stacks(["SKILL.md"], scopes)

    assert result["matched"] == ["ai", "py"]
    assert result["detail"]["ai"] == ["SKILL.md"]
    assert result["detail"]["py"] == ["SKILL.md"]
