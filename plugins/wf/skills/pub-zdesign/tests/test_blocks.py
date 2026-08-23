from zdesign_publisher.blocks import (
    build_table,
    compute_colwidths,
    parse_blocks,
    parse_list,
    split_table_row,
)


def test_split_table_row():
    assert split_table_row("| a | b | c |") == ["a", "b", "c"]


def test_split_table_row_escaped_pipe():
    assert split_table_row(r"| a\|b | c |") == ["a|b", "c"]


def test_parse_blocks_heading_and_paragraph():
    lines = ["# Title", "", "Some paragraph text."]
    blocks = parse_blocks(lines)
    assert blocks[0] == {"type": "heading", "attrs": {"level": 1}, "content": [{"type": "text", "text": "Title"}]}
    assert blocks[1]["type"] == "paragraph"
    assert blocks[1]["content"][0]["text"] == "Some paragraph text."


def test_parse_blocks_rule():
    blocks = parse_blocks(["---"])
    assert blocks == [{"type": "rule"}]


def test_parse_blocks_code_block_known_language():
    lines = ["```python", "x = 1", "```"]
    blocks = parse_blocks(lines)
    assert blocks == [
        {
            "type": "codeBlock",
            "attrs": {"language": "python"},
            "content": [{"type": "text", "text": "x = 1"}],
        }
    ]


def test_parse_blocks_code_block_unknown_language_omits_attrs():
    lines = ["```wat", "abc", "```"]
    blocks = parse_blocks(lines)
    assert "attrs" not in blocks[0]


def test_parse_blocks_blockquote():
    lines = ["> quoted line"]
    blocks = parse_blocks(lines)
    assert blocks[0]["type"] == "blockquote"
    assert blocks[0]["content"][0]["content"][0]["text"] == "quoted line"


def test_parse_blocks_details_expand():
    lines = ["<details>", "<summary>Click me</summary>", "hidden text", "</details>"]
    blocks = parse_blocks(lines)
    assert blocks[0]["type"] == "expand"
    assert blocks[0]["attrs"]["title"] == "Click me"
    assert blocks[0]["content"][0]["content"][0]["text"] == "hidden text"


def test_parse_blocks_nested_details():
    lines = ["<details>", "<summary>Outer</summary>", "<details>", "<summary>Inner</summary>", "x", "</details>", "</details>"]
    blocks = parse_blocks(lines)
    outer = blocks[0]
    assert outer["attrs"]["title"] == "Outer"
    inner = outer["content"][0]
    assert inner["type"] == "expand"
    assert inner["attrs"]["title"] == "Inner"


def test_parse_blocks_table():
    lines = ["| a | b |", "|---|---|", "| 1 | 2 |"]
    blocks = parse_blocks(lines)
    assert blocks[0]["type"] == "table"
    assert len(blocks[0]["content"]) == 2  # header row + 1 data row


def test_parse_blocks_media_marker_with_file_id():
    lines = ["\x00MEDIA:0\x00"]
    blocks = parse_blocks(lines, media_files={0: "file-id-123"}, image_width=500)
    media_single = blocks[0]
    assert media_single["type"] == "mediaSingle"
    assert media_single["attrs"]["width"] == 500
    assert media_single["content"][0]["attrs"] == {"type": "file", "id": "file-id-123"}


def test_parse_blocks_media_marker_without_file_id():
    blocks = parse_blocks(["\x00MEDIA:0\x00"])
    assert blocks[0]["content"][0]["attrs"] == {"type": "file"}


def test_parse_blocks_toc_comment_becomes_expand():
    blocks = parse_blocks(["<!-- confluence:toc -->", "", "# Section"])
    assert blocks[0]["type"] == "expand"
    assert blocks[0]["attrs"]["title"] == "Table of Contents"
    assert blocks[0]["content"][0]["attrs"]["extensionKey"] == "toc"
    assert blocks[1]["type"] == "heading"


def test_parse_blocks_table_of_contents_heading_is_parsed_as_heading():
    lines = ["# Table of Contents", "", "# Section"]
    blocks = parse_blocks(lines)
    assert blocks[0]["type"] == "heading"
    assert blocks[1]["type"] == "heading"


def test_parse_list_bullet():
    block, i = parse_list(["- one", "- two"], 0)
    assert block["type"] == "bulletList"
    assert len(block["content"]) == 2
    assert i == 2


def test_parse_list_ordered():
    block, i = parse_list(["1. one", "2. two"], 0)
    assert block["type"] == "orderedList"
    assert i == 2


def test_parse_list_nested():
    lines = ["- parent", "  - child"]
    block, i = parse_list(lines, 0)
    assert block["type"] == "bulletList"
    parent_item = block["content"][0]
    nested = [c for c in parent_item["content"] if c.get("type") == "bulletList"]
    assert len(nested) == 1
    assert nested[0]["content"][0]["content"][0]["content"][0]["text"] == "child"


def test_compute_colwidths_no_recognized_headers_returns_none():
    assert compute_colwidths(["Foo", "Bar"]) is None


def test_compute_colwidths_narrow_and_wide_columns():
    widths = compute_colwidths(["#", "Description", "Other"])
    assert widths[0] == 60  # narrow "#"
    assert widths[1] > widths[2]  # "Description" is a wide column


def test_build_table_pads_short_rows():
    table = build_table(["a", "b", "c"], [["1", "2"]])
    data_row = table["content"][1]
    assert len(data_row["content"]) == 3
    assert data_row["content"][2]["content"][0]["content"] == [{"type": "text", "text": ""}]


def test_build_table_default_layout():
    table = build_table(["a", "b"], [["1", "2"]])
    assert table["attrs"]["layout"] == "default"


def test_parse_blocks_wide_table_marker_sets_wide_layout():
    lines = ["<!-- confluence:wide-table -->", "", "| a | b |", "|---|---|", "| 1 | 2 |"]
    blocks = parse_blocks(lines)
    assert len(blocks) == 1
    assert blocks[0]["type"] == "table"
    assert blocks[0]["attrs"]["layout"] == "wide"


def test_parse_blocks_no_marker_keeps_default_layout():
    lines = ["| a | b |", "|---|---|", "| 1 | 2 |"]
    blocks = parse_blocks(lines)
    assert blocks[0]["attrs"]["layout"] == "default"


def test_parse_blocks_wide_table_marker_dropped_if_not_followed_by_table():
    lines = ["<!-- confluence:wide-table -->", "Just a paragraph.", "", "| a | b |", "|---|---|", "| 1 | 2 |"]
    blocks = parse_blocks(lines)
    assert blocks[0]["type"] == "paragraph"
    table_block = next(b for b in blocks if b["type"] == "table")
    assert table_block["attrs"]["layout"] == "default"
