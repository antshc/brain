import json
from unittest.mock import MagicMock

from assemble_page import assemble, convert_adf_to_markdown, extract_title_and_body


def _raw(title: str, body: dict) -> dict:
    return {"content": {"nodes": [{"title": title, "body": body}]}}


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


def test_assemble_skips_diagram_restore_for_a_simple_page(monkeypatch):
    monkeypatch.setattr("assemble_page.convert_adf_to_markdown", lambda body: "Presentation text.\n")
    load_credentials = MagicMock()
    monkeypatch.setattr("assemble_page.load_credentials", load_credentials)

    raw = _raw("Simple Page", {"type": "doc", "version": 1, "content": []})
    result = assemble(raw, "123", "/repo")

    assert result == "# Simple Page\n\nPresentation text.\n"
    load_credentials.assert_not_called()


def test_assemble_restores_diagrams_when_placeholder_present_and_token_available(monkeypatch):
    monkeypatch.setattr(
        "assemble_page.convert_adf_to_markdown",
        lambda body: '<!-- adf:diagram drawio="order-flow.drawio" -->',
    )
    monkeypatch.setattr(
        "assemble_page.load_credentials", lambda root: {"site": "x", "email": "e", "token": "t"}
    )
    monkeypatch.setattr("assemble_page.get_confluence", lambda credentials: MagicMock())
    monkeypatch.setattr(
        "assemble_page.restore_diagrams",
        lambda confluence, page_id, markdown: "```mermaid\nflowchart TD; A-->B;\n```",
    )

    raw = _raw("Complex Page", {"type": "doc", "version": 1, "content": []})
    result = assemble(raw, "123", "/repo")

    assert result == "# Complex Page\n\n```mermaid\nflowchart TD; A-->B;\n```"


def test_assemble_does_not_duplicate_a_title_the_body_already_carries_as_h1(monkeypatch):
    monkeypatch.setattr(
        "assemble_page.convert_adf_to_markdown",
        lambda body: "# Behavior Diagram\n\nPresentation text.\n",
    )

    raw = _raw("Behavior Diagram", {"type": "doc", "version": 1, "content": []})
    result = assemble(raw, "123", "/repo")

    assert result == "# Behavior Diagram\n\nPresentation text.\n"


def test_assemble_degrades_when_placeholder_present_and_no_token(monkeypatch):
    monkeypatch.setattr(
        "assemble_page.convert_adf_to_markdown",
        lambda body: '<!-- adf:diagram drawio="order-flow.drawio" -->',
    )
    monkeypatch.setattr("assemble_page.load_credentials", lambda root: None)

    raw = _raw("Complex Page", {"type": "doc", "version": 1, "content": []})
    result = assemble(raw, "123", "/repo")

    assert "ATLASSIAN_API_TOKEN" in result
    assert "```mermaid" not in result
