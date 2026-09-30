import json

import pytest

from env import load_credentials


def config_path(tmp_path) -> str:
    return str(tmp_path / ".atlassian.json.user")


def write_config(tmp_path, data: dict):
    (tmp_path / ".atlassian.json.user").write_text(json.dumps(data))


def test_load_credentials_returns_site_email_token(tmp_path):
    write_config(
        tmp_path,
        {
            "site": "example.atlassian.net",
            "email": "me@example.com",
            "apiToken": "super-secret-token",
        },
    )
    creds = load_credentials(config_path(tmp_path))
    assert creds == {
        "site": "example.atlassian.net",
        "email": "me@example.com",
        "token": "super-secret-token",
    }


@pytest.mark.parametrize(
    "data",
    [
        {"site": "example.atlassian.net"},
        {},
    ],
)
def test_load_credentials_returns_none_instead_of_raising_when_incomplete(tmp_path, data):
    if data:
        write_config(tmp_path, data)
    assert load_credentials(config_path(tmp_path)) is None


def test_load_credentials_returns_none_when_config_absent(tmp_path):
    assert load_credentials(config_path(tmp_path)) is None
