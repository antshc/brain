"""`comment_links.py`: Confluence page references become smart-link cards in a Jira comment."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from atl_cli import comment_links
from atl_cli.comment_links import page_resolver, with_page_cards

CREDENTIALS = {"site": "org.atlassian.net", "email": "me@x.com", "token": "secret-token"}
PAGE_URL = "https://org.atlassian.net/wiki/spaces/ZIC/pages/42/Title"


def test_numeric_id_resolves_to_the_canonical_page_url(monkeypatch):
    seen = {}

    def get(url, **kwargs):
        seen.update(url=url, **kwargs)
        return SimpleNamespace(status_code=200, json=lambda: {"_links": {"base": "https://org.atlassian.net/wiki", "webui": "/spaces/ZIC/pages/42/Title"}})

    monkeypatch.setattr(comment_links.requests, "get", get)

    assert page_resolver(CREDENTIALS)("42") == PAGE_URL
    assert seen["url"] == "https://org.atlassian.net/wiki/api/v2/pages/42"
    assert seen["auth"] == ("me@x.com", "secret-token")


def test_a_page_url_on_the_site_is_used_as_given_without_a_lookup(monkeypatch):
    monkeypatch.setattr(comment_links.requests, "get", lambda *args, **kwargs: pytest.fail("no lookup expected"))

    assert page_resolver(CREDENTIALS)(PAGE_URL) == PAGE_URL


@pytest.mark.parametrize("reference", ["https://evil.example/wiki/spaces/X/pages/1/T", "https://org.atlassian.net/browse/ABC-1", "ftp://org.atlassian.net/wiki/x", "Some title"])
def test_other_hosts_non_pages_and_titles_are_rejected(reference):
    with pytest.raises(ValueError, match="not a Confluence page URL"):
        page_resolver(CREDENTIALS)(reference)


def test_a_missing_page_id_is_reported(monkeypatch):
    monkeypatch.setattr(comment_links.requests, "get", lambda *args, **kwargs: SimpleNamespace(status_code=404, json=lambda: {}))

    with pytest.raises(ValueError, match="page 9 not found.*404"):
        page_resolver(CREDENTIALS)("9")


def test_with_page_cards_adds_one_card_paragraph_per_page_without_mutating_the_body():
    body = {"type": "doc", "version": 1, "content": [{"type": "paragraph"}]}

    result = with_page_cards(body, [PAGE_URL, PAGE_URL + "2"])

    assert result["content"][1:] == [
        {"type": "paragraph", "content": [{"type": "inlineCard", "attrs": {"url": PAGE_URL}}]},
        {"type": "paragraph", "content": [{"type": "inlineCard", "attrs": {"url": PAGE_URL + "2"}}]},
    ]
    assert body["content"] == [{"type": "paragraph"}]
