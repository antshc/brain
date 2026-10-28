import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "plugins" / "wf" / "skills" / "implement-spec" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "integration: runs spec_gh.py as a subprocess against a stateful fake gh and a real git repo")
