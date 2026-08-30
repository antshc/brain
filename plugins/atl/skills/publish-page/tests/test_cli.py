import json
from unittest.mock import MagicMock, patch

import pytest

from page_diagrams.cli import main


def test_extract_prints_processed_markdown_and_diagrams(capsys):
    md = "# Title\n\n```mermaid\ngraph TD; A-->B;\n```\n"
    with patch("sys.stdin.read", return_value=md):
        main(["extract"])
    out = json.loads(capsys.readouterr().out)
    assert "\x00MEDIA:0\x00" in out["processedMarkdown"]
    assert out["diagrams"] == [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]


def test_extract_no_diagrams_returns_empty_list(capsys):
    with patch("sys.stdin.read", return_value="just text\n"):
        main(["extract"])
    out = json.loads(capsys.readouterr().out)
    assert out["diagrams"] == []
    assert out["processedMarkdown"] == "just text\n"


def test_extract_strips_ignored_sections_before_finding_mermaid(capsys):
    md = (
        "keep this\n\n"
        "<!-- confluence:ignore:start -->\n"
        "```mermaid\ngraph TD; A-->B;\n```\n"
        "<!-- confluence:ignore:end -->\n"
    )
    with patch("sys.stdin.read", return_value=md):
        main(["extract"])
    out = json.loads(capsys.readouterr().out)
    assert out["diagrams"] == []
    assert "```mermaid" not in out["processedMarkdown"]
    assert "keep this" in out["processedMarkdown"]


def test_extract_reports_unterminated_ignore_start(capsys):
    md = "keep\n<!-- confluence:ignore:start -->\nnever closed\n"
    with patch("sys.stdin.read", return_value=md):
        with pytest.raises(SystemExit):
            main(["extract"])
    err = capsys.readouterr().err
    assert "unterminated" in err


def test_render_attach_reports_mmdc_missing(tmp_path, capsys):
    payload = json.dumps({"diagrams": [{"index": 0, "code": "graph TD; A-->B;", "name": "00-title"}]})
    with patch("sys.stdin.read", return_value=payload), patch(
        "page_diagrams.cli.render_diagrams", side_effect=FileNotFoundError
    ):
        with pytest.raises(SystemExit):
            main(["render-attach", "--assets-dir", str(tmp_path), "--page-id", "123", "--root", str(tmp_path)])
    err = capsys.readouterr().err
    assert "mmdc" in err


def test_render_attach_uploads_and_prints_media_ids(tmp_path, capsys):
    (tmp_path / ".atlassian").write_text(
        "ATLASSIAN_SITE=example.atlassian.net\nATLASSIAN_EMAIL=me@example.com\nATLASSIAN_API_TOKEN=secret\n"
    )
    diagrams = [
        {
            "index": 0,
            "code": "graph TD; A-->B;",
            "name": "00-title",
            "filename": "00-title.png",
            "png_path": "/tmp/00-title.png",
        }
    ]
    payload = json.dumps({"diagrams": diagrams})

    confluence = MagicMock()
    with patch("sys.stdin.read", return_value=payload), patch(
        "page_diagrams.cli.render_diagrams"
    ) as mock_render, patch(
        "page_diagrams.cli.get_confluence", return_value=confluence
    ) as mock_get_confluence, patch(
        "page_diagrams.cli.upload_diagrams", return_value={"00-title.png": "file-1"}
    ) as mock_upload:
        main(["render-attach", "--assets-dir", str(tmp_path), "--page-id", "123", "--root", str(tmp_path)])

    mock_render.assert_called_once()
    mock_get_confluence.assert_called_once()
    mock_upload.assert_called_once_with(confluence, "123", diagrams)

    out = json.loads(capsys.readouterr().out)
    assert out["mediaIdsByIndex"] == {"0": "file-1"}


def test_render_attach_requires_credentials(tmp_path):
    payload = json.dumps(
        {"diagrams": [{"index": 0, "code": "x", "name": "00-x", "filename": "00-x.png", "png_path": "/tmp/00-x.png"}]}
    )
    with patch("sys.stdin.read", return_value=payload), patch("page_diagrams.cli.render_diagrams"):
        with pytest.raises(SystemExit, match="ATLASSIAN"):
            main(["render-attach", "--assets-dir", str(tmp_path), "--page-id", "123", "--root", str(tmp_path)])


def test_render_attach_with_no_diagrams_skips_render_and_upload(tmp_path, capsys):
    payload = json.dumps({"diagrams": []})
    with patch("sys.stdin.read", return_value=payload), patch(
        "page_diagrams.cli.render_diagrams"
    ) as mock_render, patch("page_diagrams.cli.upload_diagrams") as mock_upload:
        main(["render-attach", "--assets-dir", str(tmp_path), "--page-id", "123", "--root", str(tmp_path)])

    mock_render.assert_not_called()
    mock_upload.assert_not_called()
    out = json.loads(capsys.readouterr().out)
    assert out["mediaIdsByIndex"] == {}


