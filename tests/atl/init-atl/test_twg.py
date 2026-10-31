from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest

import twg

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

    assert exit_code == twg.MISSING_TWG_EXIT_CODE
    assert "twg CLI not found" in capsys.readouterr().err


def test_find_twg_falls_back_to_the_default_install_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(twg.shutil, "which", lambda name: None)
    binary = tmp_path / ".local" / "bin" / "twg"
    binary.parent.mkdir(parents=True)
    binary.write_text("")

    assert twg.find_twg(home=tmp_path, local_app_data="") == str(binary)
