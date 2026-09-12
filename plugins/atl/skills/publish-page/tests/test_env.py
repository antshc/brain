import pytest

from page_diagrams.env import (
    find_config,
    load_credentials,
    load_drawio_extension_key,
    load_renderer,
    load_swimlane_drawio_enabled,
    parse_config,
)


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


def test_load_renderer_returns_configured_value(tmp_path):
    (tmp_path / ".atlassian").write_text("ATLASSIAN_DIAGRAM_RENDERER=drawio\n")
    assert load_renderer(str(tmp_path)) == "drawio"


def test_load_renderer_defaults_to_png_when_key_absent(tmp_path):
    (tmp_path / ".atlassian").write_text("ATLASSIAN_SITE=example.atlassian.net\n")
    assert load_renderer(str(tmp_path)) == "png"


def test_load_renderer_defaults_to_png_when_config_absent(tmp_path):
    assert load_renderer(str(tmp_path)) == "png"


def test_load_renderer_rejects_unknown_value_naming_the_alternatives(tmp_path):
    (tmp_path / ".atlassian").write_text("ATLASSIAN_DIAGRAM_RENDERER=svg\n")
    with pytest.raises(ValueError) as exc:
        load_renderer(str(tmp_path))
    assert "svg" in str(exc.value)
    assert "png, drawio, mermaid" in str(exc.value)


def test_load_drawio_extension_key_returns_configured_value(tmp_path):
    (tmp_path / ".atlassian").write_text("ATLASSIAN_DRAWIO_EXTENSION_KEY=app-1/env-1/static/drawio\n")
    assert load_drawio_extension_key(str(tmp_path)) == "app-1/env-1/static/drawio"


@pytest.mark.parametrize("value", ["true", "True", "1", "yes"])
def test_load_swimlane_drawio_enabled_returns_true_for_truthy_values(tmp_path, value):
    (tmp_path / ".atlassian").write_text(f"ATLASSIAN_SWIMLANE_DRAWIO={value}\n")
    assert load_swimlane_drawio_enabled(str(tmp_path)) is True


@pytest.mark.parametrize("value", ["false", "False", "0", "no"])
def test_load_swimlane_drawio_enabled_returns_false_for_falsy_values(tmp_path, value):
    (tmp_path / ".atlassian").write_text(f"ATLASSIAN_SWIMLANE_DRAWIO={value}\n")
    assert load_swimlane_drawio_enabled(str(tmp_path)) is False


def test_load_swimlane_drawio_enabled_defaults_to_true_when_key_absent(tmp_path):
    (tmp_path / ".atlassian").write_text("ATLASSIAN_SITE=example.atlassian.net\n")
    assert load_swimlane_drawio_enabled(str(tmp_path)) is True


def test_load_swimlane_drawio_enabled_defaults_to_true_when_config_absent(tmp_path):
    assert load_swimlane_drawio_enabled(str(tmp_path)) is True


def test_load_drawio_extension_key_names_the_key_and_where_to_find_it_when_absent(tmp_path):
    (tmp_path / ".atlassian").write_text("ATLASSIAN_DIAGRAM_RENDERER=drawio\n")
    with pytest.raises(ValueError) as exc:
        load_drawio_extension_key(str(tmp_path))
    assert "ATLASSIAN_DRAWIO_EXTENSION_KEY" in str(exc.value)
    assert "extensionKey" in str(exc.value)


@pytest.mark.parametrize("value", ["drawio", "app-1/static/drawio", "app-1/env-1/static/drawio/extra"])
def test_load_drawio_extension_key_rejects_a_malformed_value(tmp_path, value):
    (tmp_path / ".atlassian").write_text(f"ATLASSIAN_DRAWIO_EXTENSION_KEY={value}\n")
    with pytest.raises(ValueError, match="malformed"):
        load_drawio_extension_key(str(tmp_path))
