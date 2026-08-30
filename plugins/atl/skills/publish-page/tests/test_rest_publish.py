from unittest.mock import MagicMock

from page_diagrams.rest_publish import adf_body_size, create_page_adf, get_page_version, update_page_adf


def test_adf_body_size_counts_utf8_bytes():
    adf = {"type": "doc", "content": []}
    assert adf_body_size(adf) == len('{"type": "doc", "content": []}')


def test_get_page_version_reads_version_number():
    confluence = MagicMock()
    confluence.get.return_value = {"version": {"number": 3}}

    version = get_page_version(confluence, "123")

    confluence.get.assert_called_once_with("/api/v2/pages/123")
    assert version == 3


def test_update_page_adf_puts_incremented_version():
    confluence = MagicMock()
    confluence.put.return_value = {"id": "123"}
    adf = {"type": "doc", "content": []}

    result = update_page_adf(confluence, "123", "Title", adf, version=3)

    confluence.put.assert_called_once()
    args, kwargs = confluence.put.call_args
    assert args[0] == "/api/v2/pages/123"
    assert kwargs["data"]["version"]["number"] == 4
    assert kwargs["data"]["body"]["representation"] == "atlas_doc_format"
    assert result == {"id": "123"}


def test_create_page_adf_posts_new_page():
    confluence = MagicMock()
    confluence.post.return_value = {"id": "456"}
    adf = {"type": "doc", "content": []}

    result = create_page_adf(confluence, "space-1", "Title", adf)

    confluence.post.assert_called_once()
    args, kwargs = confluence.post.call_args
    assert args[0] == "/api/v2/pages"
    assert kwargs["data"]["spaceId"] == "space-1"
    assert kwargs["data"]["title"] == "Title"
    assert result == {"id": "456"}
