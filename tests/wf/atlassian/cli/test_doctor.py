from __future__ import annotations

import json
from unittest.mock import patch

from atl_cli.doctor import inspect_runtime, main


def test_doctor_reports_current_interpreter_packages_and_tools(tmp_path):
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"pythonPath": "/opt/atl-venv/bin/python"}))

    with patch("atl_cli.doctor._package_version", side_effect=["5.0.5", "2.32.0", "0.9.41"]), patch(
        "atl_cli.doctor.shutil.which", side_effect=["/usr/bin/twg", "/usr/bin/mmdc", "/usr/bin/drawio"]
    ):
        report = inspect_runtime(str(config))

    assert report["ok"] is True
    assert report["configuredPython"] == "/opt/atl-venv/bin/python"
    assert report["packages"]["pymarkdownlnt"] == "0.9.41"
    assert report["commands"]["twg"] == "/usr/bin/twg"


def test_doctor_returns_nonzero_and_names_missing_package(capsys):
    with patch("atl_cli.doctor._package_version", side_effect=[None, "2.32.0", None]), patch(
        "atl_cli.doctor.shutil.which", return_value=None
    ):
        exit_code = main([])

    report = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert report["ok"] is False
    assert "missing Python packages: atlassian-python-api, pymarkdownlnt" in report["problems"]
