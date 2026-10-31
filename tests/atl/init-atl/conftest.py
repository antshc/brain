import sys
from pathlib import Path

SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3]
    / "plugins" / "atl" / "skills" / "init-atl" / "assets" / "preflight-atlassian" / "scripts"
)
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
