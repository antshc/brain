import json

from preflight_atl.cli import main


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
    }


def test_main_prints_resolved_facts_without_echoing_the_token(tmp_path, capsys):
    (tmp_path / ".atlassian").write_text(
        "ATLASSIAN_SITE=example.atlassian.net\nATLASSIAN_EMAIL=me@example.com\n"
        "ATLASSIAN_API_TOKEN=super-secret-token\nATLASSIAN_JIRA_PROJECT_KEYS=PROJ\n"
        "ATLASSIAN_CONFLUENCE_SPACE_IDS=12345\n"
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
