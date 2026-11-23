from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import HTTPError

from atl_cli import publish_work

ADF = {"type": "doc", "version": 1, "content": [{"type": "expand", "attrs": {"title": "More"}, "content": []}]}
CREDENTIALS = {"site": "https://org.atlassian.net", "email": "e", "token": "t"}


@pytest.fixture
def jira(monkeypatch):
    client = MagicMock()
    client.post.return_value = {"id": "1", "key": "ABC-7"}
    monkeypatch.setattr(publish_work, "load_credentials", lambda config_path: CREDENTIALS)
    monkeypatch.setattr(publish_work, "get_jira", lambda credentials: client)
    return client


@pytest.fixture
def adf_file(tmp_path):
    path = tmp_path / "description.json"
    path.write_text(json.dumps(ADF))
    return str(path)


def _out(capsys) -> dict:
    return json.loads(capsys.readouterr().out)


def test_build_fields_keeps_explicit_fields_over_extra():
    fields = publish_work.build_fields(
        adf=ADF, summary="S", project="ABC", issue_type="Story", parent="ABC-1", extra={"summary": "X", "labels": ["a"]}
    )

    assert fields == {
        "labels": ["a"],
        "project": {"key": "ABC"},
        "issuetype": {"name": "Story"},
        "summary": "S",
        "parent": {"key": "ABC-1"},
        "description": ADF,
    }


def test_create_posts_rest_v3_fields_and_reports_key_and_url(jira, adf_file, capsys):
    publish_work.main(
        ["create", "--config", "cfg", "--project", "ABC", "--issue-type", "Story", "--summary", "S", "--adf", adf_file]
    )

    jira.post.assert_called_once()
    path = jira.post.call_args.args[0]
    fields = jira.post.call_args.kwargs["data"]["fields"]
    assert path == "rest/api/3/issue"
    assert fields["description"] == ADF
    assert "parent" not in fields
    assert _out(capsys) == {"key": "ABC-7", "url": "https://org.atlassian.net/browse/ABC-7"}


def test_update_puts_description_without_touching_unsupplied_fields(jira, adf_file, capsys):
    publish_work.main(["update", "--config", "cfg", "--key", "ABC-3", "--adf", adf_file])

    jira.put.assert_called_once_with("rest/api/3/issue/ABC-3", data={"fields": {"description": ADF}})
    jira.post.assert_not_called()
    assert _out(capsys)["key"] == "ABC-3"


def test_attachment_failure_is_reported_without_losing_the_key(jira, adf_file, tmp_path, capsys):
    good = tmp_path / "a.png"
    good.write_bytes(b"x")
    jira.add_attachment.side_effect = [None, HTTPError("too large")]

    publish_work.main(
        ["update", "--config", "cfg", "--key", "ABC-3", "--adf", adf_file, "--attach", str(good), "--attach", str(good)]
    )

    out = _out(capsys)
    assert out["attached"] == ["a.png"]
    assert out["attachFailed"] == [{"file": "a.png", "error": "too large"}]


def test_jira_rejection_exits_with_jira_message(jira, adf_file, capsys):
    jira.post.side_effect = HTTPError("Field 'customfield_1' is required.")

    with pytest.raises(SystemExit):
        publish_work.main(
            ["create", "--config", "cfg", "--project", "ABC", "--issue-type", "Bug", "--summary", "S", "--adf", adf_file]
        )

    assert "customfield_1" in capsys.readouterr().err


def test_transport_failure_reports_only_the_exception_class(jira, adf_file, capsys):
    jira.put.side_effect = RequestsConnectionError("https://x/?token=secret")

    with pytest.raises(SystemExit):
        publish_work.main(["update", "--config", "cfg", "--key", "ABC-3", "--adf", adf_file])

    err = capsys.readouterr().err
    assert "ConnectionError" in err
    assert "secret" not in err


def test_read_adf_writes_the_live_description(jira, tmp_path, capsys):
    jira.get.return_value = {"fields": {"description": ADF}}
    out_path = tmp_path / "live.json"

    publish_work.main(["read-adf", "--config", "cfg", "--key", "ABC-3", "--out", str(out_path)])

    jira.get.assert_called_once_with("rest/api/3/issue/ABC-3", params={"fields": "description"})
    assert json.loads(out_path.read_text()) == ADF


def test_missing_credentials_fail_before_any_call(monkeypatch, adf_file, capsys):
    monkeypatch.setattr(publish_work, "load_credentials", lambda config_path: None)

    with pytest.raises(SystemExit):
        publish_work.main(["update", "--config", "cfg", "--key", "ABC-3", "--adf", adf_file])

    assert "apiToken" in capsys.readouterr().err


def test_main_prints_the_version_message_before_reading_credentials(monkeypatch):
    monkeypatch.setattr("atl_cli.config.installed_version", lambda: "4.0.7")

    with pytest.raises(SystemExit) as excinfo:
        publish_work.main(["read-adf", "--config", "cfg", "--key", "ABC-1", "--out", "x.json"])

    assert "required, found 4.0.7; run `/atlassian install` (atlassian skill's Install tactic) in Copilot CLI" in str(excinfo.value)


