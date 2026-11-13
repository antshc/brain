from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from atl_cli.page_diagrams import pipeline
from atl_cli.page_diagrams.cli import build_arg_parser


def publish_child(tmp_path, monkeypatch, *, page_id=None, actual_parent="100", attachment=False, space="10"):
    md = tmp_path / "research.md"
    md.write_text("# Research\n\nSupported findings.\n" + ("\n[probe.txt](probe.txt)\n" if attachment else ""))
    (tmp_path / "probe.txt").write_text("observations")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"cloudId": "example.atlassian.net", "email": "user@example.com", "apiToken": "test"}))
    client = MagicMock()
    client.post.return_value = {"id": "101"}

    def read(path, **kwargs):
        if path == "/api/v2/pages/100":
            return {"id": "100", "spaceId": space}
        if path == "/api/v2/pages/101":
            return {"id": "101", "parentId": actual_parent, "version": {"number": 1}}
        if path == "/rest/api/content/101/child/attachment":
            return {"results": [{"title": "probe.txt", "extensions": {"fileId": "file-1"}}]}
        raise AssertionError(path)

    client.get.side_effect = read
    monkeypatch.setattr(pipeline, "get_confluence", lambda _: client)
    return client, lambda: pipeline.publish(
        str(md), str(config), page_id, "10" if page_id is None else None,
        None, str(tmp_path / "assets"), str(tmp_path / "final.json"), parent_id="100",
    )


@pytest.mark.parametrize("attachment", [False, True])
def test_create_child_carries_parent_in_text_and_media_paths(tmp_path, monkeypatch, attachment):
    client, run = publish_child(tmp_path, monkeypatch, attachment=attachment)
    result = run()
    assert client.post.call_args.kwargs["data"]["parentId"] == "100"
    assert result["pageId"] == "101"
    assert result["parentId"] == "100"
    assert result["attachments"] == int(attachment)
    assert any(call.args[0] == "/api/v2/pages/101" for call in client.get.call_args_list)


def test_update_with_wrong_parent_is_blocked_before_writing(tmp_path, monkeypatch):
    client, run = publish_child(tmp_path, monkeypatch, page_id="101", actual_parent="999")
    with pytest.raises(ValueError, match="parent differs"):
        run()
    client.put.assert_not_called()
    client.post.assert_not_called()


def test_create_with_parent_from_another_space_is_blocked(tmp_path, monkeypatch):
    client, run = publish_child(tmp_path, monkeypatch, space="99")
    with pytest.raises(ValueError, match="creation space"):
        run()
    client.put.assert_not_called()
    client.post.assert_not_called()


@pytest.mark.parametrize("attachment", [False, True])
def test_failed_parent_readback_preserves_created_id(tmp_path, monkeypatch, attachment):
    client, run = publish_child(tmp_path, monkeypatch, actual_parent="999", attachment=attachment)
    with pytest.raises(pipeline.CreatedPageError) as error:
        run()
    assert error.value.page_id == "101"
    assert "--page-id 101" in str(error.value)
    assert client.post.call_count == 1
    client.put.assert_not_called()


def test_parent_option_parses_for_create_and_resume():
    parser = build_arg_parser()
    for target in (["--space-id", "10"], ["--page-id", "101"]):
        args = parser.parse_args(["run", "--md-path", "research.md", "--config", "config.json", "--parent-id", "100", *target])
        assert args.parent_id == "100"
