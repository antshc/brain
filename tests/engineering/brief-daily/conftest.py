import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "skills" / "engineering" / "daily-briefing" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def spill(tmp_path):
    counter = {"n": 0}

    def write(payload):
        counter["n"] += 1
        path = tmp_path / f"content{counter['n']}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return str(path)

    return write
