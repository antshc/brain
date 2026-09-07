from preflight_atl.resolve import derive_cloud_id, resolve


def write_config(tmp_path, content: str):
    (tmp_path / ".atlassian").write_text(content)


def test_resolve_returns_empty_fields_when_config_absent(tmp_path):
    facts = resolve(str(tmp_path))
    assert facts == {
        "site": "",
        "cloudId": "",
        "defaultProjectKey": "",
        "defaultSpaceId": "",
        "tokenAvailable": False,
        "mcpConnected": False,
    }


def test_resolve_reports_site_and_default_project_key_from_nested_config(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / ".atlassian").write_text(
        "ATLASSIAN_SITE=example.atlassian.net\nATLASSIAN_JIRA_PROJECT_KEYS=PROJ\n"
    )
    facts = resolve(str(tmp_path))
    assert facts["site"] == "example.atlassian.net"
    assert facts["defaultProjectKey"] == "PROJ"


def test_resolve_uses_first_of_three_jira_project_keys(tmp_path):
    write_config(tmp_path, "ATLASSIAN_JIRA_PROJECT_KEYS=ONE, TWO, THREE\n")
    assert resolve(str(tmp_path))["defaultProjectKey"] == "ONE"


def test_resolve_uses_first_of_three_confluence_space_ids(tmp_path):
    write_config(tmp_path, "ATLASSIAN_CONFLUENCE_SPACE_IDS=111, 222, 333\n")
    assert resolve(str(tmp_path))["defaultSpaceId"] == "111"


def test_resolve_derives_cloud_id_from_site_without_a_lookup():
    assert derive_cloud_id("example.atlassian.net") == "https://example.atlassian.net"
    assert derive_cloud_id("https://example.atlassian.net") == "https://example.atlassian.net"
    assert derive_cloud_id("") == ""


def test_resolve_reports_token_available_when_token_present(tmp_path):
    write_config(tmp_path, "ATLASSIAN_API_TOKEN=secret\n")
    assert resolve(str(tmp_path))["tokenAvailable"] is True


def test_resolve_reports_token_unavailable_when_absent_or_blank(tmp_path):
    assert resolve(str(tmp_path))["tokenAvailable"] is False

    write_config(tmp_path, 'ATLASSIAN_API_TOKEN=""\n')
    assert resolve(str(tmp_path))["tokenAvailable"] is False


def test_resolve_never_echoes_the_token_or_email_value(tmp_path):
    write_config(
        tmp_path,
        "ATLASSIAN_SITE=example.atlassian.net\nATLASSIAN_EMAIL=me@example.com\n"
        "ATLASSIAN_API_TOKEN=super-secret-token\n",
    )
    facts = resolve(str(tmp_path))
    assert "me@example.com" not in facts.values()
    assert "super-secret-token" not in facts.values()
    assert "super-secret-token" not in str(facts)
