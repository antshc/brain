from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest
from requests.exceptions import HTTPError

from atl_cli.page_operations import rename_page


def _page(title: str, version: int, body: dict | None = None) -> dict:
    body = body or {"type": "doc", "version": 1, "content": []}
    return {
        "id": "42",
        "title": title,
        "version": {"number": version},
        "body": {"atlas_doc_format": {"value": json.dumps(body)}},
    }


def test_rename_page_updates_with_live_body_and_verifies(monkeypatch):
    confluence = MagicMock()
    body = {"type": "doc", "version": 1, "content": [{"type": "paragraph"}]}
    confluence.get.side_effect = [_page("Old", 7, body), _page("New", 8, body)]

    result = rename_page(confluence, "42", "New", "https://example.atlassian.net")

    payload = confluence.put.call_args.kwargs["data"]
    assert payload["title"] == "New"
    assert json.loads(payload["body"]["value"]) == body
    assert payload["version"] == {"number": 8}
    assert result["previousTitle"] == "Old"
    assert result["changed"] is True


def test_rename_page_retries_a_version_only_conflict(monkeypatch):
    confluence = MagicMock()
    body = {"type": "doc", "version": 1, "content": []}
    response = MagicMock(status_code=409)
    confluence.get.side_effect = [
        _page("Old", 3, body),
        _page("Old", 4, body),
        _page("New", 5, body),
    ]
    confluence.put.side_effect = [HTTPError("conflict", response=response), {"id": "42"}]

    result = rename_page(confluence, "42", "New", "https://example.atlassian.net")

    assert [value.kwargs["data"]["version"]["number"] for value in confluence.put.call_args_list] == [4, 5]
    assert result["version"] == 5


def test_rename_page_refuses_a_conflict_after_content_changed():
    confluence = MagicMock()
    response = MagicMock(status_code=409)
    confluence.get.side_effect = [
        _page("Old", 3),
        _page("Old", 4, {"type": "doc", "version": 1, "content": [{"type": "rule"}]}),
    ]
    confluence.put.side_effect = HTTPError("conflict", response=response)

    with pytest.raises(RuntimeError, match="changed concurrently"):
        rename_page(confluence, "42", "New", "https://example.atlassian.net")

    assert confluence.put.call_count == 1


def test_rename_page_same_title_is_read_only():
    confluence = MagicMock()
    confluence.get.return_value = _page("Same", 2)

    result = rename_page(confluence, "42", "Same", "https://example.atlassian.net")

    assert result["changed"] is False
    confluence.put.assert_not_called()


def test_rename_page_refuses_a_non_object_body():
    confluence = MagicMock()
    confluence.get.return_value = {
        "title": "Old",
        "version": {"number": 2},
        "body": {"atlas_doc_format": {"value": "not-json"}},
    }

    with pytest.raises(ValueError, match="not parsed ADF"):
        rename_page(confluence, "42", "New", "https://example.atlassian.net")

    confluence.put.assert_not_called()
