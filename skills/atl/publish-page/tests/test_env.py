from page_diagrams.env import find_config, load_credentials, parse_config


def test_find_config_returns_none_when_absent(tmp_path):
    assert find_config(str(tmp_path)) is None


def test_find_config_locates_file_nested_beneath_root(tmp_path):
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    config_path = nested / ".atlassian"
    config_path.write_text("ATLASSIAN_SITE=example.atlassian.net\n")

    assert find_config(str(tmp_path)) == str(config_path)


def test_parse_config_parses_key_value_pairs(tmp_path):
    path = tmp_path / ".atlassian"
    path.write_text(
        '# comment\nATLASSIAN_SITE="example.atlassian.net"\nATLASSIAN_EMAIL=me@example.com\n'
        "ATLASSIAN_API_TOKEN=secret\n"
    )
    values = parse_config(str(path))
    assert values["ATLASSIAN_SITE"] == "example.atlassian.net"
    assert values["ATLASSIAN_EMAIL"] == "me@example.com"
    assert values["ATLASSIAN_API_TOKEN"] == "secret"


def test_load_credentials_returns_site_email_token(tmp_path):
    (tmp_path / ".atlassian").write_text(
        "ATLASSIAN_SITE=example.atlassian.net\nATLASSIAN_EMAIL=me@example.com\n"
        "ATLASSIAN_API_TOKEN=super-secret-token\n"
    )
    creds = load_credentials(str(tmp_path))
    assert creds == {
        "site": "example.atlassian.net",
        "email": "me@example.com",
        "token": "super-secret-token",
    }


def test_load_credentials_raises_naming_every_missing_key(tmp_path):
    (tmp_path / ".atlassian").write_text("ATLASSIAN_SITE=example.atlassian.net\n")
    try:
        load_credentials(str(tmp_path))
    except SystemExit as exc:
        assert "ATLASSIAN_EMAIL" in str(exc)
        assert "ATLASSIAN_API_TOKEN" in str(exc)
        assert "ATLASSIAN_SITE" not in str(exc)
    else:
        raise AssertionError("expected SystemExit")


def test_load_credentials_raises_when_config_absent(tmp_path):
    try:
        load_credentials(str(tmp_path))
    except SystemExit as exc:
        assert "ATLASSIAN_SITE" in str(exc)
    else:
        raise AssertionError("expected SystemExit")
