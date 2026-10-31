import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from requests.exceptions import ConnectionError as RequestsConnectionError

from assemble_page import (
    ConversionError,
    PageFetchError,
    assemble,
    convert_adf_to_markdown,
    default_assets_dir,
    extract_title_and_body,
    fetch_page,
)
from fetch_diagrams import AttachmentRetrievalError


def _page(title: str, body: dict) -> dict:
    return {"title": title, "body": {"atlas_doc_format": {"value": json.dumps(body), "representation": "atlas_doc_format"}}}


def _drawio_body() -> dict:
    return {
        "type": "doc",
        "version": 1,
        "content": [{"type": "extension", "attrs": {"extensionKey": "app/env/static/drawio"}}],
    }


def _confluence_stub(attachments, downloads):
    confluence = MagicMock()
    confluence.get_attachments_from_content.return_value = {"results": attachments}
    confluence.get.side_effect = lambda link, **kwargs: downloads[link]
    return confluence


def test_default_assets_dir_appends_assets_to_the_full_markdown_name():
    assert default_assets_dir(Path("docs/page.md")) == Path("docs/page.md.assets")


def test_extract_title_and_body_parses_the_rest_v2_adf_string():
    body = {"type": "doc", "version": 1, "content": []}
    title, extracted_body = extract_title_and_body(_page("Behavior Diagram", body))

    assert title == "Behavior Diagram"
    assert extracted_body == body


def test_extract_title_and_body_rejects_a_non_object_body():
    page = {"title": "T", "body": {"atlas_doc_format": {"value": "[]"}}}

    with pytest.raises(ConversionError, match="must be a JSON object"):
        extract_title_and_body(page)


def test_fetch_page_reads_rest_v2_with_atlas_doc_format():
    body = {"type": "doc", "version": 1, "content": []}
    confluence = MagicMock()
    confluence.get.return_value = _page("Behavior Diagram", body)

    assert fetch_page(confluence, "123") == ("Behavior Diagram", body)
    confluence.get.assert_called_once_with("/api/v2/pages/123", params={"body-format": "atlas_doc_format"})


def test_fetch_page_raises_a_safe_category_on_request_failure():
    confluence = MagicMock()
    confluence.get.side_effect = RequestsConnectionError("https://secret.example/?token=abc")

    with pytest.raises(PageFetchError) as excinfo:
        fetch_page(confluence, "123")

    assert str(excinfo.value) == "ConnectionError"


def test_convert_adf_to_markdown_shells_out_to_map_markdown_adf(monkeypatch):
    captured = {}

    def fake_run(cmd, input, capture_output, text):  # noqa: A002
        captured["cmd"] = cmd
        captured["input"] = input
        return MagicMock(returncode=0, stdout="# Title\n\nBody.\n", stderr="")

    monkeypatch.setattr("assemble_page.subprocess.run", fake_run)

    body = {"type": "doc", "version": 1, "content": []}
    markdown = convert_adf_to_markdown(body)

    assert markdown == "# Title\n\nBody.\n"
    assert captured["cmd"][-1] == "adf-to-md"
    assert json.loads(captured["input"]) == body


def test_convert_adf_to_markdown_raises_sanitized_conversion_error_without_a_traceback(monkeypatch):
    def fake_run(cmd, input, capture_output, text):  # noqa: A002
        return MagicMock(returncode=1, stdout="", stderr="error: unhandled inline node type 'weirdNode'\n")

    monkeypatch.setattr("assemble_page.subprocess.run", fake_run)

    with pytest.raises(ConversionError) as excinfo:
        convert_adf_to_markdown({"type": "doc", "version": 1, "content": []})

    assert str(excinfo.value) == "error: unhandled inline node type 'weirdNode'"


def test_assemble_skips_attachment_handling_for_a_page_with_no_references(monkeypatch, tmp_path):
    monkeypatch.setattr("assemble_page.convert_adf_to_markdown", lambda body: "Presentation text.\n")
    confluence = MagicMock()

    assets_dir = tmp_path / "page.md.tmp"
    result = assemble("Simple Page", {"type": "doc", "version": 1, "content": []}, "123", confluence, str(assets_dir))

    assert result == "# Simple Page\n\nPresentation text.\n"
    confluence.assert_not_called()
    assert not assets_dir.exists()

