from preflight_atl.config import find_config, load_config, parse_config


def test_find_config_returns_none_when_absent(tmp_path):
    assert find_config(str(tmp_path)) is None


def test_load_config_returns_empty_dict_when_absent(tmp_path):
    assert load_config(str(tmp_path)) == {}


def test_find_config_locates_file_nested_beneath_root(tmp_path):
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    config_path = nested / ".atlassian"
    config_path.write_text("ATLASSIAN_SITE=example.atlassian.net\n")

    assert find_config(str(tmp_path)) == str(config_path)


def test_find_config_ignores_file_above_root(tmp_path):
    above = tmp_path / "above"
    root = tmp_path / "above" / "root"
    root.mkdir(parents=True)
    (above / ".atlassian").write_text("ATLASSIAN_SITE=example.atlassian.net\n")

    assert find_config(str(root)) is None
    assert load_config(str(root)) == {}


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


def test_parse_config_ignores_blank_lines_and_comments(tmp_path):
    path = tmp_path / ".atlassian"
    path.write_text("\n# a comment\nATLASSIAN_SITE=site\n\n")
    assert parse_config(str(path)) == {"ATLASSIAN_SITE": "site"}
