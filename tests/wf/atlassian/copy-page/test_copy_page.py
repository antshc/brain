from __future__ import annotations

import copy
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from atl_cli.conversion_guard import compare_documents
from atl_cli.copy_page import copy_page, strip_comment_anchors
from atl_cli.map_markdown import md_to_adf


def test_strip_comment_anchors_keeps_text_and_drops_source_identity():
    markdown = '<!-- adf:comment id="c1" -->Keep this<!-- /adf:comment -->'

    assert strip_comment_anchors(markdown) == "Keep this"


def test_copy_page_clones_with_required_attachments_and_verifies(tmp_path, monkeypatch):
    credentials = {"site": "https://example.atlassian.net", "email": "e", "token": "t"}
    client = MagicMock()
    client.get.return_value = {"title": "Destination title"}
    monkeypatch.setattr("atl_cli.copy_page.require_supported_library", lambda: None)
    monkeypatch.setattr("atl_cli.copy_page.load_credentials", lambda path: credentials)
    monkeypatch.setattr("atl_cli.copy_page.get_confluence", lambda current: client)
    monkeypatch.setattr(
        "atl_cli.copy_page.fetch_page",
        lambda confluence, page_id: (
            "Source title",
            {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Body",
                                "marks": [
                                    {
                                        "type": "annotation",
                                        "attrs": {"annotationType": "inlineComment", "id": "c1"},
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
        ),
    )
    monkeypatch.setattr("atl_cli.copy_page.lint_markdown", lambda markdown: None)
    monkeypatch.setattr("atl_cli.copy_page.validate_markdown", lambda markdown, **kwargs: None)
    seen: dict = {}

    def fake_publish(**kwargs):
        seen["markdown"] = Path(kwargs["md_path"]).read_text()
        manifest = Path(kwargs["assets_dir"]) / "final-adf.manifest.json"
        manifest.write_text(json.dumps({"title": kwargs["title"], "adf": {}}))
        seen["title"] = kwargs["title"]
        return {
            "method": "rest",
            "pageId": kwargs["page_id"],
            "title": kwargs["title"],
            "attachments": 1,
            "manifestPath": str(manifest),
        }

    monkeypatch.setattr("atl_cli.copy_page.publish", fake_publish)
    monkeypatch.setattr("atl_cli.copy_page.verify_publish", lambda argv: 0)

    result = copy_page(
        source="123",
        target="456",
        config_path="config.json",
        work_dir=str(tmp_path / "copy"),
    )

    assert 'adf:comment' not in seen["markdown"]
    assert "Body" in seen["markdown"]
    assert seen["title"] == "Destination title"
    assert result["verified"] is True
    assert result["commentPolicy"] == "clone"
    assert result["sourcePageId"] == "123"
    assert result["targetPageId"] == "456"


def test_copy_page_rejects_using_the_same_page_as_source_and_target(tmp_path):
    with pytest.raises(ValueError, match="must differ"):
        copy_page(
            source="42",
            target="https://example.atlassian.net/wiki/spaces/X/pages/42/Copy",
            config_path="config.json",
            work_dir=str(tmp_path),
        )


@pytest.mark.parametrize("source_widths", ["none", "uniform", "row-specific-with-comment"])
def test_copy_page_does_not_inherit_destination_table_widths(tmp_path, monkeypatch, source_widths):
    source = md_to_adf("| A | B |\n| --- | --- |\n| one | two |\n")
    destination = copy.deepcopy(source)
    if source_widths != "none":
        source["content"][0]["attrs"].update({"layout": "wide", "width": 640})
        for row in source["content"][0]["content"]:
            for cell, width in zip(row["content"], (77, 123)):
                cell["attrs"] = {"colwidth": [width]}
    if source_widths == "row-specific-with-comment":
        cell = source["content"][0]["content"][1]["content"][0]
        cell["attrs"]["colwidth"] = [88]
        cell["content"][0]["content"][0]["marks"] = [
            {"type": "annotation", "attrs": {"annotationType": "inlineComment", "id": "c1"}}
        ]
    table = destination["content"][0]
    table["attrs"].update({"layout": "wide", "width": 960})
    for row in table["content"]:
        for cell, width in zip(row["content"], (155, 355)):
            cell["attrs"] = {"colwidth": [width]}

    client = MagicMock()
    client.get.side_effect = lambda path, params=None: (
        {"version": {"number": 7}, "body": {"atlas_doc_format": {"value": json.dumps(destination)}}}
        if params else {"title": "Destination", "version": {"number": 7}}
    )
    credentials = {"site": "https://example.atlassian.net", "email": "e", "token": "t"}
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"cloudId": "example.atlassian.net", "email": "e", "apiToken": "t"}))
    monkeypatch.setattr("atl_cli.copy_page.require_supported_library", lambda: None)
    monkeypatch.setattr("atl_cli.copy_page.load_credentials", lambda path: credentials)
    monkeypatch.setattr("atl_cli.copy_page.get_confluence", lambda current: client)
    monkeypatch.setattr("atl_cli.copy_page.fetch_page", lambda confluence, page_id: ("Source", source))
    monkeypatch.setattr("atl_cli.copy_page.verify_publish", lambda argv: 0)
    monkeypatch.setattr("atl_cli.page_diagrams.pipeline.get_confluence", lambda current: client)
    monkeypatch.setattr("atl_cli.page_diagrams.pipeline._plan_comment_guard", lambda *args: (None, {}))
    update = MagicMock()
    monkeypatch.setattr("atl_cli.page_diagrams.pipeline.update_page_adf", update)

    copy_page(source="123", target="456", config_path=str(config), work_dir=str(tmp_path / "copy"))

    expected = copy.deepcopy(source)
    if source_widths == "row-specific-with-comment":
        del expected["content"][0]["content"][1]["content"][0]["content"][0]["content"][0]["marks"]
    compare_documents(expected, update.call_args.args[3])