def test_assemble_saves_attachments_and_restores_diagrams_when_reference_present_and_token_available(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(
        "assemble_page.convert_adf_to_markdown",
        lambda body: '<!-- adf:diagram drawio="order-flow.drawio" -->',
    )
    confluence = MagicMock()
    snapshot = MagicMock()
    fetch_attachment_snapshot = MagicMock(return_value=snapshot)
    publish_attachment_cache = MagicMock()
    monkeypatch.setattr("assemble_page.fetch_attachment_snapshot", fetch_attachment_snapshot)
    monkeypatch.setattr("assemble_page.publish_attachment_cache", publish_attachment_cache)
    monkeypatch.setattr(
        "assemble_page.restore_diagrams",
        lambda markdown, snapshot_, assets_dir_name: "```mermaid\nflowchart TD; A-->B;\n```",
    )

    assets_dir = tmp_path / "page.md.tmp"
    result = assemble("Complex Page", _drawio_body(), "123", confluence, str(assets_dir))

    assert result == "# Complex Page\n\n```mermaid\nflowchart TD; A-->B;\n```"
    fetch_attachment_snapshot.assert_called_once_with(confluence, "123")
    publish_attachment_cache.assert_called_once_with(snapshot, str(assets_dir))


def test_assemble_does_not_duplicate_a_title_the_body_already_carries_as_h1(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "assemble_page.convert_adf_to_markdown",
        lambda body: "# Behavior Diagram\n\nPresentation text.\n",
    )

    result = assemble(
        "Behavior Diagram", {"type": "doc", "version": 1, "content": []}, "123", MagicMock(), str(tmp_path / "page.md.tmp")
    )

    assert result == "# Behavior Diagram\n\nPresentation text.\n"


def test_assemble_end_to_end_covers_all_three_rendering_rules(monkeypatch, tmp_path):
    attachments = [
        {
            "title": "order-flow.drawio",
            "extensions": {"fileId": "diagram-1"},
            "_links": {"download": "/download/order-flow.drawio"},
        },
        {"title": "order-flow.source.mmd", "_links": {"download": "/download/order-flow.source.mmd"}},
        {
            "title": "Screenshot.png",
            "extensions": {"fileId": "image-1"},
            "_links": {"download": "/download/Screenshot.png"},
        },
        {
            "title": "notes.pdf",
            "extensions": {"fileId": "file-1"},
            "_links": {"download": "/download/notes.pdf"},
        },
    ]
    downloads = {
        "/download/order-flow.drawio": b"drawio-bytes",
        "/download/order-flow.source.mmd": "flowchart TD; A-->B;\n",
        "/download/Screenshot.png": b"png-bytes",
        "/download/notes.pdf": b"pdf-bytes",
    }
    confluence = _confluence_stub(attachments, downloads)

    monkeypatch.setattr(
        "assemble_page.convert_adf_to_markdown",
        lambda body: (
            '<!-- adf:diagram drawio="order-flow.drawio" -->\n\n'
            '<!-- adf:attachment media-id="image-1" alt="Screenshot.png" -->\n\n'
            '<!-- adf:attachment media-id="file-1" alt="" -->'
        ),
    )

    assets_dir = tmp_path / "page.md.tmp"
    result = assemble("Diagrams Page", _drawio_body(), "123", confluence, str(assets_dir))

    assert "```mermaid\nflowchart TD; A-->B;\n```" in result
    assert "![Screenshot.png](page.md.tmp/Screenshot.png)" in result
    assert "[notes.pdf](page.md.tmp/notes.pdf)" in result
    assert (assets_dir / "order-flow.drawio").read_bytes() == b"drawio-bytes"
    assert (assets_dir / "Screenshot.png").read_bytes() == b"png-bytes"
    assert (assets_dir / "notes.pdf").read_bytes() == b"pdf-bytes"
    confluence.get_attachments_from_content.assert_called_once()


def test_assemble_skip_mode_makes_no_attachment_calls(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "assemble_page.convert_adf_to_markdown",
        lambda body: '<!-- adf:diagram drawio="order-flow.drawio" -->',
    )
    confluence = MagicMock()

    assets_dir = tmp_path / "page.md.tmp"
    result = assemble("Complex Page", _drawio_body(), "123", confluence, str(assets_dir), attachments="skip")

    assert "skipped" in result
    assert "```mermaid" not in result
    confluence.get_attachments_from_content.assert_not_called()
    assert not assets_dir.exists()


def test_assemble_auto_mode_degrades_safely_on_attachment_retrieval_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "assemble_page.convert_adf_to_markdown",
        lambda body: '<!-- adf:diagram drawio="order-flow.drawio" -->',
    )

    def fake_fetch_snapshot(confluence, page_id):
        raise AttachmentRetrievalError("SSLError")

    monkeypatch.setattr("assemble_page.fetch_attachment_snapshot", fake_fetch_snapshot)

    assets_dir = tmp_path / "page.md.tmp"
    result = assemble("Complex Page", _drawio_body(), "123", MagicMock(), str(assets_dir))

    assert "SSLError" in result
    assert "```mermaid" not in result
    assert not assets_dir.exists()
    assert "https://" not in result
    assert "# Complex Page" in result


def test_assemble_required_mode_propagates_attachment_retrieval_failure_and_writes_nothing(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(
        "assemble_page.convert_adf_to_markdown",
        lambda body: '<!-- adf:diagram drawio="order-flow.drawio" -->',
    )

    def fake_fetch_snapshot(confluence, page_id):
        raise AttachmentRetrievalError("ConnectTimeout")

    monkeypatch.setattr("assemble_page.fetch_attachment_snapshot", fake_fetch_snapshot)

    assets_dir = tmp_path / "page.md.tmp"

    with pytest.raises(AttachmentRetrievalError):
        assemble("Complex Page", _drawio_body(), "123", MagicMock(), str(assets_dir), attachments="required")

    assert not assets_dir.exists()


def test_assemble_required_mode_raises_when_attachment_placeholder_cannot_be_resolved(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(
        "assemble_page.convert_adf_to_markdown",
        lambda body: '<!-- adf:attachment media-id="missing" alt="missing.png" -->',
    )
    monkeypatch.setattr("assemble_page.fetch_attachment_snapshot", lambda confluence, page_id: MagicMock())
    monkeypatch.setattr("assemble_page.publish_attachment_cache", lambda snapshot, assets_dir: None)
    monkeypatch.setattr(
        "assemble_page.restore_diagrams",
        lambda markdown, snapshot, assets_dir_name: (
            '<!-- adf:diagram source unavailable: attachment for media-id="missing" not found -->'
        ),
    )

    body = {
        "type": "doc",
        "version": 1,
        "content": [{"type": "media", "attrs": {"id": "missing", "type": "file"}}],
    }

    with pytest.raises(AttachmentRetrievalError, match="unresolved attachment reference"):
        assemble("Complex Page", body, "123", MagicMock(), str(tmp_path / "page.md.tmp"), attachments="required")
