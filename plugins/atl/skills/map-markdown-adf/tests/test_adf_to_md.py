"""ADF -> Markdown cases, ported from pyadf2md's JSON fixtures and extended for the block/mark
types pyadf2md never supported (heading, codeBlock, blockquote, rule, expand, strike, code, link).
"""
import json


def _doc(*content):
    return {"version": 1, "type": "doc", "content": list(content)}


def _p(*inline):
    return {"type": "paragraph", "content": list(inline)}


def _t(text, marks=None):
    node = {"type": "text", "text": text}
    if marks:
        node["marks"] = marks
    return node


def test_paragraph(adf_to_md):
    doc = _doc(_p(_t("Hello world.")))
    assert adf_to_md(doc) == "Hello world."


def test_bold_italic(adf_to_md):
    doc = _doc(_p(_t("bold", [{"type": "strong"}]), _t(" "), _t("italic", [{"type": "em"}])))
    assert adf_to_md(doc) == "**bold** *italic*"


def test_code_strike_and_link(adf_to_md):
    doc = _doc(
        _p(
            _t("code", [{"type": "code"}]),
            _t(" "),
            _t("gone", [{"type": "strike"}]),
            _t(" "),
            _t("label", [{"type": "link", "attrs": {"href": "https://example.com"}}]),
        )
    )
    assert adf_to_md(doc) == "`code` ~~gone~~ [label](https://example.com)"


def test_heading(adf_to_md):
    doc = _doc({"type": "heading", "attrs": {"level": 2}, "content": [_t("Title")]})
    assert adf_to_md(doc) == "## Title"


def test_bullet_list(adf_to_md):
    doc = _doc(
        {
            "type": "bulletList",
            "content": [
                {"type": "listItem", "content": [_p(_t("one"))]},
                {"type": "listItem", "content": [_p(_t("two"))]},
            ],
        }
    )
    assert adf_to_md(doc) == "- one\n- two"


def test_nested_bullet_list(adf_to_md):
    doc = _doc(
        {
            "type": "bulletList",
            "content": [
                {
                    "type": "listItem",
                    "content": [
                        _p(_t("parent")),
                        {
                            "type": "bulletList",
                            "content": [{"type": "listItem", "content": [_p(_t("child"))]}],
                        },
                    ],
                },
            ],
        }
    )
    assert adf_to_md(doc) == "- parent\n  - child"


def test_ordered_list(adf_to_md):
    doc = _doc(
        {
            "type": "orderedList",
            "content": [
                {"type": "listItem", "content": [_p(_t("one"))]},
                {"type": "listItem", "content": [_p(_t("two"))]},
            ],
        }
    )
    assert adf_to_md(doc) == "1. one\n2. two"


def test_blockquote(adf_to_md):
    doc = _doc({"type": "blockquote", "content": [_p(_t("quoted line"))]})
    assert adf_to_md(doc) == "> quoted line"


def test_panel(adf_to_md):
    doc = _doc({"type": "panel", "attrs": {"panelType": "warning"}, "content": [_p(_t("Be careful here."))]})
    assert adf_to_md(doc) == "> [!WARNING]\n> Be careful here."


def test_status(adf_to_md):
    doc = _doc(_p(_t("Assignee: "), {"type": "status", "attrs": {"text": "In Progress", "color": "blue"}}))
    assert adf_to_md(doc) == "Assignee: [STATUS:In Progress|blue]"


def test_code_block(adf_to_md):
    doc = _doc({"type": "codeBlock", "attrs": {"language": "python"}, "content": [_t("x = 1")]})
    assert adf_to_md(doc) == "```python\nx = 1\n```"


def test_rule(adf_to_md):
    doc = _doc({"type": "rule"})
    assert adf_to_md(doc) == "---"


def test_expand(adf_to_md):
    doc = _doc({"type": "expand", "attrs": {"title": "Click me"}, "content": [_p(_t("hidden text"))]})
    assert adf_to_md(doc) == "<details>\n<summary>Click me</summary>\n\nhidden text\n</details>"


