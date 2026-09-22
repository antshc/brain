from unittest.mock import MagicMock

import pytest
from requests.exceptions import ConnectTimeout, SSLError

from fetch_diagrams import (
    AttachmentRetrievalError,
    AttachmentSnapshot,
    _relative_link,
    download_attachment_bytes,
    fetch_attachment_snapshot,
    find_attachment_reference_nodes,
    has_attachment_reference,
    has_diagram_placeholder,
    publish_attachment_cache,
    restore_diagrams,
    restore_diagrams_failed,
    restore_diagrams_skipped,
    restore_diagrams_without_credentials,
)


def _confluence(attachments, downloads):
    """A stub Confluence client: `attachments` is the `get_attachments_from_content` result list,
    `downloads` maps a download link to the raw bytes/text `get(..., not_json_response=True)` returns.
    """
    confluence = MagicMock()
    confluence.get_attachments_from_content.return_value = {"results": attachments}
    confluence.get.side_effect = lambda link, **kwargs: downloads[link]
    return confluence


def test_has_diagram_placeholder_detects_drawio_and_attachment_markers():
    assert has_diagram_placeholder('<!-- adf:diagram drawio="x.drawio" -->')
    assert has_diagram_placeholder('<!-- adf:attachment media-id="file-1" alt="" -->')
    assert not has_diagram_placeholder("plain text, no diagrams")


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
                    {"type": "media", "attrs": {"id": "f2", "type": "file", "alt": "Screenshot.png"}}
                ],
            }
        ],
    }
    nodes = find_attachment_reference_nodes(body)
    assert len(nodes) == 1
    assert nodes[0]["attrs"]["id"] == "f2"


