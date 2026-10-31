"""CLI-level tests for `main()`: argument wiring, credential gate, and error framing. The REST
client is stubbed; ADF->Markdown still runs `/map-markdown-adf`'s real CLI."""
import json
from unittest.mock import MagicMock

import pytest

import assemble_page

CREDENTIALS = {"site": "https://s.example", "email": "e", "token": "t"}


def _page(title: str, body: dict) -> dict:
    return {"title": title, "body": {"atlas_doc_format": {"value": json.dumps(body)}}}


@pytest.fixture
def confluence(monkeypatch):
    client = MagicMock()
    client.get.return_value = _page("Simple Page", {"type": "doc", "version": 1, "content": []})
    monkeypatch.setattr(assemble_page, "load_credentials", lambda config_path: CREDENTIALS)
    monkeypatch.setattr(assemble_page, "get_confluence", lambda credentials: client)
    return client


def _main(tmp_path, *extra: str) -> None:
    assemble_page.main(
        ["--page-id", "123", "--config", str(tmp_path / "cfg"), "--md-path", str(tmp_path / "page.md"), "--comments", "skip", *extra]
    )


def test_main_writes_markdown_to_md_path_with_default_assets_dir(confluence, tmp_path):
    _main(tmp_path)

    assert (tmp_path / "page.md").read_text() == "# Simple Page\n\n\n"
    assert not (tmp_path / "page.md.assets").exists()
    confluence.get.assert_called_once_with("/api/v2/pages/123", params={"body-format": "atlas_doc_format"})


def test_main_accepts_an_explicit_assets_dir_override(confluence, tmp_path):
    assets_dir = tmp_path / "custom-assets"

    _main(tmp_path, "--assets-dir", str(assets_dir))

    assert (tmp_path / "page.md").read_text() == "# Simple Page\n\n\n"
    assert not assets_dir.exists()


def test_main_site_overrides_the_configured_site(monkeypatch, tmp_path):
    seen = {}
    client = MagicMock()
    client.get.return_value = _page("Simple Page", {"type": "doc", "version": 1, "content": []})
    monkeypatch.setattr(assemble_page, "load_credentials", lambda config_path: CREDENTIALS)
    monkeypatch.setattr(assemble_page, "get_confluence", lambda credentials: seen.setdefault("c", credentials) and client)

    _main(tmp_path, "--site", "https://other.example")

    assert seen["c"]["site"] == "https://other.example"


def test_main_fails_naming_credentials_when_config_is_incomplete(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(assemble_page, "load_credentials", lambda config_path: None)

    with pytest.raises(SystemExit):
        _main(tmp_path)

    assert "apiToken" in capsys.readouterr().err
    assert not (tmp_path / "page.md").exists()


def test_main_reports_a_safe_fetch_failure_and_writes_nothing(confluence, tmp_path, capsys):
    from requests.exceptions import ConnectionError as RequestsConnectionError

    confluence.get.side_effect = RequestsConnectionError("https://secret.example/?token=abc")

    with pytest.raises(SystemExit):
        _main(tmp_path)

    err = capsys.readouterr().err
    assert "Page fetch failed: ConnectionError" in err
    assert "secret" not in err
    assert not (tmp_path / "page.md").exists()


def test_main_reports_a_sanitized_conversion_failure_without_a_traceback_and_writes_nothing(confluence, tmp_path, capsys):
    confluence.get.return_value = _page("Broken Page", {"type": "doc", "version": 1, "content": [{"type": "totallyUnknownNode"}]})

    with pytest.raises(SystemExit):
        _main(tmp_path)

    err = capsys.readouterr().err
    assert "ADF conversion failed:" in err
    assert "totallyUnknownNode" in err
    assert "Traceback" not in err
    assert not (tmp_path / "page.md").exists()


def _attachment_reference_body() -> dict:
    return {
        "type": "doc",
        "version": 1,
        "content": [{"type": "extension", "attrs": {"extensionKey": "app/env/static/drawio"}}],
    }


def test_main_attachments_skip_makes_no_attachment_calls(confluence, tmp_path):
    confluence.get.return_value = _page("Diagram Page", _attachment_reference_body())

    _main(tmp_path, "--attachments", "skip")

    assert "skipped" in (tmp_path / "page.md").read_text()
    assert not (tmp_path / "page.md.assets").exists()
    confluence.get_attachments_from_content.assert_not_called()


def test_main_attachments_required_fails_without_writing_when_retrieval_fails(confluence, tmp_path, capsys):
    from requests.exceptions import SSLError

    confluence.get.return_value = _page("Diagram Page", _attachment_reference_body())
    confluence.get_attachments_from_content.side_effect = SSLError("boom")

    with pytest.raises(SystemExit):
        _main(tmp_path, "--attachments", "required")

    err = capsys.readouterr().err
    assert "Attachment retrieval failed:" in err
    assert "Traceback" not in err
    assert not (tmp_path / "page.md").exists()
    assert not (tmp_path / "page.md.assets").exists()


def _synthetic_fixture_body() -> dict:
    """A synthetic fixture covering the real Confluence shapes this hardening effort targets —
    expand+TOC, inline smart-card links, lists, tables, and image/generic-file media — built
    only from structure, never from any private wording or URL.
    """
    toc_extension = {
        "type": "extension",
        "attrs": {
            "layout": "default",
            "extensionType": "com.atlassian.confluence.macro.core",
            "extensionKey": "toc",
            "parameters": {"macroParams": {}},
        },
    }
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "expand", "attrs": {"title": "Overview"}, "content": [toc_extension]},
            {"type": "heading", "attrs": {"level": 1}, "content": [{"type": "text", "text": "Alerts"}]},
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "See "},
                    {"type": "inlineCard", "attrs": {"url": "https://example.atlassian.net/wiki/x/AbCdE"}},
                    {"type": "text", "text": " for details."},
                ],
            },
            {
                "type": "bulletList",
                "content": [
                    {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "task one"}]}]},
                    {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "task two"}]}]},
                ],
            },
            {
                "type": "table",
                "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
                "content": [
                    {
                        "type": "tableRow",
                        "content": [
                            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Env"}]}]},
                            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Status"}]}]},
                        ],
                    },
                    {
                        "type": "tableRow",
                        "content": [
                            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "prod"}]}]},
                            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "green"}]}]},
                        ],
                    },
                ],
            },
            {
                "type": "mediaSingle",
                "attrs": {"layout": "center"},
                "content": [{"type": "media", "attrs": {"id": "image-1", "type": "file", "alt": "dashboard.png"}}],
            },
            {
                "type": "mediaGroup",
                "content": [{"type": "media", "attrs": {"id": "file-1", "type": "file", "alt": "runbook.pdf"}}],
            },
        ],
    }



def test_main_converts_the_synthetic_cross_skill_fixture_with_no_preprocessing(confluence, tmp_path):
    """Runs `main` end to end on a fixture shaped like the page that originally failed —
    no `jq` or other ADF preprocessing needed.
    """
    confluence.get.return_value = _page("PROJ Monitoring GUI Alerts + Tasks", _synthetic_fixture_body())

    _main(tmp_path, "--attachments", "skip")

    markdown = (tmp_path / "page.md").read_text()
    assert "<!-- adf:toc -->" in markdown
    assert "[https://example.atlassian.net/wiki/x/AbCdE](https://example.atlassian.net/wiki/x/AbCdE)" in markdown
    assert "- task one" in markdown
    assert "| Env | Status |" in markdown
    assert "skipped" in markdown
    assert not (tmp_path / "page.md.assets").exists()
