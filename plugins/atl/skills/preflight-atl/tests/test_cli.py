import json

from preflight_atl.cli import main


def write_settings(tmp_path, atl: dict, credentials: dict | None = None) -> None:
    data: dict = {"atl": atl}
    if credentials is not None:
        data["credentials"] = {"atl": credentials}
    (tmp_path / ".harness.json.user").write_text(json.dumps(data))


def test_main_prints_empty_fields_as_json_when_config_absent(tmp_path, capsys):
    main(["--root", str(tmp_path)])
    facts = json.loads(capsys.readouterr().out)
    assert facts == {
        "site": "",
        "cloudId": "",
        "defaultProjectKey": "",
        "defaultSpaceId": "",
        "tokenAvailable": False,
        "mcpConnected": False,
        "accountId": "",
        "displayName": "",
    }


def test_main_prints_resolved_facts_without_echoing_the_token(tmp_path, capsys):
    write_settings(
        tmp_path,
        atl={"site": "example.atlassian.net", "jira_project_keys": ["PROJ"], "confluence_space_ids": ["12345"]},
        credentials={"email": "me@example.com", "api_token": "super-secret-token"},
    )
    main(["--root", str(tmp_path)])
    raw_out = capsys.readouterr().out
    facts = json.loads(raw_out)

    assert facts["site"] == "example.atlassian.net"
    assert facts["cloudId"] == "https://example.atlassian.net"
    assert facts["defaultProjectKey"] == "PROJ"
    assert facts["defaultSpaceId"] == "12345"
    assert facts["tokenAvailable"] is True
    assert "super-secret-token" not in raw_out
    assert "me@example.com" not in raw_out
