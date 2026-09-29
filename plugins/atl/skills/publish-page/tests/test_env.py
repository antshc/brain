import json

import pytest

from page_diagrams.env import (
    load_credentials,
    load_drawio_extension_key,
    load_renderer,
    load_settings,
    load_swimlane_drawio_enabled,
)


def write_settings(tmp_path, atl: dict | None = None, credentials: dict | None = None) -> None:
    data: dict = {}
    if atl is not None:
        data["atl"] = atl
    if credentials is not None:
        data["credentials"] = {"atl": credentials}
    (tmp_path / ".harness.json.user").write_text(json.dumps(data))


def test_load_settings_returns_empty_dict_when_absent(tmp_path):
    assert load_settings(str(tmp_path)) == {}


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


def test_load_credentials_raises_naming_every_missing_key(tmp_path):
    write_settings(tmp_path, atl={"site": "example.atlassian.net"})
    try:
        load_credentials(str(tmp_path))
    except SystemExit as exc:
        assert "credentials.atl.email" in str(exc)
        assert "credentials.atl.api_token" in str(exc)
        assert "atl.site" not in str(exc)
    else:
        raise AssertionError("expected SystemExit")


def test_load_credentials_raises_when_config_absent(tmp_path):
    try:
        load_credentials(str(tmp_path))
    except SystemExit as exc:
        assert "atl.site" in str(exc)
    else:
        raise AssertionError("expected SystemExit")


def test_load_renderer_returns_configured_value(tmp_path):
    write_settings(tmp_path, atl={"diagram_renderer": "drawio"})
    assert load_renderer(str(tmp_path)) == "drawio"


def test_load_renderer_defaults_to_png_when_key_absent(tmp_path):
    write_settings(tmp_path, atl={"site": "example.atlassian.net"})
    assert load_renderer(str(tmp_path)) == "png"


def test_load_renderer_defaults_to_png_when_config_absent(tmp_path):
    assert load_renderer(str(tmp_path)) == "png"


def test_load_renderer_rejects_unknown_value_naming_the_alternatives(tmp_path):
    write_settings(tmp_path, atl={"diagram_renderer": "svg"})
    with pytest.raises(ValueError) as exc:
        load_renderer(str(tmp_path))
    assert "svg" in str(exc.value)
    assert "png, drawio, mermaid" in str(exc.value)


def test_load_drawio_extension_key_returns_configured_value(tmp_path):
    write_settings(tmp_path, atl={"drawio_extension_key": "app-1/env-1/static/drawio"})
    assert load_drawio_extension_key(str(tmp_path)) == "app-1/env-1/static/drawio"


@pytest.mark.parametrize("value", ["true", "True", "1", "yes"])
def test_load_swimlane_drawio_enabled_returns_true_for_truthy_values(tmp_path, value):
    write_settings(tmp_path, atl={"swimlane_drawio": value})
    assert load_swimlane_drawio_enabled(str(tmp_path)) is True


@pytest.mark.parametrize("value", ["false", "False", "0", "no"])
def test_load_swimlane_drawio_enabled_returns_false_for_falsy_values(tmp_path, value):
    write_settings(tmp_path, atl={"swimlane_drawio": value})
    assert load_swimlane_drawio_enabled(str(tmp_path)) is False


def test_load_swimlane_drawio_enabled_defaults_to_true_when_key_absent(tmp_path):
    write_settings(tmp_path, atl={"site": "example.atlassian.net"})
    assert load_swimlane_drawio_enabled(str(tmp_path)) is True


def test_load_swimlane_drawio_enabled_defaults_to_true_when_config_absent(tmp_path):
    assert load_swimlane_drawio_enabled(str(tmp_path)) is True


def test_load_drawio_extension_key_names_the_key_and_where_to_find_it_when_absent(tmp_path):
    write_settings(tmp_path, atl={"diagram_renderer": "drawio"})
    with pytest.raises(ValueError) as exc:
        load_drawio_extension_key(str(tmp_path))
    assert "drawio_extension_key" in str(exc.value)
    assert "extensionKey" in str(exc.value)


@pytest.mark.parametrize("value", ["drawio", "app-1/static/drawio", "app-1/env-1/static/drawio/extra"])
def test_load_drawio_extension_key_rejects_a_malformed_value(tmp_path, value):
    write_settings(tmp_path, atl={"drawio_extension_key": value})
    with pytest.raises(ValueError, match="malformed"):
        load_drawio_extension_key(str(tmp_path))
