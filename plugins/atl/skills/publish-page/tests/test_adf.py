import pytest

from page_diagrams.adf import replace_markers, substitute_media


def _marker_paragraph(index: int) -> dict:
    return {"type": "paragraph", "content": [{"type": "text", "text": f"\x00MEDIA:{index}\x00"}]}


def test_replace_markers_swaps_marker_paragraphs_for_media_nodes():
    adf = {
        "content": [
            {"type": "heading", "content": [{"type": "text", "text": "Title"}]},
            _marker_paragraph(0),
            {"type": "paragraph", "content": [{"type": "text", "text": "some text"}]},
        ]
    }
    result, replaced = replace_markers(adf, {"0": "file-1"}, "123")
    assert replaced == 1
    assert result["content"][1] == {
        "type": "mediaSingle",
        "attrs": {"layout": "center", "width": 768, "widthType": "pixel"},
        "content": [{"type": "media", "attrs": {"id": "file-1", "type": "file", "collection": "contentId-123"}}],
    }
    assert result["content"][0]["type"] == "heading"
    assert result["content"][2]["content"][0]["text"] == "some text"


def test_replace_markers_handles_multiple_markers_and_no_markers():
    adf = {"content": [_marker_paragraph(0), _marker_paragraph(1)]}
    result, replaced = replace_markers(adf, {"0": "file-0", "1": "file-1"}, "999")
    assert replaced == 2
    assert result["content"][0]["content"][0]["attrs"]["id"] == "file-0"
    assert result["content"][1]["content"][0]["attrs"]["id"] == "file-1"

    adf_no_markers = {"content": [{"type": "paragraph", "content": [{"type": "text", "text": "plain"}]}]}
    result_no_markers, replaced_none = replace_markers(adf_no_markers, {}, "1")
    assert replaced_none == 0
    assert result_no_markers["content"][0]["content"][0]["text"] == "plain"


def test_substitute_media_replaces_marker_nested_inside_expand():
    adf = {
        "content": [
            {
                "type": "expand",
                "attrs": {"title": "Details"},
                "content": [_marker_paragraph(0)],
            },
        ]
    }
    result, replaced = substitute_media(adf, {"0": "file-1"}, "123")
    assert replaced == 1
    nested = result["content"][0]["content"][0]
    assert nested["type"] == "mediaSingle"
    assert nested["content"][0]["attrs"]["id"] == "file-1"


def test_substitute_media_raises_on_leftover_marker():
    # A marker mixed into a paragraph with other text isn't recognized as a substitutable
    # marker node, so it survives substitution — the verification gate must catch it.
    leftover = {
        "type": "paragraph",
        "content": [{"type": "text", "text": "before "}, {"type": "text", "text": "\x00MEDIA:1\x00"}],
    }
    adf = {"content": [_marker_paragraph(0), leftover]}
    with pytest.raises(RuntimeError, match=r"MEDIA:1"):
        substitute_media(adf, {"0": "file-0"}, "123")