def test_create_accepts_markdown_and_converts_it_in_process(jira, tmp_path, capsys):
    source = tmp_path / "description.md"
    source.write_text("<details>\n<summary>More</summary>\n\nHidden.\n\n</details>\n")

    publish_work.main(
        ["create", "--config", "cfg", "--project", "ABC", "--issue-type", "Story", "--summary", "S", "--markdown", str(source)]
    )

    description = jira.post.call_args.kwargs["data"]["fields"]["description"]
    assert description["content"][0]["type"] == "expand"
    assert _out(capsys)["key"] == "ABC-7"


def test_create_requires_a_description_source(jira, capsys):
    with pytest.raises(SystemExit):
        publish_work.main(["create", "--config", "cfg", "--project", "ABC", "--issue-type", "Story", "--summary", "S"])

    jira.post.assert_not_called()


def test_markdown_rejected_by_the_converter_fails_before_any_call(jira, tmp_path, capsys):
    source = tmp_path / "description.md"
    source.write_text('<!-- adf:comment id="a" -->unterminated\n')

    with pytest.raises(SystemExit):
        publish_work.main(["update", "--config", "cfg", "--key", "ABC-3", "--markdown", str(source)])

    assert "error: Markdown conversion failed:" in capsys.readouterr().err
    jira.put.assert_not_called()


def test_markdown_with_an_unresolved_adf_error_fails_before_any_call(jira, tmp_path, capsys):
    source = tmp_path / "description.md"
    source.write_text('Hi <!-- adf:error id="e1" node="mention" -->⚠️ **Conversion error e1:** x\n')

    with pytest.raises(SystemExit):
        publish_work.main(["update", "--config", "cfg", "--key", "ABC-3", "--markdown", str(source)])

    assert "line 1: unresolved conversion error e1 (adf:error)" in capsys.readouterr().err
    jira.put.assert_not_called()


def test_update_with_only_attachments_resumes_by_key_without_touching_fields(jira, tmp_path, capsys):
    attachment = tmp_path / "a.png"
    attachment.write_bytes(b"x")

    publish_work.main(["update", "--config", "cfg", "--key", "ABC-7", "--attach", str(attachment)])

    jira.put.assert_not_called()
    jira.add_attachment.assert_called_once_with("ABC-7", str(attachment))
    assert _out(capsys) == {"key": "ABC-7", "url": "https://org.atlassian.net/browse/ABC-7", "attached": ["a.png"]}


def test_create_with_an_unknown_outcome_warns_against_a_blind_retry(jira, adf_file, capsys):
    jira.post.side_effect = RequestsConnectionError("https://x/?token=secret")

    with pytest.raises(SystemExit):
        publish_work.main(
            ["create", "--config", "cfg", "--project", "ABC", "--issue-type", "Story", "--summary", "S", "--adf", adf_file]
        )

    err = capsys.readouterr().err
    assert "outcome unknown (ConnectionError)" in err
    assert "before retrying" in err
    assert "secret" not in err


MEDIA_ID = "a7b047b2-009f-4465-b755-a060ab84fac8"


@pytest.fixture
def comment_jira(jira, monkeypatch):
    jira.post.return_value = {"id": "900"}
    jira.add_attachment.side_effect = lambda key, path: [
        {"id": "55" if path.endswith(".png") else "56", "filename": path.rsplit("/", 1)[-1], "mimeType": "image/png" if path.endswith(".png") else "text/plain"}
    ]
    monkeypatch.setattr(publish_work, "media_resolver", lambda credentials: lambda attachment_id: f"{attachment_id}-{MEDIA_ID}"[-36:])
    return jira


def _files(tmp_path):
    image, report = tmp_path / "shot.png", tmp_path / "report.txt"
    image.write_bytes(b"x")
    report.write_text("x")
    return image, report


def test_comment_shows_an_image_preview_and_a_file_card_inline(comment_jira, tmp_path, capsys):
    image, report = _files(tmp_path)
    source = tmp_path / "comment.md"
    source.write_text("See **below**\n")

    publish_work.main(["comment", "--config", "cfg", "--key", "ABC-7", "--markdown", str(source), "--attach", str(report), "--attach", str(image)])

    path, = comment_jira.post.call_args.args
    body = comment_jira.post.call_args.kwargs["data"]["body"]
    assert path == "rest/api/3/issue/ABC-7/comment"
    assert [node["type"] for node in body["content"]] == ["paragraph", "mediaSingle", "mediaGroup"]
    assert body["content"][1]["content"][0]["attrs"] == {"type": "file", "id": MEDIA_ID, "collection": ""}
    assert body["content"][2]["content"][0]["attrs"]["type"] == "file"
    assert _out(capsys) == {
        "key": "ABC-7",
        "commentId": "900",
        "url": "https://org.atlassian.net/browse/ABC-7?focusedCommentId=900",
        "attached": [
            {"id": "56", "filename": "report.txt", "inline": "card"},
            {"id": "55", "filename": "shot.png", "inline": "preview"},
        ],
    }


