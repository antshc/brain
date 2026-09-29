import json

import pytest

from preflight_atl.config import config_path, load_config


def write_settings(tmp_path, data: dict) -> None:
    (tmp_path / ".harness.json.user").write_text(json.dumps(data))


def test_config_path_raises_on_empty_root():
    with pytest.raises(ValueError):
        config_path("")


def test_load_config_returns_empty_dict_when_file_absent(tmp_path):
    assert load_config(str(tmp_path)) == {}


def test_load_config_merges_atl_and_credentials_atl(tmp_path):
    write_settings(tmp_path, {
        "atl": {"site": "example.atlassian.net", "jira_project_keys": ["PROJ"]},
        "credentials": {"atl": {"api_token": "secret", "email": "me@example.com"}},
    })

    config = load_config(str(tmp_path))

    assert config["site"] == "example.atlassian.net"
    assert config["jira_project_keys"] == ["PROJ"]
    assert config["api_token"] == "secret"
    assert config["email"] == "me@example.com"


def test_load_config_ignores_other_plugins_sections(tmp_path):
    write_settings(tmp_path, {"harness": {"repos": []}, "atl": {"site": "x"}})

    assert load_config(str(tmp_path)) == {"site": "x"}


def test_load_config_does_not_search_ancestors(tmp_path):
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    write_settings(tmp_path, {"atl": {"site": "outer"}})

    assert load_config(str(nested)) == {}
