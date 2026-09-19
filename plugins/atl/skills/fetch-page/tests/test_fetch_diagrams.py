from unittest.mock import MagicMock

from fetch_diagrams import (
    has_diagram_placeholder,
    restore_diagrams,
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


def test_has_diagram_placeholder_detects_drawio_and_media_markers():
    assert has_diagram_placeholder('<!-- adf:diagram drawio="x.drawio" -->')
    assert has_diagram_placeholder('<!-- adf:diagram media-id="file-1" -->')
    assert not has_diagram_placeholder("plain text, no diagrams")


def test_restore_diagrams_returns_markdown_unchanged_when_no_placeholder():
    confluence = MagicMock()
    md = "# Title\n\nNo diagrams here.\n"
    assert restore_diagrams(confluence, "123", md) == md
    confluence.get_attachments_from_content.assert_not_called()


def test_restore_diagrams_resolves_drawio_placeholder_to_verbatim_fence():
    attachments = [
        {"title": "order-flow.drawio", "_links": {"download": "/download/order-flow.drawio"}},
        {"title": "order-flow.source.mmd", "_links": {"download": "/download/order-flow.source.mmd"}},
    ]
    downloads = {"/download/order-flow.source.mmd": "%% diagram-id: order-flow\nflowchart TD; A-->B;\n"}
    confluence = _confluence(attachments, downloads)

    md = 'before\n\n<!-- adf:diagram drawio="order-flow.drawio" -->\n\nafter'
    result = restore_diagrams(confluence, "123", md)

    assert result == (
        "before\n\n```mermaid\n%% diagram-id: order-flow\nflowchart TD; A-->B;\n```\n\nafter"
    )


def test_restore_diagrams_resolves_media_placeholder_via_file_id():
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

    md = '<!-- adf:diagram media-id="file-1" -->'
    result = restore_diagrams(confluence, "123", md)

    assert result == "```mermaid\nflowchart TD; A-->B;\n```"


def test_restore_diagrams_notes_when_sidecar_is_missing():
    attachments = [{"title": "order-flow.drawio", "_links": {"download": "/download/order-flow.drawio"}}]
    confluence = _confluence(attachments, downloads={})

    md = '<!-- adf:diagram drawio="order-flow.drawio" -->'
    result = restore_diagrams(confluence, "123", md)

    assert "order-flow.source.mmd" in result
    assert "not attached" in result
    assert "```mermaid" not in result


def test_restore_diagrams_notes_when_media_id_has_no_matching_attachment():
    confluence = _confluence(attachments=[], downloads={})

    md = '<!-- adf:diagram media-id="unknown-file" -->'
    result = restore_diagrams(confluence, "123", md)

    assert "unknown-file" in result
    assert "not found" in result


def test_restore_diagrams_handles_bytes_download_response():
    attachments = [{"title": "order-flow.source.mmd", "_links": {"download": "/download/order-flow.source.mmd"}}]
    downloads = {"/download/order-flow.source.mmd": b"flowchart TD; A-->B;\n"}
    confluence = _confluence(attachments, downloads)

    md = '<!-- adf:diagram drawio="order-flow.drawio" -->'
    result = restore_diagrams(confluence, "123", md)

    assert result == "```mermaid\nflowchart TD; A-->B;\n```"


def test_restore_diagrams_without_credentials_replaces_every_placeholder_with_a_note():
    md = (
        '<!-- adf:diagram drawio="order-flow.drawio" -->\n\n'
        '<!-- adf:diagram media-id="file-1" -->'
    )
    result = restore_diagrams_without_credentials(md)

    assert result.count("ATLASSIAN_API_TOKEN") == 2
    assert "```mermaid" not in result


def test_restore_diagrams_without_credentials_leaves_plain_markdown_untouched():
    md = "# Title\n\nJust text.\n"
    assert restore_diagrams_without_credentials(md) == md
