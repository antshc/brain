import json
import subprocess
import sys
from pathlib import Path


SELECT = Path(__file__).resolve().parents[1] / "scripts" / "select.py"
AGENTS = Path(__file__).resolve().parents[3] / "agents"


def select(*paths):
    result = subprocess.run(
        [sys.executable, str(SELECT), "--agents-dir", str(AGENTS), *paths],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_ai_authoring_routes_to_retained_agent():
    assert select("plugins/example/skills/new/SKILL.md")["primaryAgent"] == "codey-ai"


def test_csharp_and_build_files_route_to_dotnet_agent():
    result = select("src/Service.cs", "src/Service.csproj", "src/Directory.Build.props")
    assert result["primaryAgent"] == "codey-dotnet"
    assert result["matched"] == ["dotnet"]
    assert result["detail"]["dotnet"] == ["src/Service.cs", "src/Service.csproj", "src/Directory.Build.props"]


def test_fsharp_and_vb_files_do_not_route_to_csharp_agent():
    result = select("src/Service.fs", "src/Service.fsproj", "src/Service.vb", "src/Service.vbproj")
    assert result["primaryAgent"] == "general-purpose"
    assert result["matched"] == []


def test_mixed_stack_change_retains_every_match():
    result = select("src/Service.cs", "scripts/update.py")
    assert result["matched"] == ["dotnet", "py"]


def test_unmatched_work_routes_to_general_purpose():
    assert select("README.md")["primaryAgent"] == "general-purpose"
