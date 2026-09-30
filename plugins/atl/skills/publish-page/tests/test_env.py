import json

import pytest

from page_diagrams.env import (
    load_credentials,
    load_drawio_extension_key,
    load_renderer,
    load_swimlane_drawio_enabled,
)


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


def test_load_credentials_raises_naming_every_missing_key(tmp_path):
    write_config(tmp_path, {"site": "example.atlassian.net"})
    try:
        load_credentials(config_path(tmp_path))
    except SystemExit as exc:
        assert "email" in str(exc)
        assert "apiToken" in str(exc)
        assert "site" not in str(exc)
    else:
        raise AssertionError("expected SystemExit")


def test_load_credentials_raises_when_config_absent(tmp_path):
    try:
        load_credentials(config_path(tmp_path))
    except SystemExit as exc:
        assert "site" in str(exc)
    else:
        raise AssertionError("expected SystemExit")


def test_load_renderer_returns_configured_value(tmp_path):
    write_config(tmp_path, {"diagramRenderer": "drawio"})
    assert load_renderer(config_path(tmp_path)) == "drawio"


def test_load_renderer_defaults_to_png_when_key_absent(tmp_path):
    write_config(tmp_path, {"site": "example.atlassian.net"})
    assert load_renderer(config_path(tmp_path)) == "png"


def test_load_renderer_defaults_to_png_when_config_absent(tmp_path):
    assert load_renderer(config_path(tmp_path)) == "png"


def test_load_renderer_rejects_unknown_value_naming_the_alternatives(tmp_path):
    write_config(tmp_path, {"diagramRenderer": "svg"})
    with pytest.raises(ValueError) as exc:
        load_renderer(config_path(tmp_path))
    assert "svg" in str(exc.value)
    assert "png, drawio, mermaid" in str(exc.value)


def test_load_drawio_extension_key_returns_configured_value(tmp_path):
    write_config(tmp_path, {"drawioExtensionKey": "app-1/env-1/static/drawio"})
    assert load_drawio_extension_key(config_path(tmp_path)) == "app-1/env-1/static/drawio"


@pytest.mark.parametrize("value", ["true", "True", "1", "yes"])
def test_load_swimlane_drawio_enabled_returns_true_for_truthy_values(tmp_path, value):
    write_config(tmp_path, {"swimlaneDrawio": value})
    assert load_swimlane_drawio_enabled(config_path(tmp_path)) is True


@pytest.mark.parametrize("value", ["false", "False", "0", "no"])
def test_load_swimlane_drawio_enabled_returns_false_for_falsy_values(tmp_path, value):
    write_config(tmp_path, {"swimlaneDrawio": value})
    assert load_swimlane_drawio_enabled(config_path(tmp_path)) is False


def test_load_swimlane_drawio_enabled_defaults_to_true_when_key_absent(tmp_path):
    write_config(tmp_path, {"site": "example.atlassian.net"})
    assert load_swimlane_drawio_enabled(config_path(tmp_path)) is True


def test_load_swimlane_drawio_enabled_defaults_to_true_when_config_absent(tmp_path):
    assert load_swimlane_drawio_enabled(config_path(tmp_path)) is True


def test_load_drawio_extension_key_names_the_key_and_where_to_find_it_when_absent(tmp_path):
    write_config(tmp_path, {"diagramRenderer": "drawio"})
    with pytest.raises(ValueError) as exc:
        load_drawio_extension_key(config_path(tmp_path))
    assert "drawioExtensionKey" in str(exc.value)
    assert "extensionKey" in str(exc.value)


@pytest.mark.parametrize("value", ["drawio", "app-1/static/drawio", "app-1/env-1/static/drawio/extra"])
def test_load_drawio_extension_key_rejects_a_malformed_value(tmp_path, value):
    write_config(tmp_path, {"drawioExtensionKey": value})
    with pytest.raises(ValueError, match="malformed"):
        load_drawio_extension_key(config_path(tmp_path))

