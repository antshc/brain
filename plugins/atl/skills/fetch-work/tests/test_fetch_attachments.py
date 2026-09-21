from unittest.mock import MagicMock

from fetch_attachments import (
    NO_TOKEN_NOTE,
    _relative_link,
    download_attachment_bytes,
    fetch_description_adf,
    find_attachment_reference_nodes,
    has_attachment_placeholder,
    has_attachment_reference,
    list_attachments,
    replace_blob_image_refs_without_credentials,
    restore_attachments,
    restore_attachments_without_credentials,
    save_attachments,
)


def _jira(attachments=None, downloads=None, description=None):
    """A stub Jira client: `attachments` is the `fields.attachment` list, `downloads` maps a
    `content` download URL to the raw bytes/text `get(..., not_json_response=True)` returns,
    `description` is the ADF `fields.description` body.
    """
    downloads = downloads or {}

    def get(path, **kwargs):
        params = kwargs.get("params")
        if params == {"fields": "attachment"}:
            return {"fields": {"attachment": attachments or []}}
        if params == {"fields": "description"}:
            return {"fields": {"description": description}}
        return downloads[path]

    jira = MagicMock()
    jira.get.side_effect = get
    return jira


def test_has_attachment_placeholder_detects_marker():
    assert has_attachment_placeholder('<!-- adf:attachment media-id="file-1" alt="" -->')
    assert not has_attachment_placeholder("plain text, no attachments")


def test_find_attachment_reference_nodes_detects_generic_file_media():
    body = {
        "type": "doc",
        "content": [
            {"type": "mediaGroup", "content": [{"type": "media", "attrs": {"id": "f1", "type": "file"}}]}
        ],
    }
    nodes = find_attachment_reference_nodes(body)
    assert len(nodes) == 1
    assert nodes[0]["attrs"]["id"] == "f1"


def test_find_attachment_reference_nodes_detects_image_media_by_alt_extension():
    body = {
        "type": "doc",
        "content": [
            {
                "type": "mediaSingle",
                "content": [
                    {"type": "media", "attrs": {"id": "f2", "alt": "image-20260827-132403.png"}}
                ],
            }
        ],
    }
    nodes = find_attachment_reference_nodes(body)
    assert len(nodes) == 1
    assert nodes[0]["attrs"]["id"] == "f2"


def test_find_attachment_reference_nodes_ignores_a_plain_doc():
    body = {
        "type": "doc",
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "no attachments here"}]},
        ],
    }
    assert find_attachment_reference_nodes(body) == []


def test_has_attachment_reference_true_and_false():
    assert has_attachment_reference({"type": "doc", "content": []}) is False
    matching = {
        "type": "doc",
        "content": [{"type": "media", "attrs": {"id": "f1", "type": "file"}}],
    }
    assert has_attachment_reference(matching) is True


def test_fetch_description_adf_calls_rest_v3_with_description_field():
    adf = {"type": "doc", "version": 1, "content": []}
    jira = _jira(description=adf)

    result = fetch_description_adf(jira, "ZIC-5881")

    assert result == adf
    jira.get.assert_called_once_with("rest/api/3/issue/ZIC-5881", params={"fields": "description"})


def test_list_attachments_calls_rest_v3_with_attachment_field():
    attachments = [{"filename": "a.png"}]
    jira = _jira(attachments=attachments)

    result = list_attachments(jira, "ZIC-5881")

    assert result == attachments
    jira.get.assert_called_once_with("rest/api/3/issue/ZIC-5881", params={"fields": "attachment"})


def test_download_attachment_bytes_encodes_str_responses():
    jira = MagicMock()
    jira.get.return_value = "text content"
    attachment = {"id": "1", "content": "https://x/rest/api/3/attachment/content/1"}
    assert download_attachment_bytes(jira, attachment) == b"text content"


def test_download_attachment_bytes_returns_bytes_unchanged():
    jira = MagicMock()
    jira.get.return_value = b"\x89PNG"
    attachment = {"id": "1", "content": "https://x/rest/api/3/attachment/content/1"}
    assert download_attachment_bytes(jira, attachment) == b"\x89PNG"


def test_download_attachment_bytes_uses_a_relative_path_built_from_the_attachment_id():
    """Never follows `attachment["content"]` verbatim — that's an absolute URL, and
    `atlassian-python-api`'s `.get()` always prepends the configured site, doubling the host.
    """
    jira = MagicMock()
    jira.get.return_value = b"png-bytes"
    attachment = {"id": "148451", "content": "https://zerto.atlassian.net/rest/api/3/attachment/content/148451"}

    download_attachment_bytes(jira, attachment)

    jira.get.assert_called_once_with("rest/api/3/attachment/content/148451", not_json_response=True)


def test_save_attachments_writes_every_attachment_and_returns_bytes_map(tmp_path):
    attachments = [
        {"filename": "a.png", "id": "1"},
        {"filename": "b.txt", "id": "2"},
    ]
    downloads = {
        "rest/api/3/attachment/content/1": b"png-bytes",
        "rest/api/3/attachment/content/2": "text",
    }
    jira = _jira(attachments=attachments, downloads=downloads)
    assets_dir = tmp_path / "work.md.tmp"

    result = save_attachments(jira, "ZIC-5881", str(assets_dir))

    assert result == {"a.png": b"png-bytes", "b.txt": b"text"}
    assert (assets_dir / "a.png").read_bytes() == b"png-bytes"
    assert (assets_dir / "b.txt").read_bytes() == b"text"