def test_comment_with_a_comment_id_replaces_that_comment(comment_jira, tmp_path, capsys):
    _, report = _files(tmp_path)
    source = tmp_path / "comment.md"
    source.write_text("Edited\n")

    publish_work.main(["comment", "--config", "cfg", "--key", "ABC-7", "--comment-id", "900", "--markdown", str(source), "--attach", str(report)])

    comment_jira.post.assert_not_called()
    assert comment_jira.put.call_args.args == ("rest/api/3/issue/ABC-7/comment/900",)
    assert _out(capsys)["commentId"] == "900"


def test_comment_without_attachments_posts_the_converted_markdown(comment_jira, tmp_path, capsys):
    source = tmp_path / "comment.md"
    source.write_text("Plain\n")

    publish_work.main(["comment", "--config", "cfg", "--key", "ABC-7", "--markdown", str(source)])

    assert [node["type"] for node in comment_jira.post.call_args.kwargs["data"]["body"]["content"]] == ["paragraph"]
    assert "attached" not in _out(capsys)


def test_comment_with_a_missing_file_uploads_and_posts_nothing(comment_jira, tmp_path, capsys):
    image, _ = _files(tmp_path)
    source = tmp_path / "comment.md"
    source.write_text("x\n")

    with pytest.raises(SystemExit):
        publish_work.main(["comment", "--config", "cfg", "--key", "ABC-7", "--markdown", str(source), "--attach", str(image), "--attach", str(tmp_path / "gone.txt")])

    comment_jira.add_attachment.assert_not_called()
    comment_jira.post.assert_not_called()
    assert "cannot read attachment" in capsys.readouterr().err


def test_comment_is_not_posted_when_a_media_id_cannot_be_resolved(comment_jira, monkeypatch, tmp_path, capsys):
    image, _ = _files(tmp_path)
    source = tmp_path / "comment.md"
    source.write_text("x\n")

    def refuse(attachment_id):
        raise ValueError(f"attachment {attachment_id} has no media file id (HTTP 404)")

    monkeypatch.setattr(publish_work, "media_resolver", lambda credentials: refuse)

    with pytest.raises(SystemExit):
        publish_work.main(["comment", "--config", "cfg", "--key", "ABC-7", "--markdown", str(source), "--attach", str(image)])

    comment_jira.post.assert_not_called()
    assert "cannot be shown inline" in capsys.readouterr().err


def test_comment_shows_page_cards_before_the_files_and_lists_the_resolved_urls(comment_jira, monkeypatch, tmp_path, capsys):
    image, _ = _files(tmp_path)
    source = tmp_path / "comment.md"
    source.write_text("Text\n")
    monkeypatch.setattr(publish_work, "page_resolver", lambda credentials: lambda reference: f"https://org.atlassian.net/wiki/spaces/Z/pages/{reference}/T")

    publish_work.main(["comment", "--config", "cfg", "--key", "ABC-7", "--markdown", str(source), "--page", "42", "--attach", str(image)])

    body = comment_jira.post.call_args.kwargs["data"]["body"]
    assert [node["type"] for node in body["content"]] == ["paragraph", "paragraph", "mediaSingle"]
    assert body["content"][1]["content"] == [{"type": "inlineCard", "attrs": {"url": "https://org.atlassian.net/wiki/spaces/Z/pages/42/T"}}]
    assert _out(capsys)["pages"] == ["https://org.atlassian.net/wiki/spaces/Z/pages/42/T"]


def test_comment_with_an_unresolvable_page_posts_and_uploads_nothing(comment_jira, monkeypatch, tmp_path, capsys):
    image, _ = _files(tmp_path)
    source = tmp_path / "comment.md"
    source.write_text("x\n")

    def refuse(reference):
        raise ValueError("page 9 not found (HTTP 404)")

    monkeypatch.setattr(publish_work, "page_resolver", lambda credentials: refuse)

    with pytest.raises(SystemExit):
        publish_work.main(["comment", "--config", "cfg", "--key", "ABC-7", "--markdown", str(source), "--page", "9", "--attach", str(image)])

    comment_jira.add_attachment.assert_not_called()
    comment_jira.post.assert_not_called()
    assert "cannot link page 9" in capsys.readouterr().err


def test_comment_markdown_with_an_inline_card_marker_keeps_the_page_card(comment_jira, tmp_path):
    source = tmp_path / "comment.md"
    source.write_text('<!-- adf:inline-card -->[https://org.atlassian.net/wiki/spaces/Z/pages/1/T](https://org.atlassian.net/wiki/spaces/Z/pages/1/T)<!-- /adf:inline-card -->\n')

    publish_work.main(["comment", "--config", "cfg", "--key", "ABC-7", "--markdown", str(source)])

    paragraph = comment_jira.post.call_args.kwargs["data"]["body"]["content"][0]
    assert paragraph["content"][0] == {"type": "inlineCard", "attrs": {"url": "https://org.atlassian.net/wiki/spaces/Z/pages/1/T"}}
