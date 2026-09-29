import json

from preflight_atl.resolve import derive_cloud_id, resolve


def write_settings(tmp_path, atl: dict | None = None, credentials: dict | None = None) -> None:
    data: dict = {}
    if atl is not None:
        data["atl"] = atl
    if credentials is not None:
        data["credentials"] = {"atl": credentials}
    (tmp_path / ".harness.json.user").write_text(json.dumps(data))


def test_resolve_returns_empty_fields_when_config_absent(tmp_path):
    facts = resolve(str(tmp_path))
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


def test_resolve_reports_cached_identity_from_config(tmp_path):
    write_settings(tmp_path, atl={"account_id": "63f4d6193ec8aa51d3d20548", "display_name": "Anton Shcherbyna"})
    facts = resolve(str(tmp_path))
    assert facts["accountId"] == "63f4d6193ec8aa51d3d20548"
    assert facts["displayName"] == "Anton Shcherbyna"


def test_resolve_reports_site_and_default_project_key_from_config(tmp_path):
    write_settings(tmp_path, atl={"site": "example.atlassian.net", "jira_project_keys": ["PROJ"]})
    facts = resolve(str(tmp_path))
    assert facts["site"] == "example.atlassian.net"
    assert facts["defaultProjectKey"] == "PROJ"


def test_resolve_uses_first_of_three_jira_project_keys(tmp_path):
    write_settings(tmp_path, atl={"jira_project_keys": ["ONE", "TWO", "THREE"]})
    assert resolve(str(tmp_path))["defaultProjectKey"] == "ONE"


def test_resolve_uses_first_of_three_confluence_space_ids(tmp_path):
    write_settings(tmp_path, atl={"confluence_space_ids": ["111", "222", "333"]})
    assert resolve(str(tmp_path))["defaultSpaceId"] == "111"


def test_resolve_derives_cloud_id_from_site_without_a_lookup():
    assert derive_cloud_id("example.atlassian.net") == "https://example.atlassian.net"
    assert derive_cloud_id("https://example.atlassian.net") == "https://example.atlassian.net"
    assert derive_cloud_id("") == ""


def test_resolve_reports_token_available_when_token_present(tmp_path):
    write_settings(tmp_path, credentials={"api_token": "secret"})
    assert resolve(str(tmp_path))["tokenAvailable"] is True


def test_resolve_reports_token_unavailable_when_absent_or_blank(tmp_path):
    assert resolve(str(tmp_path))["tokenAvailable"] is False

    write_settings(tmp_path, credentials={"api_token": ""})
    assert resolve(str(tmp_path))["tokenAvailable"] is False


def test_resolve_never_echoes_the_token_or_email_value(tmp_path):
    write_settings(
        tmp_path,
        atl={"site": "example.atlassian.net"},
        credentials={"email": "me@example.com", "api_token": "super-secret-token"},
    )
    facts = resolve(str(tmp_path))
    assert "me@example.com" not in facts.values()
    assert "super-secret-token" not in facts.values()
    assert "super-secret-token" not in str(facts)