def test_save_attachments_skips_mkdir_when_attachment_list_is_empty(tmp_path):
    jira = _jira(attachments=[])
    assets_dir = tmp_path / "work.md.tmp"

    result = save_attachments(jira, "ZIC-5881", str(assets_dir))

    assert result == {}
    assert not assets_dir.exists()


def test_relative_link_percent_encodes_spaces():
    assert _relative_link("work.md.tmp", "Screenshot 1.png") == "work.md.tmp/Screenshot%201.png"


def test_restore_attachments_returns_markdown_unchanged_when_no_placeholder():
    jira = MagicMock()
    md = "# Title\n\nNo attachments here.\n"
    assert restore_attachments(jira, "ZIC-5881", md, {}, "work.md.tmp") == md
    jira.get.assert_not_called()


def test_restore_attachments_resolves_image_attachment_from_downloaded_map_without_rest_call():
    jira = MagicMock()
    downloaded = {"image-20260827-132403.png": b"png-bytes"}

    md = '<!-- adf:attachment media-id="a21ae9fb-..." alt="image-20260827-132403.png" -->'
    result = restore_attachments(jira, "ZIC-5881", md, downloaded, "work.md.tmp")

    assert result == "![image-20260827-132403.png](work.md.tmp/image-20260827-132403.png)"
    jira.get.assert_not_called()


def test_restore_attachments_resolves_generic_file_attachment_to_plain_link():
    jira = MagicMock()
    downloaded = {"notes.pdf": b"pdf-bytes"}

    md = '<!-- adf:attachment media-id="file-1" alt="notes.pdf" -->'
    result = restore_attachments(jira, "ZIC-5881", md, downloaded, "work.md.tmp")

    assert result == "[notes.pdf](work.md.tmp/notes.pdf)"


def test_restore_attachments_falls_back_to_rest_lookup_when_filename_not_in_downloaded():
    attachments = [{"filename": "image-20260827-132403.png", "id": "148455"}]
    downloads = {"rest/api/3/attachment/content/148455": b"png-bytes"}
    jira = _jira(attachments=attachments, downloads=downloads)

    md = '<!-- adf:attachment media-id="a21ae9fb-..." alt="image-20260827-132403.png" -->'
    result = restore_attachments(jira, "ZIC-5881", md, {}, "work.md.tmp")

    assert result == "![image-20260827-132403.png](work.md.tmp/image-20260827-132403.png)"


def test_restore_attachments_notes_when_filename_has_no_matching_attachment():
    jira = _jira(attachments=[])

    md = '<!-- adf:attachment media-id="unknown" alt="missing.png" -->'
    result = restore_attachments(jira, "ZIC-5881", md, {}, "work.md.tmp")

    assert "missing.png" in result
    assert "adf:attachment source unavailable" in result


def test_restore_attachments_notes_when_placeholder_alt_is_empty():
    jira = MagicMock()

    md = '<!-- adf:attachment media-id="unknown" alt="" -->'
    result = restore_attachments(jira, "ZIC-5881", md, {}, "work.md.tmp")

    assert "no filename" in result
    jira.get.assert_not_called()


def test_restore_attachments_percent_encodes_spaces_in_the_relative_link():
    jira = MagicMock()
    downloaded = {"Screenshot 2026-02-10 113535.png": b"png-bytes"}

    md = '<!-- adf:attachment media-id="image-1" alt="Screenshot 2026-02-10 113535.png" -->'
    result = restore_attachments(jira, "ZIC-5881", md, downloaded, "work.md.tmp")

    assert result == (
        "![Screenshot 2026-02-10 113535.png](work.md.tmp/Screenshot%202026-02-10%20113535.png)"
    )


def test_restore_attachments_resolves_image_attachment_with_size_to_an_image_plus_media_size_comment():
    jira = MagicMock()
    downloaded = {"image-20260827-132403.png": b"png-bytes"}

    md = (
        '<!-- adf:attachment media-id="image-1" alt="image-20260827-132403.png" '
        'width="628" height="256" -->'
    )
    result = restore_attachments(jira, "ZIC-5881", md, downloaded, "work.md.tmp")

    assert result == (
        "![image-20260827-132403.png](work.md.tmp/image-20260827-132403.png)\n"
        "<!-- media-size: width=628 height=256 -->"
    )


def test_restore_attachments_without_credentials_replaces_every_placeholder_with_a_note():
    md = (
        '<!-- adf:attachment media-id="file-1" alt="a.png" -->\n\n'
        '<!-- adf:attachment media-id="file-2" alt="b.png" -->'
    )
    result = restore_attachments_without_credentials(md)

    assert result.count("ATLASSIAN_API_TOKEN") == 2
    assert NO_TOKEN_NOTE in result


def test_restore_attachments_without_credentials_leaves_plain_markdown_untouched():
    md = "# Title\n\nJust text.\n"
    assert restore_attachments_without_credentials(md) == md


def test_replace_blob_image_refs_without_credentials_swaps_blob_markers_for_the_note():
    md = (
        "before\n\n![](blob:https://media.staging.atl-paas.net/?type=file&id=abc)\n\nafter\n\n"
        "![](blob:https://media.staging.atl-paas.net/?type=file&id=def)"
    )
    result = replace_blob_image_refs_without_credentials(md)

    assert result.count(NO_TOKEN_NOTE) == 2
    assert "blob:" not in result


def test_replace_blob_image_refs_without_credentials_leaves_plain_markdown_untouched():
    md = "# Title\n\nJust text, no embedded images.\n"
    assert replace_blob_image_refs_without_credentials(md) == md