def test_expand_with_toc_extension_renders_toc_comment(adf_to_md):
    toc_extension = {
        "type": "extension",
        "attrs": {
            "layout": "default",
            "extensionType": "com.atlassian.confluence.macro.core",
            "extensionKey": "toc",
            "parameters": {"macroParams": {}},
        },
    }
    doc = _doc({"type": "expand", "attrs": {"title": "Table of Contents"}, "content": [toc_extension]})
    assert adf_to_md(doc) == "<!-- adf:toc -->"


def _toc_extension():
    return {
        "type": "extension",
        "attrs": {
            "layout": "default",
            "extensionType": "com.atlassian.confluence.macro.core",
            "extensionKey": "toc",
            "parameters": {"macroParams": {}},
        },
    }


def test_standalone_toc_extension_renders_toc_comment(adf_to_md):
    doc = _doc(_toc_extension())
    assert adf_to_md(doc) == "<!-- adf:toc -->"


def test_expand_with_toc_among_other_content_keeps_details_wrapper(adf_to_md):
    doc = _doc(
        {
            "type": "expand",
            "attrs": {"title": "Overview"},
            "content": [_toc_extension(), _p(_t("more content"))],
        }
    )
    assert adf_to_md(doc) == (
        "<details>\n<summary>Overview</summary>\n\n<!-- adf:toc -->\n\nmore content\n</details>"
    )


def test_inline_card_renders_url_as_a_markdown_link(adf_to_md):
    doc = _doc(_p({"type": "inlineCard", "attrs": {"url": "https://example.atlassian.net/wiki/x/AbCdE"}}))
    assert adf_to_md(doc) == "[https://example.atlassian.net/wiki/x/AbCdE](https://example.atlassian.net/wiki/x/AbCdE)"


def test_inline_card_inside_list_item_and_table_cell(adf_to_md):
    doc = _doc(
        {
            "type": "bulletList",
            "content": [
                {
                    "type": "listItem",
                    "content": [_p({"type": "inlineCard", "attrs": {"url": "https://example.com/a"}})],
                }
            ],
        },
        {
            "type": "table",
            "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
            "content": [
                {
                    "type": "tableRow",
                    "content": [
                        {
                            "type": "tableCell",
                            "content": [_p({"type": "inlineCard", "attrs": {"url": "https://example.com/b"}})],
                        }
                    ],
                }
            ],
        },
    )
    assert adf_to_md(doc) == (
        "- [https://example.com/a](https://example.com/a)\n\n"
        "| [https://example.com/b](https://example.com/b) |"
    )


def test_table_cell_preserves_italic_requirement_and_bullet_line_break(adf_to_md):
    doc = _doc(
        {
            "type": "table",
            "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
            "content": [
                {
                    "type": "tableRow",
                    "content": [
                        {"type": "tableHeader", "content": [_p(_t("#"))]},
                        {"type": "tableHeader", "content": [_p(_t("Requirement"))]},
                        {"type": "tableHeader", "content": [_p(_t("Details"))]},
                    ],
                },
                {
                    "type": "tableRow",
                    "content": [
                        {"type": "tableCell", "content": [_p(_t("1.1"))]},
                        {
                            "type": "tableCell",
                            "content": [_p({"type": "text", "text": "Required behavior", "marks": [{"type": "em"}]})],
                        },
                        {
                            "type": "tableCell",
                            "content": [
                                _p(
                                    _t("• First rule"),
                                    {"type": "hardBreak"},
                                    _t("• Boundary case"),
                                )
                            ],
                        },
                    ],
                },
            ],
        }
    )

    assert adf_to_md(doc) == (
        "| # | Requirement | Details |\n"
        "| --- | --- | --- |\n"
        "| 1.1 | *Required behavior* | • First rule<br>• Boundary case |"
    )


def test_create_from_template_inline_extension_is_ignored(adf_to_md):
    doc = _doc(
        _p(
            {
                "type": "inlineExtension",
                "attrs": {
                    "extensionType": "com.atlassian.confluence.macro.core",
                    "extensionKey": "create-from-template",
                    "parameters": {
                        "macroParams": {
                            "spaceKey": {"value": "Infra"},
                            "templateId": {"value": "134021445"},
                            "buttonLabel": {"value": "Create Design Page from template"},
                        }
                    },
                },
            }
        )
    )
    assert adf_to_md(doc) == ""


