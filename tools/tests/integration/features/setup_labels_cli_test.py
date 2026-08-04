"""Subprocess-level CLI tests for the setup_labels script, against a fake `gh` binary.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

import os
from pathlib import Path
import stat
import subprocess
import sys


SCRIPT = Path(__file__).parent.parent.parent.parent / "src" / "modules" / "github_tracker" / "setup_labels.py"

_FAKE_GH = """#!/usr/bin/env python3
import json
import os
import sys

args = sys.argv[1:]

if args[:2] == ["repo", "view"]:
    print("owner/repo")
elif args[:2] == ["label", "list"]:
    existing = [name for name in os.environ.get("FAKE_GH_EXISTING_LABELS", "").split(",") if name]
    print(json.dumps([{"name": name} for name in existing]))
elif args[:2] == ["label", "create"]:
    log_path = os.environ.get("FAKE_GH_CREATE_LOG")
    if log_path:
        with open(log_path, "a") as f:
            f.write(args[2] + "\\n")
else:
    print(f"unexpected gh invocation: {args}", file=sys.stderr)
    sys.exit(1)
"""


def make_fake_gh(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_gh = bin_dir / "gh"
    fake_gh.write_text(_FAKE_GH)
    fake_gh.chmod(fake_gh.stat().st_mode | stat.S_IEXEC)
    return bin_dir


def run_script(bin_dir: Path, **extra_env: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}", **extra_env}
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True, check=False, env=env,
    )


class TestSetupLabelsCli:
    """Feature: Setup Labels CLI"""

    def test_missing_labels_are_created(self, tmp_path: Path):
        # Scenario: Missing labels are created
        bin_dir = make_fake_gh(tmp_path)
        create_log = tmp_path / "created.log"

        result = run_script(bin_dir, FAKE_GH_EXISTING_LABELS="", FAKE_GH_CREATE_LOG=str(create_log))

        assert result.returncode == 0, result.stderr
        assert "created: hitl" in result.stdout
        assert "created: spec" in result.stdout
        assert create_log.read_text().splitlines() == ["hitl", "spec"]

    def test_already_existing_labels_are_left_unchanged(self, tmp_path: Path):
        # Scenario: Already existing labels are left unchanged
        bin_dir = make_fake_gh(tmp_path)
        create_log = tmp_path / "created.log"

        result = run_script(bin_dir, FAKE_GH_EXISTING_LABELS="hitl,spec", FAKE_GH_CREATE_LOG=str(create_log))

        assert result.returncode == 0, result.stderr
        assert "exists:  hitl" in result.stdout
        assert "exists:  spec" in result.stdout
        assert not create_log.exists()
