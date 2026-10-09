import pytest

PLAIN = "# Title\n\nSome **bold** text.\n\n- one\n- two\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n\n```python\nx = 1\n```\n"


def test_plain_commonmark_is_markdown_safe(detect_adf_only):
    report = detect_adf_only(PLAIN)
    assert report == {"adfOnly": False, "constructs": []}


@pytest.mark.parametrize(
    ("markdown_text", "kind"),
    [
        ("<details>\n<summary>More</summary>\n\nbody\n\n</details>", "expand"),
        ("> [!WARNING]\n> mind the gap", "panel"),
        ("Ticket is [STATUS:Done|green] now.", "status"),
        ("<!-- adf:toc -->", "toc"),
        ("<!-- adf:wide-table -->\n\n| a |\n| --- |", "wideTable"),
    ],
)
def test_each_adf_only_construct_is_detected(detect_adf_only, markdown_text, kind):
    report = detect_adf_only(markdown_text)
    assert report["adfOnly"] is True
    assert kind in {c["kind"] for c in report["constructs"]}


def test_marker_inside_fenced_block_is_literal_text(detect_adf_only):
    markdown_text = "Example:\n\n```html\n<details>\n<summary>More</summary>\n</details>\n```\n"
    assert detect_adf_only(markdown_text) == {"adfOnly": False, "constructs": []}


def test_status_inside_fenced_block_is_literal_text(detect_adf_only):
    assert detect_adf_only("```\n[STATUS:Done|green]\n```\n")["adfOnly"] is False


def test_details_block_reports_one_expand(detect_adf_only):
    report = detect_adf_only("<details>\n<summary>More</summary>\n\nbody\n\n</details>")
    assert report["constructs"] == [{"kind": "expand", "line": 1}]


def test_plain_blockquote_is_not_a_panel(detect_adf_only):
    assert detect_adf_only("> just a quote")["adfOnly"] is False


def test_multiple_constructs_report_source_order_and_line_numbers(detect_adf_only):
    markdown_text = "<!-- adf:toc -->\n\n> [!INFO]\n> note\n\nSee [STATUS:Open|blue].\n"
    report = detect_adf_only(markdown_text)
    assert [(c["kind"], c["line"]) for c in report["constructs"]] == [
        ("toc", 1),
        ("panel", 3),
        ("status", 6),
    ]
