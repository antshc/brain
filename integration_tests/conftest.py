"""Shared pytest configuration for integration tests.

Usage
-----
Mock mode (default)::

    python3 -m pytest integration_tests/ -v

Real mode (hits live GitHub API and Copilot CLI)::

    # 1. Copy integration_tests/integrationtest-config.json.template
    #    to   integration_tests/integrationtest-config.json
    # 2. Fill in your real values
    # 3. Run:
    python3 -m pytest integration_tests/ --real -v

Tests that assert on mock internals are decorated with @pytest.mark.mock_only
and are automatically skipped when --real is passed.
"""

import json
import sys
from pathlib import Path

import pytest

# ── sys.path ──────────────────────────────────────────────────────────────────
# Add app/ to sys.path once here so individual test files don't need to.
_APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

_CONFIG_FILE = Path(__file__).resolve().parent / "integrationtest-config.json"


# ── CLI option ────────────────────────────────────────────────────────────────

def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--real",
        action="store_true",
        default=False,
        help="Run integration tests against live infrastructure (GitHub API + Copilot CLI).",
    )


# ── Marker registration ───────────────────────────────────────────────────────

def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "mock_only: test uses mock-specific assertions; skipped in --real mode.",
    )


# ── Auto-skip mock_only in real mode ──────────────────────────────────────────

def pytest_runtest_setup(item: pytest.Item) -> None:
    if item.config.getoption("--real") and item.get_closest_marker("mock_only"):
        pytest.skip("Skipped in --real mode (mock-only assertions)")


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def use_real(request: pytest.FixtureRequest) -> bool:
    """True when --real flag is passed; False in default mock mode."""
    return bool(request.config.getoption("--real"))


@pytest.fixture
def real_config(use_real: bool) -> dict:
    """Load integrationtest-config.json when running in real mode.

    Skips the test if the config file is absent so that real-mode tests
    fail gracefully in CI rather than erroring out.
    """
    if not use_real:
        return {}
    if not _CONFIG_FILE.exists():
        pytest.skip(
            f"Real config not found: {_CONFIG_FILE}. "
            "Copy integrationtest-config.json.template → integrationtest-config.json and fill in values."
        )
    return json.loads(_CONFIG_FILE.read_text())
