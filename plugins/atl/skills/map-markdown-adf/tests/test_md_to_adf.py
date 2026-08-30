"""Markdown -> ADF cases, ported from pub-zdesign's test_blocks.py and test_inline.py."""
import pytest


def test_heading_and_paragraph(md_to_adf):
    doc = md_to_adf("# Title\n\nSome paragraph text.")
    assert doc["content"][0] == {
        "type": "heading",
        "attrs": {"level": 1},
        "content": [{"type": "text", "text": "Title"}],
    }
    assert doc["content"][1]["type"] == "paragraph"
    assert doc["content"][1]["content"][0]["text"] == "Some paragraph text."


def test_rule(md_to_adf):
    doc = md_to_adf("---")
    assert doc["content"] == [{"type": "rule"}]


def test_code_block_known_language(md_to_adf):
    doc = md_to_adf("```python\nx = 1\n```")
    assert doc["content"] == [
        {
            "type": "codeBlock",
            "attrs": {"language": "python"},
            "content": [{"type": "text", "text": "x = 1"}],
        }
    ]


def test_code_block_unknown_language_omits_attrs(md_to_adf):
    doc = md_to_adf("```wat\nabc\n```")
    assert "attrs" not in doc["content"][0]


def test_blockquote(md_to_adf):
    doc = md_to_adf("> quoted line")
    block = doc["content"][0]
    assert block["type"] == "blockquote"
    assert block["content"][0]["content"][0]["text"] == "quoted line"


def test_details_expand(md_to_adf):
    md = "<details>\n<summary>Click me</summary>\n\nhidden text\n</details>"
    doc = md_to_adf(md)
    block = doc["content"][0]
    assert block["type"] == "expand"
    assert block["attrs"]["title"] == "Click me"
    assert block["content"][0]["content"][0]["text"] == "hidden text"


def test_nested_details(md_to_adf):
    md = (
        "<details>\n<summary>Outer</summary>\n\n"
        "<details>\n<summary>Inner</summary>\n\nx\n</details>\n"
        "</details>"
    )
    doc = md_to_adf(md)
    outer = doc["content"][0]
    assert outer["attrs"]["title"] == "Outer"
    inner = outer["content"][0]
    assert inner["type"] == "expand"
    assert inner["attrs"]["title"] == "Inner"


def test_table(md_to_adf):
    doc = md_to_adf("| a | b |\n| --- | --- |\n| 1 | 2 |")
    table = doc["content"][0]
    assert table["type"] == "table"
    assert len(table["content"]) == 2  # header row + one data row


def test_bullet_list(md_to_adf):
    doc = md_to_adf("- one\n- two")
    block = doc["content"][0]
    assert block["type"] == "bulletList"
    assert len(block["content"]) == 2


def test_ordered_list(md_to_adf):
    doc = md_to_adf("1. one\n2. two")
    assert doc["content"][0]["type"] == "orderedList"


def test_nested_bullet_list(md_to_adf):
    doc = md_to_adf("- parent\n  - child")
    parent_item = doc["content"][0]["content"][0]
    nested = [c for c in parent_item["content"] if c.get("type") == "bulletList"]
    assert len(nested) == 1
    assert nested[0]["content"][0]["content"][0]["content"][0]["text"] == "child"


def test_bullet_list_then_ordered_list_stay_separate(md_to_adf):
    doc = md_to_adf("- bullet one\n- bullet two\n\n1. ordered one\n2. ordered two")
    assert doc["content"][0]["type"] == "bulletList"
    assert len(doc["content"][0]["content"]) == 2
    assert doc["content"][1]["type"] == "orderedList"
    assert len(doc["content"][1]["content"]) == 2


@pytest.mark.parametrize(
    "markdown_span,expected",
    [
        ("**bold**", {"type": "text", "text": "bold", "marks": [{"type": "strong"}]}),
        ("*italic*", {"type": "text", "text": "italic", "marks": [{"type": "em"}]}),
        ("_italic_", {"type": "text", "text": "italic", "marks": [{"type": "em"}]}),
        ("__bold__", {"type": "text", "text": "bold", "marks": [{"type": "strong"}]}),
        ("`code`", {"type": "text", "text": "code", "marks": [{"type": "code"}]}),
        ("~~gone~~", {"type": "text", "text": "gone", "marks": [{"type": "strike"}]}),
    ],
)
def test_inline_marks(md_to_adf, markdown_span, expected):
    doc = md_to_adf(markdown_span)
    assert doc["content"][0]["content"][0] == expected


def test_link(md_to_adf):
    doc = md_to_adf("[label](https://example.com)")
    assert doc["content"][0]["content"][0] == {
        "type": "text",
        "text": "label",
        "marks": [{"type": "link", "attrs": {"href": "https://example.com"}}],
    }


def test_link_without_label_uses_href(md_to_adf):
    doc = md_to_adf("[](https://example.com)")
    assert doc["content"][0]["content"][0]["text"] == "https://example.com"


def test_mixed_marks_and_plain_text(md_to_adf):
    doc = md_to_adf("see **bold** and `code` here")
    assert doc["content"][0]["content"] == [
        {"type": "text", "text": "see "},
        {"type": "text", "text": "bold", "marks": [{"type": "strong"}]},
        {"type": "text", "text": " and "},
        {"type": "text", "text": "code", "marks": [{"type": "code"}]},
        {"type": "text", "text": " here"},
    ]
