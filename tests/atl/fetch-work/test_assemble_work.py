import json
from unittest.mock import MagicMock

from assemble_work import assemble, convert_adf_to_markdown, format_header


def _fields(**overrides) -> dict:
    fields = {
        "summary": "Case Number Input Mask - Swagger and GUI are not Aligned",
        "status": {"name": "New"},
        "issuetype": {"name": "Bug"},
        "assignee": {"displayName": "Anton Shcherbyna"},
        "description": {"type": "doc", "version": 1, "content": []},
    }
    fields.update(overrides)
    return fields


def _image_body() -> dict:
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "mediaSingle",
                "content": [{"type": "media", "attrs": {"id": "img-1", "alt": "shot.png"}}],
            }
        ],
    }


def test_format_header_matches_the_documented_output_shape():
    header = format_header("PROJ-5881", _fields())
    assert header == (
        "# PROJ-5881 — Case Number Input Mask - Swagger and GUI are not Aligned\n"
        "**Status:** New · **Type:** Bug · **Assignee:** Anton Shcherbyna\n\n"
    )


def test_format_header_defaults_a_null_assignee_to_unassigned():
    header = format_header("PROJ-5881", _fields(assignee=None))
    assert "**Assignee:** Unassigned" in header


def test_convert_adf_to_markdown_shells_out_to_map_markdown_adf(monkeypatch):
    captured = {}

    def fake_run(cmd, input, capture_output, text, check):  # noqa: A002
        captured["cmd"] = cmd
        captured["input"] = input
        return MagicMock(stdout="Body text.\n")

    monkeypatch.setattr("assemble_work.subprocess.run", fake_run)

    body = {"type": "doc", "version": 1, "content": []}
    markdown = convert_adf_to_markdown(body)

    assert markdown == "Body text.\n"
    assert captured["cmd"][-1] == "adf-to-md"
    assert json.loads(captured["input"]) == body


def test_assemble_returns_the_header_alone_for_an_empty_description(monkeypatch):
    convert = MagicMock()
    monkeypatch.setattr("assemble_work.convert_adf_to_markdown", convert)

    result = assemble("PROJ-5881", _fields(description=None), MagicMock(), "/repo/work.md.tmp")

    assert result.endswith("**Assignee:** Anton Shcherbyna\n\n")
    convert.assert_not_called()


def test_assemble_converts_real_adf_and_resolves_attachments(monkeypatch, tmp_path):
    jira = MagicMock()
    monkeypatch.setattr(
        "assemble_work.convert_adf_to_markdown",
        lambda body: '<!-- adf:attachment media-id="img-1" alt="shot.png" -->',
    )
    save_attachments = MagicMock(return_value={"shot.png": b"png-bytes"})
    monkeypatch.setattr("assemble_work.save_attachments", save_attachments)
    monkeypatch.setattr(
        "assemble_work.restore_attachments",
        lambda jira_, key, markdown, downloaded, assets_dir_name: "![shot.png](work.md.tmp/shot.png)",
    )

    assets_dir = tmp_path / "work.md.tmp"
    result = assemble("PROJ-5881", _fields(description=_image_body()), jira, str(assets_dir))

    assert result == (
        "# PROJ-5881 — Case Number Input Mask - Swagger and GUI are not Aligned\n"
        "**Status:** New · **Type:** Bug · **Assignee:** Anton Shcherbyna\n\n"
        "![shot.png](work.md.tmp/shot.png)"
    )
    save_attachments.assert_called_once_with(jira, "PROJ-5881", str(assets_dir))


def test_assemble_skips_attachment_handling_when_no_reference_present(monkeypatch, tmp_path):
    monkeypatch.setattr("assemble_work.convert_adf_to_markdown", lambda body: "Plain text body.\n")
    save_attachments = MagicMock()
    monkeypatch.setattr("assemble_work.save_attachments", save_attachments)

    assets_dir = tmp_path / "work.md.tmp"
    result = assemble("PROJ-5881", _fields(), MagicMock(), str(assets_dir))

    assert result.endswith("Plain text body.\n")
    save_attachments.assert_not_called()
    assert not assets_dir.exists()
