from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from atl_cli import cli
from atl_cli.cli import COMMANDS, Command
from atl_cli.twg import runner

ATL_PY = Path(cli.__file__).resolve().parents[1] / "atl.py"
FAKE_TWG = """#!/usr/bin/env python3
import json, os, sys
print(json.dumps({"args": sys.argv[1:], "user": os.environ.get("TWG_USER"),
                  "token": os.environ.get("TWG_TOKEN"), "site": os.environ.get("TWG_SITE")}))
print("stderr " + str(os.environ.get("TWG_TOKEN")), file=sys.stderr)
sys.exit(int(os.environ.get("FAKE_TWG_EXIT", "3")))
"""


@pytest.fixture
def fake_twg(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    script = bin_dir / "twg"
    script.write_text(FAKE_TWG)
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    for name in ("TWG_USER", "TWG_TOKEN", "TWG_SITE"):
        monkeypatch.delenv(name, raising=False)
    return script


def _config(tmp_path: Path, **values) -> Path:
    path = tmp_path / ".atlassian.json.user"
    path.write_text(json.dumps(values))
    return path


def test_credential_env_maps_config_to_twg_overrides():
    env = runner.credential_env({"email": "me@x.com", "apiToken": "tok", "cloudId": "https://org.atlassian.net/"})
    assert env == {"TWG_USER": "me@x.com", "TWG_TOKEN": "tok", "TWG_SITE": "org.atlassian.net"}


def test_credential_env_leaves_twg_login_in_place_without_a_token():
    assert runner.credential_env({"email": "me@x.com", "apiToken": "", "cloudId": ""}) == {}


def test_unknown_command_passes_through_with_credentials_and_redacted_output(fake_twg, tmp_path, capsysbinary):
    config = _config(tmp_path, email="me@x.com", apiToken="secret-token", cloudId="https://org.atlassian.net/")

    exit_code = cli.main(["--config", str(config), "jira", "workitem", "query", "--jql", "x"])

    out, err = capsysbinary.readouterr()
    payload = json.loads(out)
    assert exit_code == 3
    assert payload["args"] == ["jira", "workitem", "query", "--jql", "x"]
    assert payload["token"] == "<redacted>" and payload["user"] == "<redacted>"
    assert payload["site"] == "org.atlassian.net"
    assert b"secret-token" not in out + err and b"me@x.com" not in out + err
    assert not {"TWG_USER", "TWG_TOKEN", "TWG_SITE"} & set(os.environ)


def test_passthrough_runs_without_a_config(fake_twg, capsysbinary):
    cli.main(["whoami"])

    payload = json.loads(capsysbinary.readouterr().out)
    assert payload["args"] == ["whoami"] and payload["token"] is None


def test_missing_twg_exits_127(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(runner, "find_twg", lambda: None)

    assert cli.main(["whoami"]) == 127
    assert capsys.readouterr().err == "error: twg CLI not found\n"


def test_find_twg_falls_back_to_the_default_install_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(runner.shutil, "which", lambda name: None)
    binary = tmp_path / ".local" / "bin" / "twg"
    binary.parent.mkdir(parents=True)
    binary.write_text("")

    assert runner.find_twg(home=tmp_path, local_app_data="") == str(binary)


@pytest.mark.parametrize("content", ["{not json", "[1, 2]", "\udcff"])
def test_malformed_config_prints_only_the_safe_message(fake_twg, tmp_path, capsys, content):
    config = tmp_path / "bad.json"
    if content == "\udcff":
        config.write_bytes(b"\xff\xfe secret-token")
    else:
        config.write_text(content + ' "secret-token"')

    exit_code = cli.main([f"--config={config}", "whoami"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.err == "error: unreadable or malformed Atlassian config\n"
    assert "secret-token" not in captured.out + captured.err


def test_native_forwards_a_markdown_body_command_to_twg_unchanged(fake_twg, tmp_path, capsysbinary):
    config = _config(tmp_path, cloudId="org.atlassian.net")

    cli.main(["--config", str(config), "confluence", "content", "get", "12", "--native", "--format", "md"])

    assert json.loads(capsysbinary.readouterr().out)["args"] == ["confluence", "content", "get", "12", "--format", "md"]


def test_leading_config_is_appended_to_atl_commands_that_take_one(tmp_path, monkeypatch):
    seen: list[list[str]] = []
    monkeypatch.setitem(COMMANDS, "fetch-page", Command("", lambda argv, prog: seen.append(argv)))
    monkeypatch.setitem(COMMANDS, "doctor", Command("", lambda argv, prog: seen.append(argv)))
    monkeypatch.setitem(COMMANDS, "map-markdown", Command("", lambda argv, prog: seen.append(argv)))

    cli.main(["--config", "c.json", "fetch-page", "--page-id", "1", "--md-path", "p.md"])
    cli.main(["--config", "c.json", "doctor"])
    cli.main(["--config", "c.json", "map-markdown", "md-to-adf"])

    assert seen == [
        ["--page-id", "1", "--md-path", "p.md", "--config", "c.json"],
        ["--config", "c.json"],
        ["md-to-adf"],
    ]


def test_markdown_workitem_update_publishes_then_forwards_remaining_flags(fake_twg, tmp_path, monkeypatch, capsys):
    config = _config(tmp_path, email="me@x.com", apiToken="secret-token", cloudId="org.atlassian.net")
    seen: list[list[str]] = []

    def publish(argv: list[str], prog: str) -> None:
        seen.append(argv)
        print(json.dumps({"key": "ABC-1", "url": "https://org.atlassian.net/browse/ABC-1"}))

    monkeypatch.setitem(COMMANDS, "publish-work", Command("", publish))
    monkeypatch.setenv("FAKE_TWG_EXIT", "0")

    exit_code = cli.main(
        ["--config", str(config), "jira", "workitem", "update", "--id", "ABC-1", "--description", "# Hi", "--status", "Done", "--labels", "a,b"]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert seen[0][:4] == ["update", "--key", "ABC-1", "--markdown"]
    assert seen[0][-2:] == ["--config", str(config)]
    assert json.loads(captured.out)["followUp"] == {"command": "jira workitem update", "exitCode": 0}
    assert '"args": ["jira", "workitem", "update", "--id", "ABC-1", "--status", "Done", "--labels", "a,b"]' in captured.err
    assert "secret-token" not in captured.out + captured.err


def test_failed_follow_up_reports_the_published_key_and_its_exit_code(fake_twg, tmp_path, monkeypatch, capsys):
    monkeypatch.setitem(COMMANDS, "publish-work", Command("", lambda argv, prog: print(json.dumps({"key": "ABC-9"}))))

    exit_code = cli.main(
        ["--config", str(_config(tmp_path)), "jira", "workitem", "create", "--space", "ABC", "--type", "Task", "--summary", "S", "--description", "x", "--priority", "High"]
    )

    captured = capsys.readouterr()
    assert exit_code == 3
    assert json.loads(captured.out)["key"] == "ABC-9"
    assert "atl.py jira workitem update --id ABC-9 --priority High" in captured.err


def test_markdown_body_command_without_config_exits_2(fake_twg, capsys):
    assert cli.main(["jira", "workitem", "get", "ABC-1", "--output-file", "w.md"]) == 2
    assert "--config <configPath>" in capsys.readouterr().err


def test_script_runs_from_any_cwd_and_forwards_the_exit_code(fake_twg, tmp_path):
    config = _config(tmp_path, email="me@x.com", apiToken="secret-token", cloudId="org.atlassian.net")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = subprocess.run(
        [sys.executable, str(ATL_PY), "--config", str(config), "jira", "workitem", "query"],
        cwd=elsewhere,
        capture_output=True,
        env=os.environ.copy(),
    )

    assert result.returncode == 3
    assert json.loads(result.stdout)["args"] == ["jira", "workitem", "query"]
    assert b"secret-token" not in result.stdout + result.stderr


def test_markdown_comment_runs_on_twg_with_an_inline_body_and_credentials(fake_twg, tmp_path, monkeypatch, capsysbinary):
    config = _config(tmp_path, email="me@x.com", apiToken="secret-token", cloudId="org.atlassian.net")
    body = tmp_path / "comment.md"
    body.write_text("**done**\n", encoding="utf-8")
    monkeypatch.setenv("FAKE_TWG_EXIT", "0")

    exit_code = cli.main(
        ["--config", str(config), "jira", "workitem", "comment", "create", "--issue-id", "ABC-7", "--body-file", str(body), "--body-format", "markdown", "-o", "json"]
    )

    captured = capsysbinary.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["args"] == ["jira", "workitem", "comment", "create", "--issue-id", "ABC-7", "-o", "json", "--body", "**done**\n", "--body-format", "markdown"]
    assert payload["token"] == "<redacted>"
    assert b"secret-token" not in captured.out + captured.err


def test_comment_body_file_without_markdown_format_exits_2_without_running_twg(fake_twg, tmp_path, capsysbinary):
    body = tmp_path / "comment.md"
    body.write_text("x")

    exit_code = cli.main(["jira", "workitem", "comment", "create", "--issue-id", "ABC-7", "--body-file", str(body)])

    captured = capsysbinary.readouterr()
    assert exit_code == 2
    assert b"--body-format markdown" in captured.err
    assert captured.out == b""
