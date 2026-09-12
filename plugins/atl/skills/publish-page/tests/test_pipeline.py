import subprocess
from unittest.mock import MagicMock, patch

import pytest

from page_diagrams.pipeline import convert_markdown_to_adf, publish, resolve_title, substitute_diagram_notes


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


def _write_page(tmp_path, renderer=None, extension_key=None):
    md_path = tmp_path / "page.md"
    md_path.write_text("# Title\n\n```mermaid\ngraph TD; A-->B;\n```\n")
    config = (
        "ATLASSIAN_SITE=example.atlassian.net\nATLASSIAN_EMAIL=me@example.com\nATLASSIAN_API_TOKEN=secret\n"
    )
    if renderer:
        config += f"ATLASSIAN_DIAGRAM_RENDERER={renderer}\n"
    if extension_key:
        config += f"ATLASSIAN_DRAWIO_EXTENSION_KEY={extension_key}\n"
    (tmp_path / ".atlassian").write_text(config)
    return md_path


def _publish(md_path, tmp_path):
    return publish(
        md_path=str(md_path),
        root=str(tmp_path),
        page_id="123",
        space_id=None,
        title=None,
        assets_dir=str(tmp_path / "assets"),
        out_path=str(tmp_path / "final.json"),
        threshold_bytes=0,
    )


def test_publish_png_branch_passes_the_selected_renderer_through(tmp_path):
    md_path = _write_page(tmp_path)
    base_adf = {"content": [_marker_paragraph(0)]}

    def fake_render(diagrams, assets_dir, background="white", renderer="png"):
        for d in diagrams:
            d["filename"] = f"{d['name']}.png"

    with patch("page_diagrams.pipeline.convert_markdown_to_adf", return_value=base_adf), patch(
        "page_diagrams.pipeline.get_confluence", return_value=MagicMock()
    ), patch("page_diagrams.pipeline.render_diagrams", side_effect=fake_render) as mock_render, patch(
        "page_diagrams.pipeline.upload_diagrams", return_value={"00-title.png": "file-1"}
    ), patch("page_diagrams.pipeline.get_page_version", return_value=1), patch(
        "page_diagrams.pipeline.update_page_adf", return_value={"id": "123"}
    ), patch("page_diagrams.pipeline.substitute_media", return_value=(base_adf, 1)):
        result = _publish(md_path, tmp_path)

    assert mock_render.call_args.kwargs["renderer"] == "png"
    assert result["renderer"] == "png"


def test_publish_refuses_the_mermaid_renderer_before_touching_a_page(tmp_path):
    md_path = _write_page(tmp_path, "mermaid")

    with patch("page_diagrams.pipeline.get_confluence") as mock_confluence, patch(
        "page_diagrams.pipeline.render_diagrams"
    ) as mock_render:
        with pytest.raises(RuntimeError, match="section 7"):
            _publish(md_path, tmp_path)

    mock_confluence.assert_not_called()
    mock_render.assert_not_called()


def test_publish_rejects_an_unknown_renderer_before_touching_a_page(tmp_path):
    md_path = _write_page(tmp_path, "svg")

    with patch("page_diagrams.pipeline.get_confluence") as mock_confluence:
        with pytest.raises(ValueError, match="svg"):
            _publish(md_path, tmp_path)

    mock_confluence.assert_not_called()


def _fake_drawio_render(diagrams, assets_dir, background="white", renderer="png"):
    for d in diagrams:
        d["diagram_name"] = f"{d['name']}.drawio"
        d["search"] = "Start Done"
        d["width"], d["height"] = 841, 571
        d["renderer"] = "drawio"
        d["attachments"] = [
            {"path": f"/tmp/{d['name']}.drawio", "filename": f"{d['name']}.drawio"},
            {"path": f"/tmp/{d['name']}.drawio.png", "filename": f"{d['name']}.drawio.png"},
        ]