def test_inline_card_without_url_raises(run_cli):
    doc = _doc(_p({"type": "inlineCard", "attrs": {}}))
    result = run_cli("adf-to-md", json.dumps(doc))
    assert result.returncode != 0
    assert "inlineCard" in result.stderr


def test_table(adf_to_md):
    doc = _doc(
        {
            "type": "table",
            "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
            "content": [
                {
                    "type": "tableRow",
                    "content": [
                        {"type": "tableHeader", "content": [_p(_t("a"))]},
                        {"type": "tableHeader", "content": [_p(_t("b"))]},
                    ],
                },
                {
                    "type": "tableRow",
                    "content": [
                        {"type": "tableCell", "content": [_p(_t("1"))]},
                        {"type": "tableCell", "content": [_p(_t("2"))]},
                    ],
                },
            ],
        }
    )
    assert adf_to_md(doc) == "| a | b |\n| --- | --- |\n| 1 | 2 |"


def test_table_colspan(adf_to_md):
    doc = _doc(
        {
            "type": "table",
            "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
            "content": [
                {
                    "type": "tableRow",
                    "content": [
                        {"type": "tableHeader", "content": [_p(_t("Column 0"))]},
                        {"type": "tableHeader", "content": [_p(_t("Column 1"))]},
                        {"type": "tableHeader", "content": [_p(_t("Column 2"))]},
                    ],
                },
                {
                    "type": "tableRow",
                    "content": [
                        {"type": "tableCell", "attrs": {"colspan": 2}, "content": [_p(_t("row 0 col 0-1"))]},
                        {"type": "tableCell", "content": [_p(_t("row 0 col 2"))]},
                    ],
                },
                {
                    "type": "tableRow",
                    "content": [
                        {"type": "tableCell", "content": [_p(_t("row 1 col 0"))]},
                        {"type": "tableCell", "attrs": {"colspan": 2}, "content": [_p(_t("row 1 col 1-2"))]},
                    ],
                },
                {
                    "type": "tableRow",
                    "content": [
                        {"type": "tableCell", "attrs": {"colspan": 3}, "content": [_p(_t("row 2 col 0-2"))]},
                    ],
                },
            ],
        }
    )
    assert adf_to_md(doc) == (
        "| Column 0 | Column 1 | Column 2 |\n"
        "| --- | --- | --- |\n"
        "| row 0 col 0-1 |  | row 0 col 2 |\n"
        "| row 1 col 0 | row 1 col 1-2 |  |\n"
        "| row 2 col 0-2 |  |  |"
    )


def test_table_rowspan(adf_to_md):
    doc = _doc(
        {
            "type": "table",
            "content": [
                {
                    "type": "tableRow",
                    "content": [
                        {"type": "tableHeader", "content": [_p(_t("Column 0"))]},
                        {"type": "tableHeader", "content": [_p(_t("Column 1"))]},
                    ],
                },
                {
                    "type": "tableRow",
                    "content": [
                        {"type": "tableCell", "attrs": {"rowspan": 2}, "content": [_p(_t("rows 0-1"))]},
                        {"type": "tableCell", "content": [_p(_t("row 0"))]},
                    ],
                },
                {
                    "type": "tableRow",
                    "content": [
                        {"type": "tableCell", "content": [_p(_t("row 1"))]},
                    ],
                },
            ],
        }
    )
    assert adf_to_md(doc) == (
        "| Column 0 | Column 1 |\n"
        "| --- | --- |\n"
        "| rows 0-1 | row 0 |\n"
        "|  | row 1 |"
    )


def test_wide_table_layout_renders_prefixed_comment(adf_to_md):
    doc = _doc(
        {
            "type": "table",
            "attrs": {"isNumberColumnEnabled": False, "layout": "wide"},
            "content": [
                {
                    "type": "tableRow",
                    "content": [
                        {"type": "tableHeader", "content": [_p(_t("a"))]},
                        {"type": "tableHeader", "content": [_p(_t("b"))]},
                    ],
                },
                {
                    "type": "tableRow",
                    "content": [
                        {"type": "tableCell", "content": [_p(_t("1"))]},
                        {"type": "tableCell", "content": [_p(_t("2"))]},
                    ],
                },
            ],
        }
    )
    assert adf_to_md(doc) == "<!-- adf:wide-table -->\n\n| a | b |\n| --- | --- |\n| 1 | 2 |"


