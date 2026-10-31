from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import HTTPError

import publish_work

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
