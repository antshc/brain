"""`comment_state.py`: anchor, reply target, and answered state of open page comment threads."""
from __future__ import annotations

import json
from pathlib import Path

import comment_state

ME = "acc-me"
SITE = "https://example.atlassian.net"
HTML = '<p data-local-id="p1"><span class="annotation" data-annotation-id="ref-live" data-annotation-type="inlineComment">kept</span></p>'


def comment(ident, author="acc-reviewer", kind="inline", ref=None, created="2026-11-01T00:00:00Z", body="text", replies=()):
    return {
        "id": ident, "commentType": kind, "authorAccountId": author, "createdAt": created,
        "inlineMarkerRef": ref, "inlineOriginalSelection": "kept" if ref else None,
        "webUrl": f"/spaces/S/pages/1/T?focusedCommentId={ident}",
        "body": {"format": "markdown", "value": body}, "replies": list(replies),
    }


def by_id(threads):
    return {t["id"]: t for t in threads}


def test_anchored_inline_replies_in_thread():
    thread = by_id(comment_state.classify([comment("1", ref="ref-live")], HTML, ME, SITE))["1"]
    assert (thread["anchor"], thread["replyTarget"], thread["state"]) == ("anchored", "thread", "pending")
    assert thread["url"] == f"{SITE}/wiki/spaces/S/pages/1/T?focusedCommentId=1"


def test_removed_anchor_replies_on_page():
    thread = by_id(comment_state.classify([comment("1", ref="ref-gone")], HTML, ME, SITE))["1"]
    assert (thread["anchor"], thread["replyTarget"]) == ("orphaned", "page")


def test_footer_comment_replies_in_thread():
    thread = by_id(comment_state.classify([comment("1", kind="footer")], HTML, ME, SITE))["1"]
    assert (thread["anchor"], thread["replyTarget"]) == ("page", "thread")


def test_own_latest_reply_marks_answered():
    reply = comment("2", author=ME, created="2026-11-02T00:00:00Z")
    thread = by_id(comment_state.classify([comment("1", ref="ref-live", replies=[reply])], HTML, ME, SITE))["1"]
    assert thread["state"] == "answered"


def test_reviewer_follow_up_reopens_work():
    replies = [comment("2", author=ME, created="2026-11-02T00:00:00Z"), comment("3", created="2026-11-03T00:00:00Z")]
    thread = by_id(comment_state.classify([comment("1", ref="ref-live", replies=replies)], HTML, ME, SITE))["1"]
    assert thread["state"] == "pending"
    assert [e["author"] for e in thread["comments"]] == ["other", "me", "other"]


def test_page_answer_linking_orphan_marks_answered():
    footer = comment("9", author=ME, kind="footer", created="2026-11-02T00:00:00Z", body="See focusedCommentId=1")
    threads = by_id(comment_state.classify([comment("1", ref="ref-gone"), footer], HTML, ME, SITE))
    assert threads["1"]["state"] == "answered"
    assert "9" not in threads


def test_page_answer_before_follow_up_stays_pending():
    footer = comment("9", author=ME, kind="footer", created="2026-11-02T00:00:00Z", body="focusedCommentId=1")
    follow_up = comment("2", created="2026-11-03T00:00:00Z")
    threads = by_id(comment_state.classify([comment("1", ref="ref-gone", replies=[follow_up]), footer], HTML, ME, SITE))
    assert threads["1"]["state"] == "pending"


def test_report_skips_when_nothing_pending(tmp_path: Path):
    page = tmp_path / "p1.json"
    reply = comment("2", author=ME, created="2026-11-02T00:00:00Z")
    page.write_text(json.dumps({"data": {"comments": [comment("1", ref="ref-live", replies=[reply])], "nextCursor": None}}))
    report = comment_state.build_report(comment_state.load_comment_pages([page]), HTML, ME, SITE)
    assert report["action"] == "skip"
    assert report["counts"] == {"open": 1, "pending": 0, "answered": 1, "orphaned": 0}


def test_report_stops_on_truncated_list(tmp_path: Path):
    page = tmp_path / "p1.json"
    page.write_text(json.dumps({"data": {"comments": [comment("1")], "nextCursor": "abc"}}))
    report = comment_state.build_report(comment_state.load_comment_pages([page]), HTML, ME, SITE)
    assert report["action"] == "stop"


def test_cli_rejects_empty_account(tmp_path: Path, capsys):
    page, html = tmp_path / "p1.json", tmp_path / "d.html"
    page.write_text(json.dumps({"data": {"comments": []}}))
    html.write_text(HTML)
    code = comment_state.main(["--comments", str(page), "--html", str(html), "--account-id", "", "--site", SITE])
    assert code == 2
    assert "accountId" in capsys.readouterr().err
