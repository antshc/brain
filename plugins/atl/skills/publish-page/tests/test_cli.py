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
