from unittest.mock import patch

import pytest

from zdesign_publisher.env import get_confluence, load_env


def write_env(tmp_path, content: str):
    p = tmp_path / ".atlmcp.env"
    p.write_text(content)
    return str(p)


def test_load_env_parses_key_value_pairs(tmp_path):
    path = write_env(
        tmp_path,
        '# comment\nACLI_SITE="example.atlassian.net"\nACLI_EMAIL=me@example.com\nACLI_API_TOKEN=secret\n',
    )
    env = load_env(path)
    assert env["ACLI_SITE"] == "example.atlassian.net"
    assert env["ACLI_EMAIL"] == "me@example.com"
    assert env["ACLI_API_TOKEN"] == "secret"


def test_load_env_ignores_blank_lines_and_comments(tmp_path):
    path = write_env(
        tmp_path,
        "\n# a comment\nACLI_SITE=site\nACLI_EMAIL=email\nACLI_API_TOKEN=token\n\n",
    )
    env = load_env(path)
    assert len(env) == 3


def test_load_env_raises_when_required_key_missing(tmp_path):
    path = write_env(tmp_path, "ACLI_SITE=site\nACLI_EMAIL=email\n")
    with pytest.raises(SystemExit, match="ACLI_API_TOKEN"):
        load_env(path)


def test_load_env_raises_when_required_key_blank(tmp_path):
    path = write_env(tmp_path, 'ACLI_SITE=site\nACLI_EMAIL=email\nACLI_API_TOKEN=""\n')
    with pytest.raises(SystemExit, match="ACLI_API_TOKEN"):
        load_env(path)


def test_get_confluence_adds_https_scheme_when_missing():
    env = {"ACLI_SITE": "example.atlassian.net", "ACLI_EMAIL": "me@example.com", "ACLI_API_TOKEN": "secret"}
    with patch("zdesign_publisher.env.Confluence") as mock_confluence:
        get_confluence(env)
    mock_confluence.assert_called_once_with(
        url="https://example.atlassian.net", username="me@example.com", password="secret", cloud=True
    )


def test_get_confluence_leaves_existing_scheme_alone():
    env = {"ACLI_SITE": "http://example.atlassian.net", "ACLI_EMAIL": "me@example.com", "ACLI_API_TOKEN": "secret"}
    with patch("zdesign_publisher.env.Confluence") as mock_confluence:
        get_confluence(env)
    assert mock_confluence.call_args.kwargs["url"] == "http://example.atlassian.net"
