import pytest


@pytest.fixture(autouse=True)
def _no_comment_guard_reads(request, monkeypatch):
    """Pipeline tests mock `get_confluence` with MagicMock; keep the comment guard from reading
    it. Tests marked `real_comment_guard` exercise the guard themselves."""
    if request.node.get_closest_marker("real_comment_guard"):
        return
    from atl_cli.page_diagrams import comment_guard

    monkeypatch.setattr(comment_guard, "plan", lambda *_: {"orphaned": [], "unknownIds": []})


def pytest_configure(config):
    config.addinivalue_line("markers", "real_comment_guard: run the real comment_guard.plan")
