"""Harness script behavior tests.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

import json
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
        (tmp_path / ".harness.json.user").write_text(json.dumps({"harness": {"outer": True}}))
        nested_directory = tmp_path / "project" / "nested"
        nested_directory.mkdir(parents=True)
        inner_config = tmp_path / "project" / ".harness.json.user"
        inner_config.write_text(json.dumps({"harness": {"inner": True}}))

        result = run_script(RESOLVER_SCRIPT, nested_directory)

        assert result.returncode == 0
        assert json.loads(result.stdout) == {
            "harnessRepoPath": str(inner_config.parent),
            "harness": {"inner": True},
            "atl": {},
        }
        assert result.stderr == ""

    def test_all_non_credential_sections_are_emitted_verbatim(self, tmp_path: Path):
        # Scenario: All non-credential Harness Settings are emitted verbatim
        config_path = tmp_path / ".harness.json.user"
        config_path.write_text(json.dumps({
            "harness": {"repos": [{"repository": "owner/name", "branch": "main"}]},
            "atl": {"site": "example.atlassian.net"},
        }))

        result = run_script(RESOLVER_SCRIPT, tmp_path)

        assert result.returncode == 0
        assert json.loads(result.stdout) == {
            "harnessRepoPath": str(tmp_path),
            "harness": {"repos": [{"repository": "owner/name", "branch": "main"}]},
            "atl": {"site": "example.atlassian.net"},
        }
        assert result.stderr == ""

    def test_credentials_are_never_emitted(self, tmp_path: Path):
        # Scenario: Credentials are never emitted
        config_path = tmp_path / ".harness.json.user"
        config_path.write_text(json.dumps({
            "atl": {"site": "example.atlassian.net"},
            "credentials": {"atl": {"api_token": "super-secret", "email": "me@example.com"}},
        }))

        result = run_script(RESOLVER_SCRIPT, tmp_path)

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "credentials" not in output
        assert "super-secret" not in result.stdout

    def test_no_harness_configuration_returns_empty_sections(self, tmp_path: Path):
        # Scenario: No Harness Configuration File returns empty sections
        result = run_script(RESOLVER_SCRIPT, tmp_path)

        assert result.returncode == 0
        assert json.loads(result.stdout) == {"harnessRepoPath": "", "harness": {}, "atl": {}}
        assert result.stderr == "No .harness.json.user found; fall back to the current directory.\n"

    def test_invalid_json_fails_resolution(self, tmp_path: Path):
        # Scenario: Invalid JSON fails resolution
        (tmp_path / ".harness.json.user").write_text("{not valid json")

        result = run_script(RESOLVER_SCRIPT, tmp_path)

        assert result.returncode == 1
        assert result.stdout == ""
        assert "Invalid harness configuration" in result.stderr
