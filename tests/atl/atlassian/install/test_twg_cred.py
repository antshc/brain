from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

import twg_cred as twg

FAKE_TWG = """#!/usr/bin/env python3
import json, os, sys
print(json.dumps({"args": sys.argv[1:], "user": os.environ.get("TWG_USER"),
                  "token": os.environ.get("TWG_TOKEN"), "site": os.environ.get("TWG_SITE")}))
print("stderr " + str(os.environ.get("TWG_TOKEN")), file=sys.stderr)
sys.exit(3)
"""


@pytest.fixture
def fake_twg(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    script = bin_dir / "twg"
    script.write_text(FAKE_TWG)
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    return script


def _config(tmp_path: Path, **values) -> Path:
    path = tmp_path / ".atlassian.json.user"
    path.write_text(json.dumps(values))
    return path


def test_credential_env_maps_config_to_twg_overrides():
    env = twg.credential_env({"email": "me@x.com", "apiToken": "tok", "cloudId": "https://org.atlassian.net/"})
    assert env == {"TWG_USER": "me@x.com", "TWG_TOKEN": "tok", "TWG_SITE": "org.atlassian.net"}


def test_credential_env_leaves_twg_login_in_place_without_a_token():
    assert twg.credential_env({"email": "me@x.com", "apiToken": "", "cloudId": ""}) == {}


def test_main_passes_args_and_credentials_and_redacts_secrets(fake_twg, tmp_path, capsysbinary):
    config = _config(tmp_path, email="me@x.com", apiToken="secret-token", cloudId="https://org.atlassian.net")

    exit_code = twg.main(["jira", "workitem", "get", "ABC-1"], config_path=config)

    out, err = capsysbinary.readouterr()
    payload = json.loads(out)
    assert exit_code == 3
    assert payload["args"] == ["jira", "workitem", "get", "ABC-1"]
    assert payload["user"] == "<redacted>"
    assert payload["token"] == "<redacted>"
    assert payload["site"] == "org.atlassian.net"
    assert b"secret-token" not in out + err
    assert b"me@x.com" not in out + err


def test_main_runs_without_a_config_file(fake_twg, tmp_path, capsysbinary, monkeypatch):
    for name in ("TWG_USER", "TWG_TOKEN", "TWG_SITE"):
        monkeypatch.delenv(name, raising=False)

    twg.main(["whoami"], config_path=tmp_path / "missing.json")

    payload = json.loads(capsysbinary.readouterr().out)
    assert payload["user"] is None and payload["token"] is None


def test_main_reports_a_missing_twg(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(twg, "find_twg", lambda: None)

    exit_code = twg.main(["whoami"], config_path=tmp_path / "missing.json")

    assert exit_code == 127
    assert capsys.readouterr().err == "error: twg CLI not found\n"


def test_find_twg_falls_back_to_the_default_install_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(twg.shutil, "which", lambda name: None)
    binary = tmp_path / ".local" / "bin" / "twg"
    binary.parent.mkdir(parents=True)
    binary.write_text("")

    assert twg.find_twg(home=tmp_path, local_app_data="") == str(binary)


SCRIPT = Path(twg.__file__)


def test_config_flag_is_stripped_and_used_and_env_stays_in_the_child(fake_twg, tmp_path, capsysbinary, monkeypatch):
    for name in ("TWG_USER", "TWG_TOKEN", "TWG_SITE"):
        monkeypatch.delenv(name, raising=False)
    config = _config(tmp_path, email="me@x.com", apiToken="secret-token", cloudId="https://org.atlassian.net/")

    exit_code = twg.main(["--config", str(config), "whoami", "-o", "json"], config_path=tmp_path / "unused.json")

    out, err = capsysbinary.readouterr()
    payload = json.loads(out)
    assert exit_code == 3
    assert payload["args"] == ["whoami", "-o", "json"]
    assert payload["token"] == "<redacted>" and payload["site"] == "org.atlassian.net"
    assert not {"TWG_USER", "TWG_TOKEN", "TWG_SITE"} & set(os.environ)
    assert b"secret-token" not in out + err and b"me@x.com" not in out + err


def test_config_equals_form_is_accepted(fake_twg, tmp_path, capsysbinary):
    config = _config(tmp_path, cloudId="https://org.atlassian.net")

    twg.main([f"--config={config}", "whoami"], config_path=tmp_path / "unused.json")

    assert json.loads(capsysbinary.readouterr().out)["args"] == ["whoami"]


@pytest.mark.parametrize("content", ["{not json", "[1, 2]", "\udcff"])
def test_malformed_config_prints_only_the_safe_message(fake_twg, tmp_path, capsys, content):
    config = tmp_path / "bad.json"
    if content == "\udcff":
        config.write_bytes(b"\xff\xfe secret-token")
    else:
        config.write_text(content + ' "secret-token"')

    exit_code = twg.main(["--config", str(config), "whoami"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.err == "error: unreadable or malformed Atlassian config\n"
    assert "secret-token" not in captured.out + captured.err


def test_script_runs_from_any_cwd_and_forwards_the_exit_code(fake_twg, tmp_path):
    config = _config(tmp_path, email="me@x.com", apiToken="secret-token", cloudId="org.atlassian.net")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--config", str(config), "jira", "workitem", "query"],
        cwd=elsewhere,
        capture_output=True,
        env=os.environ.copy(),
    )

    assert result.returncode == 3
    assert json.loads(result.stdout)["args"] == ["jira", "workitem", "query"]
    assert b"secret-token" not in result.stdout + result.stderr
    assert b"me@x.com" not in result.stdout + result.stderr


def test_default_config_resolves_beside_skill_md_not_the_cwd():
    assert twg.CONFIG_PATH == SCRIPT.resolve().parents[1] / ".atlassian.json.user"
