import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "match_changed_files.py"


def match(*paths):
    result = subprocess.run([sys.executable, str(SCRIPT), *paths], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def test_mixed_change_preserves_each_matching_stack():
    assert match("src/Service.cs", "scripts/update.py", "plugins/crew/agents/codey-py.agent.md") == {
        "ai": ["plugins/crew/agents/codey-py.agent.md"],
        "dotnet": ["src/Service.cs"],
        "py": ["scripts/update.py"],
    }


def test_unmatched_and_empty_changes_use_default_review():
    assert match("README.md", "src/Service.fs", "src/Service.vb") == {}
    assert match() == {}


def test_file_pattern_matches_nested_paths_on_windows_and_unix():
    assert match("src\\Directory.Build.props", "src/Directory.Packages.props") == {
        "dotnet": ["src\\Directory.Build.props", "src/Directory.Packages.props"]
    }
