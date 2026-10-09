import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "plugins" / "atl" / "skills" / "fetch-work" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