def test_publish_drawio_branch_registers_custom_content_and_injects_the_macro(tmp_path):
    md_path = _write_page(tmp_path, "drawio", "app-1/env-1/static/drawio")
    base_adf = {"content": [_marker_paragraph(0)]}
    file_ids = {"00-title.drawio": "file-1", "00-title.drawio.png": "file-2"}

    with patch("page_diagrams.pipeline.convert_markdown_to_adf", return_value=base_adf), patch(
        "page_diagrams.pipeline.get_confluence", return_value=MagicMock()
    ), patch("page_diagrams.pipeline.render_diagrams", side_effect=_fake_drawio_render), patch(
        "page_diagrams.pipeline.upload_diagrams", return_value=file_ids
    ), patch("page_diagrams.pipeline.get_page_version", return_value=1), patch(
        "page_diagrams.pipeline.update_page_adf", return_value={"id": "123"}
    ), patch(
        "page_diagrams.pipeline.upsert_diagram", return_value={"id": "999", "revision": 1}
    ) as mock_upsert:
        result = _publish(md_path, tmp_path)

    mock_upsert.assert_called_once()
    assert mock_upsert.call_args.args[1:] == ("123", "00-title.drawio", "Start Done")

    node = base_adf["content"][0]
    assert node["type"] == "extension"
    assert node["attrs"]["extensionKey"] == "app-1/env-1/static/drawio"
    guest = node["attrs"]["parameters"]["guestParams"]
    assert guest["custContentId"] == "999"
    assert guest["pageId"] == "123"
    assert guest["baseUrl"] == "https://example.atlassian.net/wiki"
    assert (guest["width"], guest["height"]) == (841, 571)

    assert result["renderer"] == "drawio"
    assert result["attachments"] == 2


def test_publish_drawio_republish_reuses_the_existing_custom_content(tmp_path):
    md_path = _write_page(tmp_path, "drawio", "app-1/env-1/static/drawio")
    base_adf = {"content": [_marker_paragraph(0)]}
    confluence = MagicMock()
    confluence.get.side_effect = [
        {"results": [{"id": "999", "title": "00-title.drawio", "version": {"number": 1}}]},
        {"space": {"key": "SPACE"}},
    ]

    with patch("page_diagrams.pipeline.convert_markdown_to_adf", return_value=base_adf), patch(
        "page_diagrams.pipeline.get_confluence", return_value=confluence
    ), patch("page_diagrams.pipeline.render_diagrams", side_effect=_fake_drawio_render), patch(
        "page_diagrams.pipeline.upload_diagrams", return_value={}
    ), patch("page_diagrams.pipeline.get_page_version", return_value=1), patch(
        "page_diagrams.pipeline.update_page_adf", return_value={"id": "123"}
    ):
        _publish(md_path, tmp_path)

    confluence.post.assert_not_called()
    assert confluence.put.call_args.args[0] == "/rest/api/content/999"
    guest = base_adf["content"][0]["attrs"]["parameters"]["guestParams"]
    assert guest["custContentId"] == "999"
    assert guest["revision"] == 2
    assert guest["contentVer"] == 2


def test_publish_drawio_branch_injects_a_media_node_for_a_diagram_that_fell_back_to_png(tmp_path):
    md_path = _write_page(tmp_path, "drawio", "app-1/env-1/static/drawio")
    base_adf = {"content": [_marker_paragraph(0)]}

    def fell_back_to_png(diagrams, assets_dir, background="white", renderer="png"):
        for d in diagrams:
            d["renderer"] = "png"
            d["filename"] = f"{d['name']}.png"
            d["attachments"] = [{"path": f"/tmp/{d['name']}.png", "filename": d["filename"]}]

    with patch("page_diagrams.pipeline.convert_markdown_to_adf", return_value=base_adf), patch(
        "page_diagrams.pipeline.get_confluence", return_value=MagicMock()
    ), patch("page_diagrams.pipeline.render_diagrams", side_effect=fell_back_to_png), patch(
        "page_diagrams.pipeline.upload_diagrams", return_value={"00-title.png": "file-1"}
    ), patch("page_diagrams.pipeline.get_page_version", return_value=1), patch(
        "page_diagrams.pipeline.update_page_adf", return_value={"id": "123"}
    ), patch("page_diagrams.pipeline.upsert_diagram") as mock_upsert:
        _publish(md_path, tmp_path)

    mock_upsert.assert_not_called()
    node = base_adf["content"][0]
    assert node["type"] == "mediaSingle"
    assert node["content"][0]["attrs"]["id"] == "file-1"


def test_publish_drawio_without_the_extension_key_fails_before_touching_a_page(tmp_path):
    md_path = _write_page(tmp_path, "drawio")

    with patch("page_diagrams.pipeline.get_confluence") as mock_confluence, patch(
        "page_diagrams.pipeline.render_diagrams"
    ) as mock_render:
        with pytest.raises(ValueError, match="ATLASSIAN_DRAWIO_EXTENSION_KEY"):
            _publish(md_path, tmp_path)

    mock_confluence.assert_not_called()
    mock_render.assert_not_called()
