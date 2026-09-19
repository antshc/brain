import json
from unittest.mock import MagicMock

from assemble_page import assemble, convert_adf_to_markdown, extract_title_and_body


def _raw(title: str, body: dict) -> dict:
    return {"content": {"nodes": [{"title": title, "body": body}]}}


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


def test_extract_title_and_body_reads_the_documented_json_path():
    body = {"type": "doc", "version": 1, "content": []}
    title, extracted_body = extract_title_and_body(_raw("Behavior Diagram", body))

    assert title == "Behavior Diagram"
    assert extracted_body == body


def test_convert_adf_to_markdown_shells_out_to_map_markdown_adf(monkeypatch):
    captured = {}

    def fake_run(cmd, input, capture_output, text, check):  # noqa: A002
        captured["cmd"] = cmd
        captured["input"] = input
        return MagicMock(stdout="# Title\n\nBody.\n")

    monkeypatch.setattr("assemble_page.subprocess.run", fake_run)

    body = {"type": "doc", "version": 1, "content": []}
    markdown = convert_adf_to_markdown(body)

    assert markdown == "# Title\n\nBody.\n"
    assert captured["cmd"][-1] == "adf-to-md"
    assert json.loads(captured["input"]) == body


def test_assemble_skips_attachment_handling_for_a_page_with_no_references(monkeypatch, tmp_path):
    monkeypatch.setattr("assemble_page.convert_adf_to_markdown", lambda body: "Presentation text.\n")
    load_credentials = MagicMock()
    monkeypatch.setattr("assemble_page.load_credentials", load_credentials)

    raw = _raw("Simple Page", {"type": "doc", "version": 1, "content": []})
    assets_dir = tmp_path / "page.md.tmp"
    result = assemble(raw, "123", "/repo", str(assets_dir))

    assert result == "# Simple Page\n\nPresentation text.\n"
    load_credentials.assert_not_called()
    assert not assets_dir.exists()


def test_assemble_saves_attachments_and_restores_diagrams_when_reference_present_and_token_available(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(
        "assemble_page.convert_adf_to_markdown",
        lambda body: '<!-- adf:diagram drawio="order-flow.drawio" -->',
    )
    monkeypatch.setattr(
        "assemble_page.load_credentials", lambda root: {"site": "x", "email": "e", "token": "t"}
    )
    confluence = MagicMock()
    monkeypatch.setattr("assemble_page.get_confluence", lambda credentials: confluence)
    save_attachments = MagicMock(return_value={"order-flow.source.mmd": "flowchart TD; A-->B;\n"})
    monkeypatch.setattr("assemble_page.save_attachments", save_attachments)
    monkeypatch.setattr(
        "assemble_page.restore_diagrams",
        lambda confluence_, page_id, markdown, downloaded, assets_dir_name: "```mermaid\nflowchart TD; A-->B;\n```",
    )

    raw = _raw("Complex Page", _drawio_body())
    assets_dir = tmp_path / "page.md.tmp"
    result = assemble(raw, "123", "/repo", str(assets_dir))

    assert result == "# Complex Page\n\n```mermaid\nflowchart TD; A-->B;\n```"
    save_attachments.assert_called_once_with(confluence, "123", str(assets_dir))


def test_assemble_does_not_duplicate_a_title_the_body_already_carries_as_h1(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "assemble_page.convert_adf_to_markdown",
        lambda body: "# Behavior Diagram\n\nPresentation text.\n",
    )

    raw = _raw("Behavior Diagram", {"type": "doc", "version": 1, "content": []})
    result = assemble(raw, "123", "/repo", str(tmp_path / "page.md.tmp"))

    assert result == "# Behavior Diagram\n\nPresentation text.\n"


def test_assemble_degrades_when_reference_present_and_no_token(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "assemble_page.convert_adf_to_markdown",
        lambda body: '<!-- adf:diagram drawio="order-flow.drawio" -->',
    )
    monkeypatch.setattr("assemble_page.load_credentials", lambda root: None)

    raw = _raw("Complex Page", _drawio_body())
    assets_dir = tmp_path / "page.md.tmp"
    result = assemble(raw, "123", "/repo", str(assets_dir))

    assert "ATLASSIAN_API_TOKEN" in result
    assert "```mermaid" not in result
    assert not assets_dir.exists()


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
    monkeypatch.setattr(
        "assemble_page.load_credentials", lambda root: {"site": "x", "email": "e", "token": "t"}
    )
    monkeypatch.setattr("assemble_page.get_confluence", lambda credentials: confluence)

    raw = _raw("Diagrams Page", _drawio_body())
    assets_dir = tmp_path / "page.md.tmp"
    result = assemble(raw, "123", "/repo", str(assets_dir))

    assert "```mermaid\nflowchart TD; A-->B;\n```" in result
    assert "![Screenshot.png](page.md.tmp/Screenshot.png)" in result
    assert "[notes.pdf](page.md.tmp/notes.pdf)" in result
    assert (assets_dir / "order-flow.drawio").read_bytes() == b"drawio-bytes"
    assert (assets_dir / "Screenshot.png").read_bytes() == b"png-bytes"
    assert (assets_dir / "notes.pdf").read_bytes() == b"pdf-bytes"