def test_drawio_extension_renders_diagram_placeholder(adf_to_md):
    doc = _doc(
        {
            "type": "extension",
            "attrs": {
                "extensionKey": "app-1/env-1/static/drawio",
                "parameters": {"guestParams": {"diagramName": "order-flow.drawio"}},
            },
        }
    )
    assert adf_to_md(doc) == '<!-- adf:diagram drawio="order-flow.drawio" -->'


def test_media_single_renders_attachment_placeholder(adf_to_md):
    doc = _doc(
        {
            "type": "mediaSingle",
            "attrs": {"layout": "center"},
            "content": [{"type": "media", "attrs": {"id": "file-123", "type": "file"}}],
        }
    )
    assert adf_to_md(doc) == '<!-- adf:attachment media-id="file-123" alt="" -->'


def test_media_single_carries_alt_through(adf_to_md):
    doc = _doc(
        {
            "type": "mediaSingle",
            "attrs": {"layout": "center"},
            "content": [
                {"type": "media", "attrs": {"id": "file-456", "type": "file", "alt": "Screenshot.png"}}
            ],
        }
    )
    assert adf_to_md(doc) == '<!-- adf:attachment media-id="file-456" alt="Screenshot.png" -->'


def test_media_group_renders_one_placeholder_per_file(adf_to_md):
    doc = _doc(
        {
            "type": "mediaGroup",
            "content": [{"type": "media", "attrs": {"id": "file-789", "type": "file"}}],
        }
    )
    assert adf_to_md(doc) == '<!-- adf:attachment media-id="file-789" alt="" -->'


def test_media_group_renders_a_placeholder_per_file_when_it_holds_several(adf_to_md):
    doc = _doc(
        {
            "type": "mediaGroup",
            "content": [
                {"type": "media", "attrs": {"id": "file-1", "type": "file"}},
                {"type": "media", "attrs": {"id": "file-2", "type": "file", "alt": "diagram.png"}},
            ],
        }
    )
    assert adf_to_md(doc) == (
        '<!-- adf:attachment media-id="file-1" alt="" -->\n\n'
        '<!-- adf:attachment media-id="file-2" alt="diagram.png" -->'
    )


def test_media_single_carries_width_and_height_through(adf_to_md):
    doc = _doc(
        {
            "type": "mediaSingle",
            "attrs": {"layout": "center"},
            "content": [
                {
                    "type": "media",
                    "attrs": {
                        "id": "file-456",
                        "type": "file",
                        "alt": "Screenshot.png",
                        "width": 611,
                        "height": 793,
                    },
                }
            ],
        }
    )
    assert adf_to_md(doc) == (
        '<!-- adf:attachment media-id="file-456" alt="Screenshot.png" width="611" height="793" -->'
    )


def test_media_group_omits_width_and_height_when_the_node_has_neither(adf_to_md):
    doc = _doc(
        {
            "type": "mediaGroup",
            "content": [{"type": "media", "attrs": {"id": "file-789", "type": "file"}}],
        }
    )
    assert "width" not in adf_to_md(doc)


def test_media_single_omits_width_and_height_when_only_one_is_present(adf_to_md):
    doc = _doc(
        {
            "type": "mediaSingle",
            "attrs": {"layout": "center"},
            "content": [{"type": "media", "attrs": {"id": "file-1", "type": "file", "width": 611}}],
        }
    )
    assert adf_to_md(doc) == '<!-- adf:attachment media-id="file-1" alt="" -->'


def test_unknown_extension_still_raises(run_cli):
    doc = _doc({"type": "extension", "attrs": {"extensionKey": "some.other.macro"}})
    result = run_cli("adf-to-md", json.dumps(doc))
    assert result.returncode != 0
    assert "some.other.macro" in result.stderr


def test_unknown_node_type_still_raises(run_cli):
    doc = _doc({"type": "totallyUnknownNode"})
    result = run_cli("adf-to-md", json.dumps(doc))
    assert result.returncode != 0
    assert "totallyUnknownNode" in result.stderr
