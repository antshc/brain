"""Inline-comment guard: detect open comments an update detaches and leave one notice."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from page_diagrams import comment_guard
from page_diagrams.pipeline import publish
from requests.exceptions import ConnectionError as RequestsConnectionError

CREDS = {"site": "s.example", "email": "e", "token": "t"}


def _ann(comment_id: str) -> dict:
    return {"type": "annotation", "attrs": {"annotationType": "inlineComment", "id": comment_id}}


def _doc(*ids: str) -> dict:
    return {
        "type": "doc",
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": f"t{i}", "marks": [_ann(i)]} for i in ids]}],
    }


def _comment(cid: str, ref: str, status: str = "open") -> dict:
    return {
        "id": cid,
        "resolutionStatus": status,
        "properties": {"inlineMarkerRef": ref, "inlineOriginalSelection": f"text {ref}"},
        "body": {"storage": {"value": "<p>why <b>this</b> &amp; that</p>"}},
        "version": {"authorId": "acc"},
        "_links": {"webui": f"/spaces/S/pages/1/T?focusedCommentId={cid}"},
    }


class _FakeConfluence:
    def __init__(self, live_ids: tuple[str, ...], comments: list[dict]) -> None:
        self.live = _doc(*live_ids)
        self.comments = comments
        self.posted: list[dict] = []

    def get(self, path: str, params: dict | None = None) -> dict:
        if path == "/api/v2/pages/1":
            return {"body": {"atlas_doc_format": {"value": json.dumps(self.live)}}}
        if path == "/api/v2/pages/1/inline-comments":
            return {"results": self.comments[:1], "_links": {"next": "/wiki/api/v2/pages/1/inline-comments?cursor=2"}}
        if path == "/api/v2/pages/1/inline-comments?cursor=2":
            return {"results": self.comments[1:]}
        if path == "/rest/api/user":
            return {"displayName": "Ann"}
        raise AssertionError(path)

    def post(self, path: str, data: dict) -> dict:
        self.posted.append({"path": path, **data})
        return {"id": "999"}


def test_comment_ids_finds_marks_at_any_depth_and_ignores_other_annotations():
    other = {"type": "annotation", "attrs": {"annotationType": "other", "id": "z"}}
    adf = {"type": "doc", "content": [{"type": "table", "content": [_doc("a"), {"type": "text", "text": "x", "marks": [other]}]}]}
    assert comment_guard.comment_ids(adf) == {"a"}


@pytest.mark.real_comment_guard
def test_plan_reports_only_open_comments_anchored_now_and_dropped_by_the_update():
    comments = [
        _comment("10", "kept"),
        _comment("11", "dropped"),
        _comment("12", "already-orphaned"),
        _comment("13", "resolved", status="resolved"),
    ]
    confluence = _FakeConfluence(("kept", "dropped", "resolved"), comments)
    guard = comment_guard.plan(confluence, "1", _doc("kept", "typo"))
    assert [c["markerRef"] for c in guard["orphaned"]] == ["dropped"]
    assert guard["orphaned"][0] == {
        "id": "11",
        "markerRef": "dropped",
        "selection": "text dropped",
        "author": "Ann",
        "excerpt": "why this & that",
        "link": "/spaces/S/pages/1/T?focusedCommentId=11",
    }
    assert guard["unknownIds"] == ["typo"]


def test_notice_storage_escapes_and_explains():
    orphan = {"id": "11", "markerRef": "r1", "selection": "<a&b>", "author": "Ann", "excerpt": "x", "link": "/p?focusedCommentId=11"}
    storage = comment_guard.notice_storage([orphan], "https://s.example/wiki")
    assert "1 open inline comment." in storage
    assert "&lt;a&amp;b&gt;" in storage
    assert 'href="https://s.example/wiki/p?focusedCommentId=11"' in storage
    assert "<code>r1</code>" in storage
    assert "&lt;!-- adf:comment id=\"ANCHOR-ID\" --&gt;" in storage


def _write_md(tmp_path, body: str):
    md = tmp_path / "page.md"
    md.write_text(f"# T\n\n{body}\n")
    return md


def _publish(tmp_path, md, page_id: str | None = "1") -> dict:
    return publish(
        md_path=str(md),
        config_path=str(tmp_path / "cfg.json"),
        page_id=page_id,
        space_id=None if page_id else "S",
        title=None,
        assets_dir=str(tmp_path / "assets"),
        out_path=str(tmp_path / "final.json"),
    )


@pytest.mark.real_comment_guard
def test_rest_update_posts_one_notice_after_publishing(tmp_path):
    confluence = _FakeConfluence(("kept", "dropped"), [_comment("10", "kept"), _comment("11", "dropped")])
    md = _write_md(tmp_path, '<!-- adf:comment id="kept" -->a<!-- /adf:comment --> b')
    with patch("page_diagrams.pipeline.load_credentials", return_value=CREDS), patch(
        "page_diagrams.pipeline.get_confluence", return_value=confluence
    ), patch("page_diagrams.pipeline.get_page_version", return_value=3), patch(
        "page_diagrams.pipeline.update_page_adf"
    ) as update:
        result = _publish(tmp_path, md)
    update.assert_called_once()
    published = update.call_args.args[3]
    assert comment_guard.comment_ids(published) == {"kept"}
    assert result["orphanedComments"] == [{"id": "11", "markerRef": "dropped", "selection": "text dropped"}]
    assert result["orphanNoticeCommentId"] == "999"
    assert confluence.posted[0]["path"] == "/api/v2/footer-comments"
    assert confluence.posted[0]["pageId"] == "1"


@pytest.mark.real_comment_guard
def test_update_keeping_every_anchor_posts_nothing(tmp_path):
    confluence = _FakeConfluence(("kept",), [_comment("10", "kept")])
    md = _write_md(tmp_path, 'edited <!-- adf:comment id="kept" -->a<!-- /adf:comment -->')
    with patch("page_diagrams.pipeline.load_credentials", return_value=CREDS), patch(
        "page_diagrams.pipeline.get_confluence", return_value=confluence
    ), patch("page_diagrams.pipeline.get_page_version", return_value=3), patch("page_diagrams.pipeline.update_page_adf"):
        result = _publish(tmp_path, md)
    assert "orphanedComments" not in result
    assert confluence.posted == []


@pytest.mark.real_comment_guard
def test_guard_read_failure_still_publishes(tmp_path):
    confluence = MagicMock()
    confluence.get.side_effect = RequestsConnectionError("https://x/?token=secret")
    md = _write_md(tmp_path, "plain")
    with patch("page_diagrams.pipeline.load_credentials", return_value=CREDS), patch(
        "page_diagrams.pipeline.get_confluence", return_value=confluence
    ), patch("page_diagrams.pipeline.get_page_version", return_value=3), patch("page_diagrams.pipeline.update_page_adf") as update:
        result = _publish(tmp_path, md)
    update.assert_called_once()
    assert result["commentGuard"] == "failed (ConnectionError)"


def test_guard_skips_on_create(tmp_path):
    md = _write_md(tmp_path, "plain")
    with patch("page_diagrams.pipeline.load_credentials", return_value=CREDS), patch(
        "page_diagrams.pipeline.get_confluence", return_value=MagicMock()
    ), patch("page_diagrams.pipeline.create_page_adf", return_value={"id": "5"}):
        assert "commentGuard" not in _publish(tmp_path, md, page_id=None)
