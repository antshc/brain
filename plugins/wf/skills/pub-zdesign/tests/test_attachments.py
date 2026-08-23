from unittest.mock import MagicMock

import pytest

from zdesign_publisher.attachments import upload_diagrams


def make_diagrams():
    return [
        {"png_path": "/tmp/00-a.png", "filename": "00-a.png"},
        {"png_path": "/tmp/01-b.png", "filename": "01-b.png"},
    ]


def test_upload_diagrams_attaches_each_file_then_reads_back_file_ids():
    confluence = MagicMock()
    confluence.get.return_value = {
        "results": [
            {"title": "00-a.png", "extensions": {"fileId": "file-1"}},
            {"title": "01-b.png", "extensions": {"fileId": "file-2"}},
        ]
    }
    diagrams = make_diagrams()

    result = upload_diagrams(confluence, "12345", diagrams)

    assert confluence.attach_file.call_count == 2
    confluence.attach_file.assert_any_call("/tmp/00-a.png", name="00-a.png", page_id="12345")
    confluence.attach_file.assert_any_call("/tmp/01-b.png", name="01-b.png", page_id="12345")
    confluence.get.assert_called_once_with(
        "/rest/api/content/12345/child/attachment",
        params={"expand": "extensions.fileId", "limit": 200},
    )
    assert result == {"00-a.png": "file-1", "01-b.png": "file-2"}


def test_upload_diagrams_raises_when_attachment_missing_on_reread():
    confluence = MagicMock()
    confluence.get.return_value = {"results": [{"title": "00-a.png", "extensions": {"fileId": "file-1"}}]}
    diagrams = make_diagrams()  # includes 01-b.png, which won't be in the reread response

    with pytest.raises(RuntimeError, match="01-b.png"):
        upload_diagrams(confluence, "12345", diagrams)
