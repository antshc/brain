import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ATL_PY = Path(__file__).resolve().parents[4] / "plugins" / "atl" / "skills" / "atlassian" / "scripts" / "atl.py"
COMMANDS = ("fetch-work", "publish-work", "fetch-page", "publish-page", "map-markdown")


def _run(*args: str, cwd: Path, stdin: str = "", env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ATL_PY), *args], input=stdin, capture_output=True, text=True, cwd=cwd, env=env
    )


def test_root_help_lists_every_command_from_an_unrelated_directory(tmp_path):
    result = _run("--help", cwd=tmp_path)

    assert result.returncode == 0
    for command in COMMANDS:
        assert command in result.stdout


def test_missing_or_unknown_command_exits_2_with_usage(tmp_path):
    assert _run(cwd=tmp_path).returncode == 2
    unknown = _run("fetch-pages", cwd=tmp_path)
    assert unknown.returncode == 2
    assert "invalid choice" in unknown.stderr


@pytest.mark.parametrize(
    "args",
    [
        ("fetch-work",),
        ("publish-work",),
        ("fetch-page",),
        ("publish-page", "verify"),
        ("publish-page", "check-anchors"),
        ("map-markdown",),
    ],
)
def test_each_command_help_names_its_atl_py_prog(tmp_path, args):
    result = _run(*args, "--help", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert f"usage: atl.py {' '.join(args)}" in result.stdout


def test_map_markdown_round_trips_offline_without_config_or_atlassian_library(tmp_path):
    blocker = tmp_path / "blocker"
    (blocker / "atlassian").mkdir(parents=True)
    (blocker / "atlassian" / "__init__.py").write_text("raise ImportError('atlassian-python-api must not load')\n")
    (blocker / "requests").mkdir()
    (blocker / "requests" / "__init__.py").write_text("raise ImportError('requests must not load')\n")
    env = {**os.environ, "PYTHONPATH": str(blocker)}

    adf = _run("map-markdown", "md-to-adf", cwd=tmp_path, stdin="# Title\n\nSome **bold**.\n", env=env)
    assert adf.returncode == 0, adf.stderr
    markdown = _run("map-markdown", "adf-to-md", cwd=tmp_path, stdin=adf.stdout, env=env)
    assert markdown.returncode == 0, markdown.stderr
    assert markdown.stdout == "# Title\n\nSome **bold**.\n"
    detect = _run("map-markdown", "detect-adf-only", cwd=tmp_path, stdin="> [!INFO]\n> Note\n", env=env)
    assert json.loads(detect.stdout)["adfOnly"] is True


def test_fetch_page_without_credentials_names_them_and_writes_nothing(tmp_path):
    config = tmp_path / ".atlassian.json.user"
    config.write_text("{}")

    result = _run("fetch-page", "--page-id", "1", "--config", str(config), "--md-path", "page.md", cwd=tmp_path)

    assert result.returncode != 0
    assert "cloudId, email, and apiToken" in result.stderr or "atlassian-python-api" in result.stderr
    assert not (tmp_path / "page.md").exists()