def test_find_attachment_reference_nodes_detects_drawio_extension_nested_in_a_table_cell():
    body = {
        "type": "doc",
        "content": [
            {
                "type": "table",
                "content": [
                    {
                        "type": "tableRow",
                        "content": [
                            {
                                "type": "tableCell",
                                "content": [
                                    {
                                        "type": "extension",
                                        "attrs": {"extensionKey": "app/env/static/drawio"},
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
    }
    nodes = find_attachment_reference_nodes(body)
    assert len(nodes) == 1
    assert nodes[0]["type"] == "extension"


def test_find_attachment_reference_nodes_ignores_a_plain_doc():
    body = {
        "type": "doc",
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "no attachments here"}]},
            {"type": "table", "content": [{"type": "tableRow", "content": []}]},
        ],
    }
    assert find_attachment_reference_nodes(body) == []


def test_has_attachment_reference_true_and_false():
    assert has_attachment_reference({"type": "doc", "content": []}) is False
    matching = {"type": "doc", "content": [{"type": "extension", "attrs": {"extensionKey": "x/static/drawio"}}]}
    assert has_attachment_reference(matching) is True


def test_download_attachment_bytes_encodes_str_responses():
    confluence = MagicMock()
    confluence.get.return_value = "text content"
    attachment = {"_links": {"download": "/download/x"}}
    assert download_attachment_bytes(confluence, attachment) == b"text content"


def test_download_attachment_bytes_returns_bytes_unchanged():
    confluence = MagicMock()
    confluence.get.return_value = b"\x89PNG"
    attachment = {"_links": {"download": "/download/x"}}
    assert download_attachment_bytes(confluence, attachment) == b"\x89PNG"


def test_fetch_attachment_snapshot_lists_and_downloads_once():
    attachments = [
        {"title": "a.png", "_links": {"download": "/download/a.png"}},
        {"title": "b.txt", "_links": {"download": "/download/b.txt"}},
    ]
    downloads = {"/download/a.png": b"png-bytes", "/download/b.txt": "text"}
    confluence = _confluence(attachments, downloads)

    snapshot = fetch_attachment_snapshot(confluence, "123")

    assert snapshot == AttachmentSnapshot(
        attachments=attachments, downloaded={"a.png": b"png-bytes", "b.txt": b"text"}
    )
    confluence.get_attachments_from_content.assert_called_once()


def test_fetch_attachment_snapshot_wraps_a_list_failure_with_only_a_safe_category():
    confluence = MagicMock()
    confluence.get_attachments_from_content.side_effect = SSLError(
        "https://media.example.atlassian.net/file?token=super-secret-signed-token"
    )

    with pytest.raises(AttachmentRetrievalError) as excinfo:
        fetch_attachment_snapshot(confluence, "123")

    assert str(excinfo.value) == "SSLError"
    assert "token" not in str(excinfo.value)
    assert "https://" not in str(excinfo.value)


def test_fetch_attachment_snapshot_wraps_a_download_failure_with_only_a_safe_category():
    attachments = [
        {"title": "first.png", "_links": {"download": "/download/first.png"}},
        {"title": "second.png", "_links": {"download": "/download/second.png"}},
    ]
    confluence = MagicMock()
    confluence.get_attachments_from_content.return_value = {"results": attachments}

    def fake_get(link, **kwargs):
        if link == "/download/first.png":
            return b"png-bytes"
        raise ConnectTimeout("https://media.example.atlassian.net/second.png?token=abc")

    confluence.get.side_effect = fake_get

    with pytest.raises(AttachmentRetrievalError) as excinfo:
        fetch_attachment_snapshot(confluence, "123")

    assert str(excinfo.value) == "ConnectTimeout"
    assert "token" not in str(excinfo.value)


def test_publish_attachment_cache_writes_every_attachment(tmp_path):
    snapshot = AttachmentSnapshot(
        attachments=[{"title": "a.png"}, {"title": "b.txt"}],
        downloaded={"a.png": b"png-bytes", "b.txt": b"text"},
    )
    assets_dir = tmp_path / "page.md.tmp"

    publish_attachment_cache(snapshot, str(assets_dir))

    assert (assets_dir / "a.png").read_bytes() == b"png-bytes"
    assert (assets_dir / "b.txt").read_bytes() == b"text"
    # no staging directory left behind after a successful publish
    assert list(tmp_path.iterdir()) == [assets_dir]


def test_publish_attachment_cache_skips_when_no_attachments(tmp_path):
    snapshot = AttachmentSnapshot(attachments=[], downloaded={})
    assets_dir = tmp_path / "page.md.tmp"

    publish_attachment_cache(snapshot, str(assets_dir))

    assert not assets_dir.exists()


def test_publish_attachment_cache_replaces_an_existing_complete_cache(tmp_path):
    assets_dir = tmp_path / "page.md.tmp"
    assets_dir.mkdir()
    (assets_dir / "old.png").write_bytes(b"old-bytes")

    snapshot = AttachmentSnapshot(attachments=[{"title": "new.png"}], downloaded={"new.png": b"new-bytes"})
    publish_attachment_cache(snapshot, str(assets_dir))

    assert (assets_dir / "new.png").read_bytes() == b"new-bytes"
    assert not (assets_dir / "old.png").exists()
    assert list(tmp_path.iterdir()) == [assets_dir]


def test_publish_attachment_cache_preserves_a_prior_complete_cache_on_publish_failure(tmp_path, monkeypatch):
    assets_dir = tmp_path / "page.md.tmp"
    assets_dir.mkdir()
    (assets_dir / "old.png").write_bytes(b"old-bytes")

    snapshot = AttachmentSnapshot(attachments=[{"title": "new.png"}], downloaded={"new.png": b"new-bytes"})

    def fake_rename(self, target):
        raise OSError("disk full")

    monkeypatch.setattr("fetch_diagrams.Path.rename", fake_rename)

    with pytest.raises(AttachmentRetrievalError) as excinfo:
        publish_attachment_cache(snapshot, str(assets_dir))

    assert str(excinfo.value) == "OSError"
    assert (assets_dir / "old.png").read_bytes() == b"old-bytes"
    assert not (assets_dir / "new.png").exists()
    # no leftover staging directory
    assert list(tmp_path.iterdir()) == [assets_dir]


def test_publish_attachment_cache_leaves_no_partial_cache_when_no_prior_cache_existed(tmp_path, monkeypatch):
    assets_dir = tmp_path / "page.md.tmp"
    snapshot = AttachmentSnapshot(attachments=[{"title": "new.png"}], downloaded={"new.png": b"new-bytes"})

    def fake_write_bytes(self, content):
        raise OSError("disk full")

    monkeypatch.setattr("fetch_diagrams.Path.write_bytes", fake_write_bytes)

    with pytest.raises(AttachmentRetrievalError):
        publish_attachment_cache(snapshot, str(assets_dir))

    assert not assets_dir.exists()
    assert list(tmp_path.iterdir()) == []


def test_relative_link_percent_encodes_spaces():
    assert _relative_link("page.md.tmp", "Screenshot 1.png") == "page.md.tmp/Screenshot%201.png"


def test_restore_diagrams_returns_markdown_unchanged_when_no_placeholder():
    md = "# Title\n\nNo diagrams here.\n"
    snapshot = AttachmentSnapshot(attachments=[], downloaded={})
    assert restore_diagrams(md, snapshot, "page.md.tmp") == md


def test_restore_diagrams_resolves_drawio_placeholder_to_verbatim_fence():
    snapshot = AttachmentSnapshot(
        attachments=[
            {"title": "order-flow.drawio"},
            {"title": "order-flow.source.mmd"},
        ],
        downloaded={"order-flow.source.mmd": "%% diagram-id: order-flow\nflowchart TD; A-->B;\n"},
    )

    md = 'before\n\n<!-- adf:diagram drawio="order-flow.drawio" -->\n\nafter'
    result = restore_diagrams(md, snapshot, "page.md.tmp")

    assert result == (
        "before\n\n```mermaid\n%% diagram-id: order-flow\nflowchart TD; A-->B;\n```\n\nafter"
    )


def test_restore_diagrams_resolves_attachment_placeholder_via_file_id():
    snapshot = AttachmentSnapshot(
        attachments=[
            {"title": "order-flow.png", "extensions": {"fileId": "file-1"}},
            {"title": "order-flow.source.mmd"},
        ],
        downloaded={"order-flow.source.mmd": "flowchart TD; A-->B;\n"},
    )

    md = '<!-- adf:attachment media-id="file-1" alt="order-flow.png" -->'
    result = restore_diagrams(md, snapshot, "page.md.tmp")

    assert result == "```mermaid\nflowchart TD; A-->B;\n```"


def test_restore_diagrams_resolves_image_attachment_without_sidecar_to_markdown_image():
    snapshot = AttachmentSnapshot(
        attachments=[{"title": "Screenshot.png", "extensions": {"fileId": "image-1"}}],
        downloaded={"Screenshot.png": b"png-bytes"},
    )

    md = '<!-- adf:attachment media-id="image-1" alt="Screenshot.png" -->'
    result = restore_diagrams(md, snapshot, "page.md.tmp")

    assert result == "![Screenshot.png](page.md.tmp/Screenshot.png)"


def test_restore_diagrams_resolves_generic_file_attachment_without_sidecar_to_markdown_link():
    snapshot = AttachmentSnapshot(
        attachments=[{"title": "notes.pdf", "extensions": {"fileId": "file-1"}}],
        downloaded={"notes.pdf": b"pdf-bytes"},
    )

    md = '<!-- adf:attachment media-id="file-1" alt="" -->'
    result = restore_diagrams(md, snapshot, "page.md.tmp")

    assert result == "[notes.pdf](page.md.tmp/notes.pdf)"
def test_restore_diagrams_percent_encodes_spaces_in_the_relative_link():
    snapshot = AttachmentSnapshot(
        attachments=[{"title": "Screenshot 2026-02-10 113535.png", "extensions": {"fileId": "image-1"}}],
        downloaded={"Screenshot 2026-02-10 113535.png": b"png-bytes"},
    )

    md = '<!-- adf:attachment media-id="image-1" alt="Screenshot 2026-02-10 113535.png" -->'
    result = restore_diagrams(md, snapshot, "page.md.tmp")

    assert result == (
        "![Screenshot 2026-02-10 113535.png](page.md.tmp/Screenshot%202026-02-10%20113535.png)"
    )


def test_restore_diagrams_notes_when_sidecar_is_missing():
    snapshot = AttachmentSnapshot(attachments=[{"title": "order-flow.drawio"}], downloaded={})

    md = '<!-- adf:diagram drawio="order-flow.drawio" -->'
    result = restore_diagrams(md, snapshot, "page.md.tmp")

    assert "order-flow.source.mmd" in result
    assert "not attached" in result
    assert "```mermaid" not in result


def test_restore_diagrams_notes_when_media_id_has_no_matching_attachment():
    snapshot = AttachmentSnapshot(attachments=[], downloaded={})

    md = '<!-- adf:attachment media-id="unknown-file" alt="" -->'
    result = restore_diagrams(md, snapshot, "page.md.tmp")

    assert "unknown-file" in result
    assert "not found" in result


def test_restore_diagrams_without_credentials_replaces_every_placeholder_with_a_note():
    md = (
        '<!-- adf:diagram drawio="order-flow.drawio" -->\n\n'
        '<!-- adf:attachment media-id="file-1" alt="" -->'
    )
    result = restore_diagrams_without_credentials(md)

    assert result.count("ATLASSIAN_API_TOKEN") == 2
    assert "```mermaid" not in result


def test_restore_diagrams_without_credentials_leaves_plain_markdown_untouched():
    md = "# Title\n\nJust text.\n"
    assert restore_diagrams_without_credentials(md) == md


def test_restore_diagrams_skipped_replaces_every_placeholder_with_a_skipped_note():
    md = (
        '<!-- adf:diagram drawio="order-flow.drawio" -->\n\n'
        '<!-- adf:attachment media-id="file-1" alt="" -->'
    )
    result = restore_diagrams_skipped(md)

    assert result.count("skipped") == 2
    assert "```mermaid" not in result


def test_restore_diagrams_failed_replaces_every_placeholder_with_the_safe_category_only():
    md = (
        '<!-- adf:diagram drawio="order-flow.drawio" -->\n\n'
        '<!-- adf:attachment media-id="file-1" alt="" -->'
    )
    result = restore_diagrams_failed(md, "SSLError")

    assert result.count("SSLError") == 2
    assert "```mermaid" not in result


def test_restore_diagrams_resolves_image_attachment_with_size_to_an_image_plus_media_size_comment():
    snapshot = AttachmentSnapshot(
        attachments=[
            {"title": "Screenshot 2026-02-10 113535.png", "extensions": {"fileId": "image-1"}}
        ],
        downloaded={"Screenshot 2026-02-10 113535.png": b"png-bytes"},
    )

    md = (
        '<!-- adf:attachment media-id="image-1" alt="Screenshot 2026-02-10 113535.png" '
        'width="611" height="793" -->'
    )
    result = restore_diagrams(md, snapshot, "page.md.tmp")

    assert result == (
        "![Screenshot 2026-02-10 113535.png](page.md.tmp/Screenshot%202026-02-10%20113535.png)\n"
        "<!-- media-size: width=611 height=793 -->"
    )


def test_restore_diagrams_resolves_generic_file_attachment_without_a_size_comment_even_if_present():
    snapshot = AttachmentSnapshot(
        attachments=[{"title": "notes.pdf", "extensions": {"fileId": "file-1"}}],
        downloaded={"notes.pdf": b"pdf-bytes"},
    )

    md = '<!-- adf:attachment media-id="file-1" alt="" width="611" height="793" -->'
    result = restore_diagrams(md, snapshot, "page.md.tmp")

    assert result == "[notes.pdf](page.md.tmp/notes.pdf)"
