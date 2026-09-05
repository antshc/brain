"""ADF -> Markdown cases, ported from pyadf2md's JSON fixtures and extended for the block/mark
types pyadf2md never supported (heading, codeBlock, blockquote, rule, expand, strike, code, link).
"""


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
    assert adf_to_md(doc) == "<!-- confluence:toc -->"


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
        "| row 0 col 0-1 | row 0 col 2 |\n"
        "| row 1 col 0 | row 1 col 1-2 |\n"
        "| row 2 col 0-2 |"
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
    assert adf_to_md(doc) == "<!-- confluence:wide-table -->\n\n| a | b |\n| --- | --- |\n| 1 | 2 |"
