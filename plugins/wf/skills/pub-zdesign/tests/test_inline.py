from zdesign_publisher.inline import parse_inline


def test_plain_text():
    assert parse_inline("hello world") == [{"type": "text", "text": "hello world"}]


def test_strong():
    assert parse_inline("**bold**") == [{"type": "text", "text": "bold", "marks": [{"type": "strong"}]}]


def test_em():
    assert parse_inline("*italic*") == [{"type": "text", "text": "italic", "marks": [{"type": "em"}]}]


def test_em_underscore():
    assert parse_inline("_italic_") == [{"type": "text", "text": "italic", "marks": [{"type": "em"}]}]


def test_strong_underscore():
    assert parse_inline("__bold__") == [{"type": "text", "text": "bold", "marks": [{"type": "strong"}]}]


def test_code():
    assert parse_inline("`code`") == [{"type": "text", "text": "code", "marks": [{"type": "code"}]}]


def test_strike():
    assert parse_inline("~~gone~~") == [{"type": "text", "text": "gone", "marks": [{"type": "strike"}]}]


def test_link():
    assert parse_inline("[label](https://example.com)") == [
        {"type": "text", "text": "label", "marks": [{"type": "link", "attrs": {"href": "https://example.com"}}]}
    ]


def test_link_without_label_uses_href():
    assert parse_inline("[](https://example.com)") == [
        {"type": "text", "text": "https://example.com", "marks": [{"type": "link", "attrs": {"href": "https://example.com"}}]}
    ]


def test_hard_break_splits_on_br():
    nodes = parse_inline("line one<br>line two")
    assert nodes == [
        {"type": "text", "text": "line one"},
        {"type": "hardBreak"},
        {"type": "text", "text": "line two"},
    ]


def test_mixed_marks_and_plain_text_around_them():
    nodes = parse_inline("see **bold** and `code` here")
    assert nodes == [
        {"type": "text", "text": "see "},
        {"type": "text", "text": "bold", "marks": [{"type": "strong"}]},
        {"type": "text", "text": " and "},
        {"type": "text", "text": "code", "marks": [{"type": "code"}]},
        {"type": "text", "text": " here"},
    ]


def test_empty_string_yields_single_empty_text_node():
    assert parse_inline("") == [{"type": "text", "text": ""}]
