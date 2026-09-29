import json

import pytest

from env import load_credentials, load_settings


def write_settings(tmp_path, atl: dict, credentials: dict | None = None) -> None:
    data: dict = {"atl": atl}
    if credentials is not None:
        data["credentials"] = {"atl": credentials}
    (tmp_path / ".harness.json.user").write_text(json.dumps(data))


def test_load_settings_returns_empty_dict_when_absent(tmp_path):
    assert load_settings(str(tmp_path)) == {}


def test_load_settings_merges_atl_and_credentials_atl(tmp_path):
    write_settings(tmp_path, atl={"site": "example.atlassian.net"}, credentials={"email": "me@example.com"})

    values = load_settings(str(tmp_path))

    assert values["site"] == "example.atlassian.net"
    assert values["email"] == "me@example.com"


def test_load_credentials_returns_site_email_token(tmp_path):
    write_settings(
        tmp_path,
        atl={"site": "example.atlassian.net"},
        credentials={"email": "me@example.com", "api_token": "super-secret-token"},
    )
    creds = load_credentials(str(tmp_path))
    assert creds == {
        "site": "example.atlassian.net",
        "email": "me@example.com",
        "token": "super-secret-token",
    }


@pytest.mark.parametrize(
    "atl,credentials",
    [
        ({"site": "example.atlassian.net"}, None),
        ({}, None),
    ],
)
def test_load_credentials_returns_none_instead_of_raising_when_incomplete(tmp_path, atl, credentials):
    write_settings(tmp_path, atl=atl, credentials=credentials)
    assert load_credentials(str(tmp_path)) is None
