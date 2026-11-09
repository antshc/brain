import pytest
import requests

from atl_cli import confluence_client
from atl_cli.confluence_client import get_confluence, installed_version, version_error

CREDENTIALS = {"site": "s.example", "email": "e", "token": "t"}


def test_get_confluence_exits_with_the_version_message_on_an_unsupported_library(monkeypatch):
    monkeypatch.setattr("atl_cli.config.installed_version", lambda: "4.0.7")

    with pytest.raises(SystemExit) as excinfo:
        get_confluence(CREDENTIALS)

    assert str(excinfo.value) == "atlassian-python-api >=5.0.5 required, found 4.0.7; run `/atlassian install` (atlassian skill's Install tactic) in Copilot CLI"


@pytest.mark.skipif(version_error(installed_version()) is not None, reason="needs the supported atlassian-python-api")
@pytest.mark.parametrize("method", ["get", "post", "put"])
def test_v1_and_v2_paths_resolve_under_the_wiki_context(method):
    confluence = get_confluence(CREDENTIALS)
    seen = []

    def fake_request(method, url, **kwargs):
        seen.append(url)
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"id": "1"}'
        response.encoding = "utf-8"
        return response

    confluence._session.request = fake_request
    getattr(confluence, method)("/api/v2/pages/1")
    getattr(confluence, method)("/rest/api/content/1/child/attachment")

    assert seen == ["https://s.example/wiki/api/v2/pages/1", "https://s.example/wiki/rest/api/content/1/child/attachment"]