def test_render_attach_with_out_writes_file_and_leaves_stdout_clean(tmp_path, capsys):
    (tmp_path / ".atlassian").write_text(
        "ATLASSIAN_SITE=example.atlassian.net\nATLASSIAN_EMAIL=me@example.com\nATLASSIAN_API_TOKEN=secret\n"
    )
    diagrams = [
        {
            "index": 0,
            "code": "graph TD; A-->B;",
            "name": "00-title",
            "filename": "00-title.png",
            "png_path": "/tmp/00-title.png",
        }
    ]
    payload = json.dumps({"diagrams": diagrams})
    out_path = tmp_path / "media-ids.json"

    with patch("sys.stdin.read", return_value=payload), patch("page_diagrams.cli.render_diagrams"), patch(
        "page_diagrams.cli.get_confluence", return_value=MagicMock()
    ), patch("page_diagrams.cli.upload_diagrams", return_value={"00-title.png": "file-1"}):
        main(
            [
                "render-attach",
                "--assets-dir", str(tmp_path),
                "--page-id", "123",
                "--root", str(tmp_path),
                "--out", str(out_path),
            ]
        )

    assert capsys.readouterr().out == ""
    assert json.loads(out_path.read_text()) == {"mediaIdsByIndex": {"0": "file-1"}}


def test_replace_markers_prints_final_adf_and_count(capsys):
    adf = {
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "\x00MEDIA:0\x00"}]},
        ]
    }
    payload = json.dumps({"adf": adf, "mediaIdsByIndex": {"0": "file-1"}})
    with patch("sys.stdin.read", return_value=payload):
        main(["replace-markers", "--page-id", "123"])
    out = json.loads(capsys.readouterr().out)
    assert out["replaced"] == 1
    assert out["adf"]["content"][0]["type"] == "mediaSingle"
    assert out["adf"]["content"][0]["content"][0]["attrs"]["collection"] == "contentId-123"


def test_substitute_media_prints_final_adf_and_count(capsys):
    adf = {
        "content": [
            {
                "type": "expand",
                "attrs": {"title": "Details"},
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": "\x00MEDIA:0\x00"}]}],
            }
        ]
    }
    payload = json.dumps({"adf": adf, "mediaIdsByIndex": {"0": "file-1"}})
    with patch("sys.stdin.read", return_value=payload):
        main(["substitute-media", "--page-id", "123"])
    out = json.loads(capsys.readouterr().out)
    assert out["replaced"] == 1
    assert out["adf"]["content"][0]["content"][0]["type"] == "mediaSingle"


def test_substitute_media_exits_on_leftover_marker(capsys):
    leftover = {
        "type": "paragraph",
        "content": [{"type": "text", "text": "before "}, {"type": "text", "text": "\x00MEDIA:0\x00"}],
    }
    adf = {"content": [leftover]}
    payload = json.dumps({"adf": adf, "mediaIdsByIndex": {"0": "file-1"}})
    with patch("sys.stdin.read", return_value=payload):
        with pytest.raises(SystemExit):
            main(["substitute-media", "--page-id", "123"])
    err = capsys.readouterr().err
    assert "MEDIA:0" in err


def test_publish_adf_small_body_signals_mcp(capsys):
    adf = {"type": "doc", "content": []}
    payload = json.dumps({"adf": adf})
    with patch("sys.stdin.read", return_value=payload):
        main(["publish-adf", "--page-id", "123", "--threshold-bytes", "200000"])
    out = json.loads(capsys.readouterr().out)
    assert out["method"] == "mcp"
    assert out["thresholdBytes"] == 200000


def test_publish_adf_large_body_updates_existing_page(tmp_path, capsys):
    (tmp_path / ".atlassian").write_text(
        "ATLASSIAN_SITE=example.atlassian.net\nATLASSIAN_EMAIL=me@example.com\nATLASSIAN_API_TOKEN=secret\n"
    )
    adf = {"type": "doc", "content": []}
    payload = json.dumps({"adf": adf})

    confluence = MagicMock()
    with patch("sys.stdin.read", return_value=payload), patch(
        "page_diagrams.cli.get_confluence", return_value=confluence
    ), patch("page_diagrams.cli.get_page_version", return_value=3) as mock_version, patch(
        "page_diagrams.cli.update_page_adf", return_value={"id": "123"}
    ) as mock_update:
        main(
            [
                "publish-adf",
                "--page-id", "123",
                "--title", "Title",
                "--root", str(tmp_path),
                "--threshold-bytes", "1",
            ]
        )

    mock_version.assert_called_once_with(confluence, "123")
    mock_update.assert_called_once_with(confluence, "123", "Title", adf, 3)
    out = json.loads(capsys.readouterr().out)
    assert out == {"method": "rest", "pageId": "123", "sizeBytes": len(json.dumps(adf).encode("utf-8"))}


def test_publish_adf_large_body_creates_new_page(tmp_path, capsys):
    (tmp_path / ".atlassian").write_text(
        "ATLASSIAN_SITE=example.atlassian.net\nATLASSIAN_EMAIL=me@example.com\nATLASSIAN_API_TOKEN=secret\n"
    )
    adf = {"type": "doc", "content": []}
    payload = json.dumps({"adf": adf})

    confluence = MagicMock()
    with patch("sys.stdin.read", return_value=payload), patch(
        "page_diagrams.cli.get_confluence", return_value=confluence
    ), patch("page_diagrams.cli.create_page_adf", return_value={"id": "456"}) as mock_create:
        main(
            [
                "publish-adf",
                "--space-id", "space-1",
                "--title", "Title",
                "--root", str(tmp_path),
                "--threshold-bytes", "1",
            ]
        )

    mock_create.assert_called_once_with(confluence, "space-1", "Title", adf)
    out = json.loads(capsys.readouterr().out)
    assert out == {"method": "rest", "pageId": "456", "sizeBytes": len(json.dumps(adf).encode("utf-8"))}
