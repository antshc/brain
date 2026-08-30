import subprocess
from unittest.mock import patch

import pytest

from page_diagrams.pipeline import convert_markdown_to_adf, resolve_title, substitute_diagram_notes


def test_resolve_title_from_first_heading():
    md = "intro text\n\n# The Title\n\nmore text\n"
    assert resolve_title(md, None) == "The Title"


def test_resolve_title_explicit_wins_over_heading():
    md = "# Heading Title\n"
    assert resolve_title(md, "Explicit Title") == "Explicit Title"


def test_resolve_title_no_heading_and_no_explicit_raises():
    with pytest.raises(ValueError, match="--title"):
        resolve_title("just text, no heading\n", None)


def test_convert_markdown_to_adf_invokes_sibling_cli_as_subprocess():
    fake_result = subprocess.CompletedProcess(args=[], returncode=0, stdout='{"type": "doc", "content": []}')
    with patch("page_diagrams.pipeline.subprocess.run", return_value=fake_result) as mock_run:
        adf = convert_markdown_to_adf("# Title\n")

    assert adf == {"type": "doc", "content": []}
    called_args = mock_run.call_args.args[0]
    assert called_args[-1] == "md-to-adf"
    assert "map-markdown-adf" in called_args[1]
    assert "map_markdown_adf.py" in called_args[1]


def test_convert_markdown_to_adf_never_imports_converter():
    import page_diagrams.pipeline as pipeline_module

    assert "converter" not in dir(pipeline_module)
    assert not hasattr(pipeline_module, "markdown_to_adf")


def test_convert_markdown_to_adf_reraises_naming_converter_on_nonzero_exit():
    error = subprocess.CalledProcessError(returncode=1, cmd=[], stderr="boom")
    with patch("page_diagrams.pipeline.subprocess.run", side_effect=error):
        with pytest.raises(RuntimeError, match="map-markdown-adf"):
            convert_markdown_to_adf("# Title\n")


def _marker_paragraph(index: int) -> dict:
    return {"type": "paragraph", "content": [{"type": "text", "text": f"\x00MEDIA:{index}\x00"}]}


def test_substitute_diagram_notes_replaces_top_level_marker():
    adf = {"content": [_marker_paragraph(0)]}
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]
    result, replaced = substitute_diagram_notes(adf, diagrams)
    assert replaced == 1
    text = result["content"][0]["content"][0]["text"]
    assert "ATLASSIAN_API_TOKEN" in text
    assert "00-title" in text


def test_substitute_diagram_notes_replaces_marker_nested_inside_expand():
    adf = {
        "content": [
            {
                "type": "expand",
                "attrs": {"title": "Details"},
                "content": [_marker_paragraph(0)],
            }
        ]
    }
    diagrams = [{"index": 0, "code": "graph TD; A-->B;", "name": "00-nested"}]
    result, replaced = substitute_diagram_notes(adf, diagrams)
    assert replaced == 1
    nested = result["content"][0]["content"][0]
    assert nested["type"] == "paragraph"
    assert "ATLASSIAN_API_TOKEN" in nested["content"][0]["text"]
