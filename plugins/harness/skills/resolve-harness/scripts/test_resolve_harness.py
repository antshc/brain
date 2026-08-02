"""Harness script behavior tests.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

import subprocess
import sys
from pathlib import Path


RESOLVER_SCRIPT = Path(__file__).parent / "resolve_harness.py"
def run_script(script: Path, working_directory: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script)],
        cwd=working_directory,
        capture_output=True,
        text=True,
        check=False,
    )


class TestMainHarness:
    """Feature: Main Harness"""

    def test_nearest_harness_configuration_is_resolved(self, tmp_path: Path):
        # Scenario: Nearest Harness Configuration File is resolved
        (tmp_path / ".harness.env").write_text('HARNESS_REPO_PATH="/outer"\nOUTER=value\n')
        nested_directory = tmp_path / "project" / "nested"
        nested_directory.mkdir(parents=True)
        (tmp_path / "project" / ".harness.env").write_text('HARNESS_REPO_PATH="/inner"\nINNER=value\n')

        result = run_script(RESOLVER_SCRIPT, nested_directory)

        assert result.returncode == 0
        assert result.stdout == 'HARNESS_REPO_PATH="/inner"\nINNER=value\n'
        assert result.stderr == ""

    def test_all_harness_settings_are_emitted_verbatim(self, tmp_path: Path):
        # Scenario: All Harness Settings are emitted verbatim
        config_path = tmp_path / ".harness.env"
        config_path.write_text('HARNESS_REPO_PATH="/harness"\nVALUE=first=second\nEMPTY=\n')

        result = run_script(RESOLVER_SCRIPT, tmp_path)

        assert result.returncode == 0
        assert result.stdout == 'HARNESS_REPO_PATH="/harness"\nVALUE=first=second\nEMPTY=\n'
        assert result.stderr == ""

    def test_no_harness_configuration_returns_empty_root(self, tmp_path: Path):
        # Scenario: No Harness Configuration File returns an empty Harness Root
        result = run_script(RESOLVER_SCRIPT, tmp_path)

        assert result.returncode == 0
        assert result.stdout == "HARNESS_REPO_PATH=\n"
        assert result.stderr == "No .harness.env found; fall back to the current directory.\n"

    def test_missing_harness_root_fails_resolution(self, tmp_path: Path):
        # Scenario: Missing Harness Root fails resolution
        (tmp_path / ".harness.env").write_text("SETTING=value\n")

        result = run_script(RESOLVER_SCRIPT, tmp_path)

        assert result.returncode == 1
        assert result.stdout == ""
        assert "HARNESS_REPO_PATH is required" in result.stderr
