import json
from unittest.mock import MagicMock

from page_diagrams.custom_content import DIAGRAM_TYPE, upsert_diagram


def test_upsert_diagram_creates_the_record_on_a_first_publish():
    confluence = MagicMock()
    confluence.get.side_effect = [{"results": []}, {"space": {"key": "SPACE"}}]
    confluence.post.return_value = {"id": 999}

    result = upsert_diagram(confluence, "123", "00-title.drawio", "Start Done")

    assert result == {"id": "999", "revision": 1}
    assert confluence.get.call_args_list[0].args[0] == f"/rest/api/content/123/child/{DIAGRAM_TYPE}"
    assert confluence.get.call_args_list[0].kwargs["params"] == {"expand": "version", "limit": 200}
    payload = confluence.post.call_args.kwargs["data"]
    assert confluence.post.call_args.args[0] == "/rest/api/content"
    assert payload["type"] == DIAGRAM_TYPE
    assert payload["title"] == "00-title.drawio"
    assert payload["space"] == {"key": "SPACE"}
    assert payload["container"] == {"id": "123", "type": "page"}
    assert json.loads(payload["body"]["raw"]["value"]) == {
        "search": "Start Done",
        "pageId": "123",
        "type": "page",
        "diagramName": "00-title.drawio",
        "revision": 1,
        "isSketch": False,
    }
    confluence.put.assert_not_called()


def test_upsert_diagram_updates_and_bumps_the_revision_on_republish():
    confluence = MagicMock()
    confluence.get.side_effect = [
        {"results": [{"id": "999", "title": "00-title.drawio", "version": {"number": 3}}]},
        {"space": {"key": "SPACE"}},
    ]

    result = upsert_diagram(confluence, "123", "00-title.drawio", "Start Done")

    assert result == {"id": "999", "revision": 4}
    confluence.post.assert_not_called()
    assert confluence.put.call_args.args[0] == "/rest/api/content/999"
    payload = confluence.put.call_args.kwargs["data"]
    assert payload["space"] == {"key": "SPACE"}
    assert payload["version"] == {"number": 4}
    assert json.loads(payload["body"]["raw"]["value"])["revision"] == 4


def test_upsert_diagram_ignores_another_diagram_on_the_same_page():
    confluence = MagicMock()
    confluence.get.side_effect = [
        {"results": [{"id": "111", "title": "01-other.drawio", "version": {"number": 2}}]},
        {"space": {"key": "SPACE"}},
    ]
    confluence.post.return_value = {"id": "222"}

    assert upsert_diagram(confluence, "123", "00-title.drawio", "") == {"id": "222", "revision": 1}
    confluence.put.assert_not_called()
