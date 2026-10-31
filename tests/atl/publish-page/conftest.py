import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "plugins" / "atl" / "skills" / "publish-page" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


import pytest


@pytest.fixture(autouse=True)
def _no_comment_guard_reads(request, monkeypatch):
    """Pipeline tests mock `get_confluence` with MagicMock; keep the comment guard from reading
    it. Tests marked `real_comment_guard` exercise the guard themselves."""
    if request.node.get_closest_marker("real_comment_guard"):
        return
    from page_diagrams import comment_guard

    monkeypatch.setattr(comment_guard, "plan", lambda *_: {"orphaned": [], "unknownIds": []})


def pytest_configure(config):
    config.addinivalue_line("markers", "real_comment_guard: run the real comment_guard.plan")
