"""Inline comment anchors: `<!-- adf:comment id="..." -->text<!-- /adf:comment -->` <-> ADF
`annotation` mark (`annotationType: inlineComment`)."""
from __future__ import annotations


def _ann(comment_id: str) -> dict:
    return {"type": "annotation", "attrs": {"annotationType": "inlineComment", "id": comment_id}}


def _inline(doc: dict) -> list[dict]:
    return doc["content"][0]["content"]


def test_md_to_adf_marks_every_text_node_in_the_span(md_to_adf):
    doc = md_to_adf('A <!-- adf:comment id="c1" -->x **bold** y<!-- /adf:comment --> z')
    assert _inline(doc) == [
        {"type": "text", "text": "A "},
        {"type": "text", "text": "x ", "marks": [_ann("c1")]},
        {"type": "text", "text": "bold", "marks": [{"type": "strong"}, _ann("c1")]},
        {"type": "text", "text": " y", "marks": [_ann("c1")]},
        {"type": "text", "text": " z"},
    ]


def test_md_to_adf_comment_inside_another_mark(md_to_adf):
    doc = md_to_adf('**a <!-- adf:comment id="c1" -->b<!-- /adf:comment -->**')
    assert _inline(doc) == [
        {"type": "text", "text": "a ", "marks": [{"type": "strong"}]},
        {"type": "text", "text": "b", "marks": [_ann("c1"), {"type": "strong"}]},
    ]


def test_md_to_adf_nested_comments_stack_marks(md_to_adf):
    doc = md_to_adf('<!-- adf:comment id="o" -->a<!-- adf:comment id="i" -->b<!-- /adf:comment -->c<!-- /adf:comment -->')
    assert _inline(doc) == [
        {"type": "text", "text": "a", "marks": [_ann("o")]},
        {"type": "text", "text": "b", "marks": [_ann("i"), _ann("o")]},
        {"type": "text", "text": "c", "marks": [_ann("o")]},
    ]


def test_md_to_adf_tag_inside_code_span_is_literal(md_to_adf):
    doc = md_to_adf('`<!-- adf:comment id="x" -->`')
    assert _inline(doc) == [{"type": "text", "text": '<!-- adf:comment id="x" -->', "marks": [{"type": "code"}]}]


def test_md_to_adf_rejects_unterminated_comment(run_cli):
    result = run_cli("md-to-adf", 'a <!-- adf:comment id="x" -->b\n')
    assert result.returncode == 1
    assert "unterminated" in result.stderr
    assert result.stdout == ""


def test_md_to_adf_rejects_stray_close_tag(run_cli):
    result = run_cli("md-to-adf", "a <!-- /adf:comment --> b\n")
    assert result.returncode == 1
    assert "stray" in result.stderr


def test_adf_to_md_wraps_a_mixed_mark_run_once(adf_to_md):
    doc = {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "x ", "marks": [_ann("c1")]},
                    {"type": "text", "text": "bold", "marks": [{"type": "strong"}, _ann("c1")]},
                    {"type": "text", "text": " tail"},
                ],
            }
        ],
    }
    assert adf_to_md(doc) == '<!-- adf:comment id="c1" -->x **bold**<!-- /adf:comment --> tail'


def test_adf_to_md_hard_break_splits_the_span(adf_to_md):
    doc = {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Line 2", "marks": [_ann("c1")]},
                    {"type": "hardBreak"},
                    {"type": "text", "text": "Line 3"},
                ],
            }
        ],
    }
    assert adf_to_md(doc) == '<!-- adf:comment id="c1" -->Line 2<!-- /adf:comment -->  \nLine 3'


def test_adf_to_md_drops_non_comment_annotations(adf_to_md):
    other = {"type": "annotation", "attrs": {"annotationType": "other", "id": "z"}}
    doc = {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "t", "marks": [other]}]}]}
    assert adf_to_md(doc) == "t"


def test_round_trip_preserves_comment_ids(md_to_adf, adf_to_md):
    source = (
        'A <!-- adf:comment id="a0b99581-1f84-4c1a-b229-983b2395cf97" -->Line 2<!-- /adf:comment --> end\n\n'
        '<!-- adf:comment id="o" -->a<!-- adf:comment id="i" -->[b](https://e.x)<!-- /adf:comment -->c<!-- /adf:comment -->\n\n'
        "| A | B |\n| --- | --- |\n| <!-- adf:comment id=\"t\" -->cell<!-- /adf:comment --> | x |"
    )
    assert adf_to_md(md_to_adf(source)) == source


def test_detect_reports_inline_comment(detect_adf_only):
    report = detect_adf_only('text <!-- adf:comment id="c" -->x<!-- /adf:comment -->\n\n```\n<!-- adf:comment id="f" -->\n```\n')
    assert report == {"adfOnly": True, "constructs": [{"kind": "inlineComment", "line": 1}]}
