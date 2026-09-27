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


def test_unmatched_work_routes_to_general_purpose():
    assert select("README.md")["primaryAgent"] == "general-purpose"
