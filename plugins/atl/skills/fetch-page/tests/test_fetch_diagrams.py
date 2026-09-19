from unittest.mock import MagicMock

from fetch_diagrams import (
    _relative_link,
    download_attachment_bytes,
    find_attachment_reference_nodes,
    has_attachment_reference,
    has_diagram_placeholder,
    restore_diagrams,
    restore_diagrams_without_credentials,
    save_attachments,
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


def test_save_attachments_writes_every_attachment_and_returns_bytes_map(tmp_path):
    attachments = [
        {"title": "a.png", "_links": {"download": "/download/a.png"}},
        {"title": "b.txt", "_links": {"download": "/download/b.txt"}},
    ]
    downloads = {"/download/a.png": b"png-bytes", "/download/b.txt": "text"}
    confluence = _confluence(attachments, downloads)
    assets_dir = tmp_path / "page.md.tmp"

    result = save_attachments(confluence, "123", str(assets_dir))

    assert result == {"a.png": b"png-bytes", "b.txt": b"text"}
    assert (assets_dir / "a.png").read_bytes() == b"png-bytes"
    assert (assets_dir / "b.txt").read_bytes() == b"text"


def test_save_attachments_skips_mkdir_when_attachment_list_is_empty(tmp_path):
    confluence = _confluence(attachments=[], downloads={})
    assets_dir = tmp_path / "page.md.tmp"

    result = save_attachments(confluence, "123", str(assets_dir))

    assert result == {}
    assert not assets_dir.exists()


def test_relative_link_percent_encodes_spaces():
    assert _relative_link("page.md.tmp", "Screenshot 1.png") == "page.md.tmp/Screenshot%201.png"


def test_restore_diagrams_returns_markdown_unchanged_when_no_placeholder():
    confluence = MagicMock()
    md = "# Title\n\nNo diagrams here.\n"
    assert restore_diagrams(confluence, "123", md, {}, "page.md.tmp") == md
    confluence.get_attachments_from_content.assert_not_called()


def test_restore_diagrams_resolves_drawio_placeholder_to_verbatim_fence():
    attachments = [
        {"title": "order-flow.drawio", "_links": {"download": "/download/order-flow.drawio"}},
        {"title": "order-flow.source.mmd", "_links": {"download": "/download/order-flow.source.mmd"}},
    ]
    downloads = {"/download/order-flow.source.mmd": "%% diagram-id: order-flow\nflowchart TD; A-->B;\n"}
    confluence = _confluence(attachments, downloads)

    md = 'before\n\n<!-- adf:diagram drawio="order-flow.drawio" -->\n\nafter'
    result = restore_diagrams(confluence, "123", md, {}, "page.md.tmp")

    assert result == (
        "before\n\n```mermaid\n%% diagram-id: order-flow\nflowchart TD; A-->B;\n```\n\nafter"
    )


def test_restore_diagrams_resolves_attachment_placeholder_via_file_id():
    attachments = [
        {
            "title": "order-flow.png",
            "extensions": {"fileId": "file-1"},
            "_links": {"download": "/download/order-flow.png"},
        },
        {"title": "order-flow.source.mmd", "_links": {"download": "/download/order-flow.source.mmd"}},
    ]
    downloads = {"/download/order-flow.source.mmd": "flowchart TD; A-->B;\n"}
    confluence = _confluence(attachments, downloads)

    md = '<!-- adf:attachment media-id="file-1" alt="order-flow.png" -->'
    result = restore_diagrams(confluence, "123", md, {}, "page.md.tmp")

    assert result == "```mermaid\nflowchart TD; A-->B;\n```"


def test_restore_diagrams_reuses_already_downloaded_sidecar_bytes():
    attachments = [
        {"title": "order-flow.drawio", "_links": {"download": "/download/order-flow.drawio"}},
        {"title": "order-flow.source.mmd", "_links": {"download": "/download/order-flow.source.mmd"}},
    ]
    confluence = _confluence(attachments, downloads={})
    downloaded = {"order-flow.source.mmd": "flowchart TD; A-->B;\n"}

    md = '<!-- adf:diagram drawio="order-flow.drawio" -->'
    result = restore_diagrams(confluence, "123", md, downloaded, "page.md.tmp")

    assert result == "```mermaid\nflowchart TD; A-->B;\n```"
    confluence.get.assert_not_called()


def test_restore_diagrams_resolves_image_attachment_without_sidecar_to_markdown_image():
    attachments = [
        {
            "title": "Screenshot.png",
            "extensions": {"fileId": "image-1"},
            "_links": {"download": "/download/Screenshot.png"},
        }
    ]
    confluence = _confluence(attachments, downloads={})
    downloaded = {"Screenshot.png": b"png-bytes"}

    md = '<!-- adf:attachment media-id="image-1" alt="Screenshot.png" -->'
    result = restore_diagrams(confluence, "123", md, downloaded, "page.md.tmp")

    assert result == "![Screenshot.png](page.md.tmp/Screenshot.png)"


def test_restore_diagrams_resolves_generic_file_attachment_without_sidecar_to_markdown_link():
    attachments = [
        {
            "title": "notes.pdf",
            "extensions": {"fileId": "file-1"},
            "_links": {"download": "/download/notes.pdf"},
        }
    ]
    confluence = _confluence(attachments, downloads={})
    downloaded = {"notes.pdf": b"pdf-bytes"}

    md = '<!-- adf:attachment media-id="file-1" alt="" -->'
    result = restore_diagrams(confluence, "123", md, downloaded, "page.md.tmp")

    assert result == "[notes.pdf](page.md.tmp/notes.pdf)"


def test_restore_diagrams_percent_encodes_spaces_in_the_relative_link():
    attachments = [
        {
            "title": "Screenshot 2026-02-10 113535.png",
            "extensions": {"fileId": "image-1"},
            "_links": {"download": "/download/Screenshot.png"},
        }
    ]
    confluence = _confluence(attachments, downloads={})
    downloaded = {"Screenshot 2026-02-10 113535.png": b"png-bytes"}

    md = '<!-- adf:attachment media-id="image-1" alt="Screenshot 2026-02-10 113535.png" -->'
    result = restore_diagrams(confluence, "123", md, downloaded, "page.md.tmp")

    assert result == (
        "![Screenshot 2026-02-10 113535.png](page.md.tmp/Screenshot%202026-02-10%20113535.png)"
    )


def test_restore_diagrams_notes_when_sidecar_is_missing():
    attachments = [{"title": "order-flow.drawio", "_links": {"download": "/download/order-flow.drawio"}}]
    confluence = _confluence(attachments, downloads={})

    md = '<!-- adf:diagram drawio="order-flow.drawio" -->'
    result = restore_diagrams(confluence, "123", md, {}, "page.md.tmp")

    assert "order-flow.source.mmd" in result
    assert "not attached" in result
    assert "```mermaid" not in result


def test_restore_diagrams_notes_when_media_id_has_no_matching_attachment():
    confluence = _confluence(attachments=[], downloads={})

    md = '<!-- adf:attachment media-id="unknown-file" alt="" -->'
    result = restore_diagrams(confluence, "123", md, {}, "page.md.tmp")

    assert "unknown-file" in result
    assert "not found" in result


def test_restore_diagrams_handles_bytes_download_response():
    attachments = [{"title": "order-flow.source.mmd", "_links": {"download": "/download/order-flow.source.mmd"}}]
    downloads = {"/download/order-flow.source.mmd": b"flowchart TD; A-->B;\n"}
    confluence = _confluence(attachments, downloads)

    md = '<!-- adf:diagram drawio="order-flow.drawio" -->'
    result = restore_diagrams(confluence, "123", md, {}, "page.md.tmp")

    assert result == "```mermaid\nflowchart TD; A-->B;\n```"


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
