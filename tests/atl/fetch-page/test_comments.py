"""`comments.py` and `append_comments`: list a page's comment threads as an ignored Markdown section."""
from __future__ import annotations

import assemble_page
import pytest
from comments import (
    CommentRetrievalError,
    fetch_comment_threads,
    render_comments_section,
    storage_to_text,
)
from requests.exceptions import ConnectionError as RequestsConnectionError

_INLINE = {
    "id": "300",
    "resolutionStatus": "open",
    "properties": {"inlineMarkerRef": "ref-1", "inlineOriginalSelection": "Line 2"},
    "body": {"storage": {"value": "<p>first <b>point</b></p><p>second</p>"}},
    "version": {"authorId": "acc-1", "createdAt": "2026-10-31T14:39:59.686Z"},
    "_links": {"webui": "/spaces/S/pages/1/T?focusedCommentId=300"},
}
_REPLY = {"id": "301", "body": {"storage": {"value": "<p>agreed</p>"}}, "version": {"authorId": "acc-2", "createdAt": "2026-11-01T00:00:00Z"}}
_FOOTER = {"id": "400", "body": {"storage": {"value": "<p>page note</p>"}}, "version": {"authorId": "acc-1", "createdAt": "2026-11-02T00:00:00Z"}, "_links": {}}


class _FakeConfluence:
    def __init__(self, responses: dict[str, dict], fail: bool = False) -> None:
        self.responses = responses
        self.fail = fail
        self.calls: list[str] = []

    def get(self, path: str, params: dict | None = None) -> dict:
        self.calls.append(path)
        if self.fail:
            raise RequestsConnectionError("https://secret.example/?token=abc")
        if path == "/rest/api/user":
            return {"displayName": {"acc-1": "Ann", "acc-2": "Bob"}[params["accountId"]]}
        return self.responses.get(path, {"results": []})


def _confluence() -> _FakeConfluence:
    return _FakeConfluence(
        {
            "/api/v2/pages/1/inline-comments": {"results": [_INLINE], "_links": {"next": "/wiki/api/v2/pages/1/inline-comments?cursor=x"}},
            "/api/v2/pages/1/inline-comments?cursor=x": {"results": []},
            "/api/v2/inline-comments/300/children": {"results": [_REPLY]},
            "/api/v2/pages/1/footer-comments": {"results": [_FOOTER]},
        }
    )


def test_storage_to_text_flattens_blocks():
    assert storage_to_text("<p>first <b>point</b></p><p>second</p>") == "first point second"


def test_fetch_comment_threads_reads_inline_replies_footer_and_follows_next():
    confluence = _confluence()
    threads = fetch_comment_threads(confluence, "1")
    assert [(t["kind"], t["id"], t["markerRef"]) for t in threads] == [("inline", "300", "ref-1"), ("footer", "400", "")]
    assert threads[0]["replies"] == [{"author": "Bob", "created": "2026-11-01", "text": "agreed"}]
    assert "/api/v2/pages/1/inline-comments?cursor=x" in confluence.calls
    assert confluence.calls.count("/rest/api/user") == 2  # author names are cached


def test_fetch_comment_threads_reports_a_safe_category_only():
    with pytest.raises(CommentRetrievalError) as raised:
        fetch_comment_threads(_FakeConfluence({}, fail=True), "1")
    assert str(raised.value) == "ConnectionError"


def test_render_marks_anchored_and_unanchored_threads():
    threads = fetch_comment_threads(_confluence(), "1")
    anchored = render_comments_section(threads, 'x <!-- adf:comment id="ref-1" -->Line 2<!-- /adf:comment -->', "https://s")
    assert anchored.startswith("<!-- adf:ignore:start -->\n## Comments")
    assert anchored.endswith("<!-- adf:ignore:end -->\n")
    assert '### Inline on "Line 2" — open, anchored as `id="ref-1"`' in anchored
    assert "- **Ann** (2026-10-31): first point second" in anchored
    assert "  - **Bob** (2026-11-01): agreed" in anchored
    assert "- [Open in Confluence](https://s/wiki/spaces/S/pages/1/T?focusedCommentId=300)" in anchored
    assert "### Page comment" in anchored
    assert "**not anchored in the body**" in render_comments_section(threads, "plain body", "https://s")


def test_render_is_empty_without_comments():
    assert render_comments_section([], "body", "https://s") == ""


def test_append_comments_skip_never_reads_credentials(monkeypatch):
    monkeypatch.setattr(assemble_page, "load_credentials", lambda _: pytest.fail("credential lookup"))
    assert assemble_page.append_comments("body\n", "1", "cfg", "skip") == "body\n"


def test_append_comments_without_token_notes_only_when_body_has_anchors(monkeypatch):
    monkeypatch.setattr(assemble_page, "load_credentials", lambda _: None)
    assert assemble_page.append_comments("body\n", "1", "cfg") == "body\n"
    anchored = assemble_page.append_comments('<!-- adf:comment id="r" -->x<!-- /adf:comment -->\n', "1", "cfg")
    assert "Comments not listed: set apiToken in .atlassian.json.user to list them." in anchored


def test_append_comments_appends_section_or_failure_note(monkeypatch):
    monkeypatch.setattr(assemble_page, "load_credentials", lambda _: {"site": "s.example", "email": "e", "token": "t"})
    monkeypatch.setattr(assemble_page, "get_confluence", lambda _: _confluence())
    listed = assemble_page.append_comments("# T\n\nbody\n", "1", "cfg")
    assert listed.startswith("# T\n\nbody\n\n<!-- adf:ignore:start -->\n## Comments")
    assert "https://s.example/wiki/spaces/S/pages/1/T" in listed

    monkeypatch.setattr(assemble_page, "get_confluence", lambda _: _FakeConfluence({}, fail=True))
    failed = assemble_page.append_comments("body\n", "1", "cfg")
    assert "Comments not listed: comment retrieval failed (ConnectionError)." in failed
    assert "secret" not in failed
