from unittest.mock import MagicMock, patch

import pytest

from zdesign_publisher.cli import main, resolve_page_id


def test_resolve_page_id_returns_given_page_id():
    confluence = MagicMock()
    assert resolve_page_id(confluence, "999", None, None) == "999"
    confluence.create_page.assert_not_called()


def test_resolve_page_id_creates_page_when_no_page_id_given():
    confluence = MagicMock()
    confluence.create_page.return_value = {"id": "new-id"}
    result = resolve_page_id(confluence, None, "SPACE", "Title")
    assert result == "new-id"
    confluence.create_page.assert_called_once_with("SPACE", "Title", "", representation="storage")


def test_resolve_page_id_requires_space_key_and_title():
    confluence = MagicMock()
    with pytest.raises(SystemExit, match="--page-id"):
        resolve_page_id(confluence, None, None, None)
    with pytest.raises(SystemExit):
        resolve_page_id(confluence, None, "SPACE", None)


def test_main_end_to_end_with_mocked_seams(tmp_path, capsys):
    md_path = tmp_path / "design.md"
    md_path.write_text("# My Design\n\n```mermaid\ngraph TD; A-->B;\n```\n")

    env_path = tmp_path / ".atlmcp.env"
    env_path.write_text('ACLI_SITE="example.atlassian.net"\nACLI_EMAIL=me@example.com\nACLI_API_TOKEN=secret\n')

    confluence = MagicMock()
    confluence.get.return_value = {
        "body": {"atlas_doc_format": {"value": '{"content": "...file-id-1..."}'}},
        "version": {"number": 3},
        "_links": {"webui": "/wiki/spaces/SP/pages/123/My+Design"},
    }

    def fake_render_diagrams(diagrams, assets_dir, background="white"):
        for d in diagrams:
            d["filename"] = f"{d['name']}.png"

    with patch("zdesign_publisher.cli.get_confluence", return_value=confluence) as mock_get_confluence, patch(
        "zdesign_publisher.cli.render_diagrams", side_effect=fake_render_diagrams
    ) as mock_render, patch(
        "zdesign_publisher.cli.upload_diagrams", return_value={"00-my-design.png": "file-id-1"}
    ) as mock_upload:
        main(["--md", str(md_path), "--page-id", "123", "--env", str(env_path)])

    mock_get_confluence.assert_called_once()
    mock_render.assert_called_once()
    mock_upload.assert_called_once()
    confluence.update_page.assert_called_once()
    update_kwargs = confluence.update_page.call_args.kwargs
    assert update_kwargs["page_id"] == "123"
    assert update_kwargs["title"] == "My Design"
    assert update_kwargs["representation"] == "atlas_doc_format"
    assert update_kwargs["always_update"] is True

    out = capsys.readouterr().out
    assert "page_id=123" in out
    assert "version=3" in out
    assert "url=https://example.atlassian.net/wiki/spaces/SP/pages/123/My+Design" in out


def test_main_raises_when_media_id_missing_from_published_body(tmp_path):
    md_path = tmp_path / "design.md"
    md_path.write_text("# My Design\n\n```mermaid\ngraph TD; A-->B;\n```\n")

    env_path = tmp_path / ".atlmcp.env"
    env_path.write_text('ACLI_SITE="example.atlassian.net"\nACLI_EMAIL=me@example.com\nACLI_API_TOKEN=secret\n')

    confluence = MagicMock()
    confluence.get.return_value = {
        "body": {"atlas_doc_format": {"value": "{}"}},  # no file id present
        "version": {"number": 1},
        "_links": {},
    }

    def fake_render_diagrams(diagrams, assets_dir, background="white"):
        for d in diagrams:
            d["filename"] = f"{d['name']}.png"

    with patch("zdesign_publisher.cli.get_confluence", return_value=confluence), patch(
        "zdesign_publisher.cli.render_diagrams", side_effect=fake_render_diagrams
    ), patch("zdesign_publisher.cli.upload_diagrams", return_value={"00-my-design.png": "file-id-1"}):
        with pytest.raises(RuntimeError, match="missing from published body"):
            main(["--md", str(md_path), "--page-id", "123", "--env", str(env_path)])


def test_main_requires_existing_markdown_file(tmp_path):
    with pytest.raises(SystemExit, match="not found"):
        main(["--md", str(tmp_path / "missing.md"), "--page-id", "123"])


def test_main_strips_ignored_sections_before_publishing(tmp_path):
    md_path = tmp_path / "design.md"
    md_path.write_text(
        "# My Design\n\nkeep this\n\n"
        "<!-- confluence:ignore:start -->\n# Source Material\nsecret provenance\n"
        "<!-- confluence:ignore:end -->\n"
    )

    env_path = tmp_path / ".atlmcp.env"
    env_path.write_text('ACLI_SITE="example.atlassian.net"\nACLI_EMAIL=me@example.com\nACLI_API_TOKEN=secret\n')

    confluence = MagicMock()
    confluence.get.return_value = {
        "body": {"atlas_doc_format": {"value": "{}"}},
        "version": {"number": 1},
        "_links": {},
    }

    with patch("zdesign_publisher.cli.get_confluence", return_value=confluence), patch(
        "zdesign_publisher.cli.render_diagrams"
    ), patch("zdesign_publisher.cli.upload_diagrams", return_value={}):
        main(["--md", str(md_path), "--page-id", "123", "--env", str(env_path)])

    published_body = confluence.update_page.call_args.kwargs["body"]
    assert "secret provenance" not in published_body
    assert "Source Material" not in published_body
    assert "keep this" in published_body
