from unittest.mock import MagicMock

import pytest
import requests

from atl_cli import confluence_client
from atl_cli.confluence_client import error_label, get_confluence, installed_version, version_error, wiki_url

CREDENTIALS = {"site": "https://s.example", "email": "me@example.com", "token": "super-secret-token"}


def _response(status: int) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response._content = b'{"results": []}'
    response.headers["Content-Type"] = "application/json"
    response.encoding = "utf-8"
    return response


@pytest.mark.parametrize(
    "site, expected",
    [
        ("https://s.example", "https://s.example/wiki"),
        ("https://s.example/", "https://s.example/wiki"),
        ("s.example", "https://s.example/wiki"),
        ("https://s.example/wiki", "https://s.example/wiki"),
    ],
)
def test_wiki_url_makes_the_wiki_context_explicit(site, expected):
    assert wiki_url(site) == expected


@pytest.mark.parametrize("found", ["5.0.5", "5.1.0", "6.0.0"])
def test_version_error_accepts_the_supported_range(found):
    assert version_error(found) is None


@pytest.mark.parametrize("found", ["4.0.7", "5.0.4", None])
def test_version_error_names_range_found_version_and_init_atl(found):
    message = version_error(found)

    assert message == f"atlassian-python-api >=5.0.5 required, found {found or 'none'}; follow Brain's plugins/atl/install/install.md in Copilot CLI"


def test_get_confluence_exits_with_the_version_message_on_an_unsupported_library(monkeypatch):
    monkeypatch.setattr("atl_cli.config.installed_version", lambda: "4.0.7")

    with pytest.raises(SystemExit) as excinfo:
        get_confluence(CREDENTIALS)

    assert str(excinfo.value) == "atlassian-python-api >=5.0.5 required, found 4.0.7; follow Brain's plugins/atl/install/install.md in Copilot CLI"


@pytest.mark.skipif(version_error(installed_version()) is not None, reason="needs the supported atlassian-python-api")
@pytest.mark.parametrize(
    "path, expected",
    [
        ("/api/v2/pages/123", "https://s.example/wiki/api/v2/pages/123"),
        ("/rest/api/content/123/child/attachment", "https://s.example/wiki/rest/api/content/123/child/attachment"),
        ("/download/attachments/123/a.png", "https://s.example/wiki/download/attachments/123/a.png"),
    ],
)
def test_raw_paths_resolve_under_the_wiki_context(path, expected):
    confluence = get_confluence(CREDENTIALS)
    seen = []
    confluence._session.request = lambda method, url, **kwargs: seen.append(url) or _response(200)

    confluence.get(path)

    assert seen == [expected]


@pytest.mark.parametrize(
    "status, expected",
    [
        (404, "HTTPError 404: check site URL and page id; wrong API base?"),
        (401, "HTTPError 401: check email/apiToken"),
        (403, "HTTPError 403: check email/apiToken"),
        (500, "HTTPError 500"),
    ],
)
def test_error_label_names_class_status_and_hint_only(status, expected):
    exception = requests.HTTPError("https://s.example/wiki/x?token=super-secret-token", response=_response(status))

    assert error_label(exception) == expected


def test_error_label_without_a_response_is_the_class_name():
    exception = requests.HTTPError("https://s.example/?token=abc")
    exception.response = None

    assert error_label(exception) == "HTTPError"
    assert error_label(requests.ConnectionError(MagicMock())) == "ConnectionError"
