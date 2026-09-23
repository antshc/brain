"""CLI-level tests for `--md-path`/`--assets-dir` wiring, invoked as a real subprocess
(mirroring `/map-markdown-adf`'s `run_cli` fixture pattern)."""
import json
import subprocess
import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "assemble_page.py"


def _run(args: list[str], stdin_text: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_SCRIPT), *args],
        input=stdin_text,
        capture_output=True,
        text=True,
    )


def _raw(title: str, body: dict) -> str:
    return json.dumps({"content": {"nodes": [{"title": title, "body": body}]}})


def test_main_writes_markdown_to_md_path_with_default_assets_dir(tmp_path):
    md_path = tmp_path / "page.md"
    raw = _raw("Simple Page", {"type": "doc", "version": 1, "content": []})

    result = _run(["--page-id", "123", "--root", str(tmp_path), "--md-path", str(md_path)], raw)

    assert result.returncode == 0, result.stderr
    assert md_path.read_text() == "# Simple Page\n\n\n"
    # a page with no attachment reference never creates the default assets folder
    assert not (tmp_path / "page.md.assets").exists()


def test_main_accepts_an_explicit_assets_dir_override(tmp_path):
    md_path = tmp_path / "page.md"
    assets_dir = tmp_path / "custom-assets"
    raw = _raw("Simple Page", {"type": "doc", "version": 1, "content": []})

    result = _run(
        [
            "--page-id",
            "123",
            "--root",
            str(tmp_path),
            "--md-path",
            str(md_path),
            "--assets-dir",
            str(assets_dir),
        ],
        raw,
    )

    assert result.returncode == 0, result.stderr
    assert md_path.read_text() == "# Simple Page\n\n\n"
    assert not assets_dir.exists()


def test_main_reports_a_sanitized_conversion_failure_without_a_traceback_and_writes_nothing(tmp_path):
    md_path = tmp_path / "page.md"
    body = {"type": "doc", "version": 1, "content": [{"type": "totallyUnknownNode"}]}
    raw = _raw("Broken Page", body)

    result = _run(["--page-id", "123", "--root", str(tmp_path), "--md-path", str(md_path)], raw)

    assert result.returncode != 0
    assert "ADF conversion failed:" in result.stderr
    assert "totallyUnknownNode" in result.stderr
    assert "Traceback" not in result.stderr
    assert not md_path.exists()


def _attachment_reference_body() -> dict:
    return {
        "type": "doc",
        "version": 1,
        "content": [{"type": "extension", "attrs": {"extensionKey": "app/env/static/drawio"}}],
    }


def test_main_attachments_skip_makes_no_credential_or_rest_calls(tmp_path):
    md_path = tmp_path / "page.md"
    raw = _raw("Diagram Page", _attachment_reference_body())

    result = _run(
        ["--page-id", "123", "--root", str(tmp_path), "--md-path", str(md_path), "--attachments", "skip"],
        raw,
    )

    assert result.returncode == 0, result.stderr
    assert "skipped" in md_path.read_text()
    assert not (tmp_path / "page.md.assets").exists()


def test_main_attachments_required_fails_without_writing_when_credentials_are_missing(tmp_path):
    md_path = tmp_path / "page.md"
    raw = _raw("Diagram Page", _attachment_reference_body())

    result = _run(
        [
            "--page-id",
            "123",
            "--root",
            str(tmp_path),
            "--md-path",
            str(md_path),
            "--attachments",
            "required",
        ],
        raw,
    )

    assert result.returncode != 0
    assert "Attachment retrieval failed:" in result.stderr
    assert "Traceback" not in result.stderr
    assert not md_path.exists()
    assert not (tmp_path / "page.md.assets").exists()


def test_main_attachments_auto_default_degrades_with_a_missing_credential_note(tmp_path):
    md_path = tmp_path / "page.md"
    raw = _raw("Diagram Page", _attachment_reference_body())

    result = _run(["--page-id", "123", "--root", str(tmp_path), "--md-path", str(md_path)], raw)

    assert result.returncode == 0, result.stderr
    assert "ATLASSIAN_API_TOKEN" in md_path.read_text()
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


def test_main_converts_the_synthetic_cross_skill_fixture_with_no_preprocessing(tmp_path):
    """Runs the real CLI end to end on a fixture shaped like the page that originally failed —
    no `jq` or other ADF preprocessing needed.
    """
    md_path = tmp_path / "page.md"
    raw = _raw("ZIC Monitoring GUI Alerts + Tasks", _synthetic_fixture_body())

    result = _run(
        ["--page-id", "123", "--root", str(tmp_path), "--md-path", str(md_path), "--attachments", "skip"],
        raw,
    )

    assert result.returncode == 0, result.stderr
    markdown = md_path.read_text()
    assert "<!-- adf:toc -->" in markdown
    assert "[https://example.atlassian.net/wiki/x/AbCdE](https://example.atlassian.net/wiki/x/AbCdE)" in markdown
    assert "- task one" in markdown
    assert "| Env | Status |" in markdown
    assert "skipped" in markdown
    assert not (tmp_path / "page.md.assets").exists()
