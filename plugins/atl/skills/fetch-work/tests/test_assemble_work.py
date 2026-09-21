import json
from unittest.mock import MagicMock

from assemble_work import assemble, convert_adf_to_markdown, extract_fields, format_header


def _raw(key: str, fields: dict) -> dict:
    return {"issues": {"nodes": [{"key": key, "fields": fields}]}}


def _fields(**overrides) -> dict:
    fields = {
        "summary": "Case Number Input Mask - Swagger and GUI are not Aligned",
        "status": {"name": "New"},
        "issuetype": {"name": "Bug"},
        "assignee": {"displayName": "Anton Shcherbyna"},
        "description": "plain description text",
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


def test_extract_fields_reads_the_documented_json_path():
    fields = _fields()
    assert extract_fields(_raw("ZIC-5881", fields)) == fields


def test_format_header_matches_the_documented_output_shape():
    header = format_header("ZIC-5881", _fields())
    assert header == (
        "# ZIC-5881 — Case Number Input Mask - Swagger and GUI are not Aligned\n"
        "**Status:** New · **Type:** Bug · **Assignee:** Anton Shcherbyna\n\n"
    )


def test_format_header_defaults_a_null_assignee_to_unassigned():
    header = format_header("ZIC-5881", _fields(assignee=None))
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


def test_assemble_uses_the_mcp_description_directly_and_notes_blob_images_without_credentials(
    monkeypatch,
):
    monkeypatch.setattr("assemble_work.load_credentials", lambda root: None)

    fields = _fields(
        description="text\n\n![](blob:https://media.staging.atl-paas.net/?type=file&id=abc)"
    )
    result = assemble(_raw("ZIC-5881", fields), "ZIC-5881", "/repo", "/repo/work.md.tmp")

    assert result.startswith("# ZIC-5881 — ")
    assert "ATLASSIAN_API_TOKEN" in result
    assert "blob:" not in result


def test_assemble_fetches_real_adf_and_resolves_attachments_when_token_available(monkeypatch, tmp_path):
    jira = MagicMock()
    monkeypatch.setattr("assemble_work.load_credentials", lambda root: {"site": "x", "email": "e", "token": "t"})
    monkeypatch.setattr("assemble_work.get_jira", lambda credentials: jira)
    monkeypatch.setattr("assemble_work.fetch_description_adf", lambda jira_, key: _image_body())
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

    fields = _fields()
    assets_dir = tmp_path / "work.md.tmp"
    result = assemble(_raw("ZIC-5881", fields), "ZIC-5881", "/repo", str(assets_dir))

    assert result == (
        "# ZIC-5881 — Case Number Input Mask - Swagger and GUI are not Aligned\n"
        "**Status:** New · **Type:** Bug · **Assignee:** Anton Shcherbyna\n\n"
        "![shot.png](work.md.tmp/shot.png)"
    )
    save_attachments.assert_called_once_with(jira, "ZIC-5881", str(assets_dir))


def test_assemble_skips_attachment_handling_when_token_available_but_no_reference_present(
    monkeypatch, tmp_path
):
    monkeypatch.setattr("assemble_work.load_credentials", lambda root: {"site": "x", "email": "e", "token": "t"})
    monkeypatch.setattr("assemble_work.get_jira", lambda credentials: MagicMock())
    monkeypatch.setattr(
        "assemble_work.fetch_description_adf",
        lambda jira_, key: {"type": "doc", "version": 1, "content": []},
    )
    monkeypatch.setattr("assemble_work.convert_adf_to_markdown", lambda body: "Plain text body.\n")
    save_attachments = MagicMock()
    monkeypatch.setattr("assemble_work.save_attachments", save_attachments)

    assets_dir = tmp_path / "work.md.tmp"
    result = assemble(_raw("ZIC-5881", _fields()), "ZIC-5881", "/repo", str(assets_dir))

    assert result.endswith("Plain text body.\n")
    save_attachments.assert_not_called()
    assert not assets_dir.exists()
