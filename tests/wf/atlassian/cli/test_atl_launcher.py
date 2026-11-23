"""`atl.py` launcher: picks the configured or repository interpreter and re-executes once."""
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import venv
from pathlib import Path

from atl_cli import cli

ATL_PY = Path(cli.__file__).resolve().parents[1] / "atl.py"
FAKE_PYTHON = """#!/bin/sh
if [ "$1" = "-c" ]; then exit "${PROBE_EXIT:-0}"; fi
printf '%s\\n' "$ATL_PYTHON_REEXEC" "$PWD" "$@" > "$RECORD"
"""


def _make_venv(path: Path, *, complete: bool) -> Path:
    venv.EnvBuilder(symlinks=True, with_pip=False).create(path)
    if complete:
        site = next((path / "lib").glob("python*/site-packages"))
        for module in ("atlassian/__init__.py", "pymarkdown/__init__.py", "pymarkdown/api.py", "requests/__init__.py"):
            (site / module).parent.mkdir(parents=True, exist_ok=True)
            (site / module).write_text("")
    return path / "bin" / "python"


def _config(tmp_path: Path, **values) -> Path:
    path = tmp_path / ".atlassian.json.user"
    path.write_text(json.dumps(values))
    return path


def _doctor_python(cwd: Path, *args: str, **env: str) -> str:
    result = subprocess.run(
        [sys.executable, str(ATL_PY), *args, "doctor"],
        cwd=cwd, capture_output=True, text=True, env={**os.environ, **env},
    )
    return json.loads(result.stdout)["pythonExecutable"]


def _fake_python(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(FAKE_PYTHON)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return path


def test_config_python_path_wins_over_ambient_python_even_when_both_share_a_base_interpreter(tmp_path):
    configured = _make_venv(tmp_path / "configured", complete=False)
    config = _config(tmp_path, pythonPath=str(configured))

    assert _doctor_python(tmp_path, "--config", str(config)) == str(configured)


def test_nearest_dependency_complete_venv_is_used_from_a_nested_cwd(tmp_path):
    outer = _make_venv(tmp_path / "repo" / ".venv", complete=True)
    _make_venv(tmp_path / "repo" / "pkg" / ".venv", complete=False)
    nested = tmp_path / "repo" / "pkg" / "src"
    nested.mkdir(parents=True)

    assert _doctor_python(nested) == str(outer)


def test_config_python_path_wins_over_a_repository_venv(tmp_path):
    configured = _make_venv(tmp_path / "configured", complete=False)
    _make_venv(tmp_path / "repo" / ".venv", complete=True)
    config = _config(tmp_path, pythonPath=str(configured))

    assert _doctor_python(tmp_path / "repo", "--config", str(config)) == str(configured)


def test_missing_or_relative_python_path_falls_back_to_the_ambient_python(tmp_path):
    config = _config(tmp_path, pythonPath="relative/python")

    assert _doctor_python(tmp_path, "--config", str(config)) == sys.executable


def test_reexec_happens_once_and_keeps_cwd_and_arguments(tmp_path):
    record = tmp_path / "record.txt"
    configured = _fake_python(tmp_path / "bin" / "python")
    config = _config(tmp_path, pythonPath=str(configured), email="me@x.com", apiToken="secret-token", cloudId="org.atlassian.net")
    cwd = tmp_path / "work"
    cwd.mkdir()

    subprocess.run(
        [sys.executable, str(ATL_PY), "--config", str(config), "doctor"],
        cwd=cwd, env={**os.environ, "RECORD": str(record)}, check=True,
    )

    reexec, workdir, script, *arguments = record.read_text().splitlines()
    assert (reexec, workdir, Path(script)) == ("1", str(cwd), ATL_PY)
    assert arguments == ["--config", str(config), "doctor"]
    assert "secret-token" not in record.read_text()


def test_an_already_reexecuted_process_never_reexecs_again(tmp_path):
    record = tmp_path / "record.txt"
    configured = _fake_python(tmp_path / "bin" / "python")
    config = _config(tmp_path, pythonPath=str(configured))

    assert _doctor_python(tmp_path, "--config", str(config), ATL_PYTHON_REEXEC="1", RECORD=str(record)) == sys.executable
    assert not record.exists()


def test_a_venv_missing_dependencies_is_skipped(tmp_path):
    record = tmp_path / "record.txt"
    _fake_python(tmp_path / "repo" / ".venv" / "bin" / "python")

    python = _doctor_python(tmp_path / "repo", PROBE_EXIT="1", RECORD=str(record))

    assert python == sys.executable
    assert not record.exists()
