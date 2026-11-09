from unittest.mock import MagicMock

import pytest

from atl_cli.page_diagrams.attachments import attach_file, upload_diagrams, upload_files


def _file(tmp_path, name: str, content: bytes = b"bytes") -> str:
    path = tmp_path / name
    path.write_bytes(content)
    return str(path)


def _uploaded(confluence) -> list[tuple[str, str]]:
    """(path, uploaded filename) per `PUT .../child/attachment` call."""
    return [(call.args[0], call.kwargs["files"]["file"][0]) for call in confluence.put.call_args_list]


def make_diagrams(tmp_path):
    return [
        {"attachments": [{"path": _file(tmp_path, "00-a.png"), "filename": "00-a.png"}]},
        {"attachments": [{"path": _file(tmp_path, "01-b.png"), "filename": "01-b.png"}]},
    ]


def test_attach_file_puts_multipart_with_no_check_header(tmp_path):
    confluence = MagicMock()
    path = _file(tmp_path, "diagram.png", b"png-bytes")

    def fake_put(path_arg, **kwargs):
        name, handle, content_type = kwargs["files"]["file"]
        fake_put.seen = (path_arg, name, handle.read(), content_type, kwargs["headers"], kwargs["data"])

    confluence.put.side_effect = fake_put

    attach_file(confluence, path, "diagram.png", "12345")

    assert fake_put.seen == (
        "/rest/api/content/12345/child/attachment",
        "diagram.png",
        b"png-bytes",
        "image/png",
        {"X-Atlassian-Token": "no-check", "Accept": "application/json"},
        {"minorEdit": "true"},
    )


def test_upload_diagrams_attaches_each_file_then_reads_back_file_ids(tmp_path):
    confluence = MagicMock()
    confluence.get.return_value = {
        "results": [
            {"title": "00-a.png", "extensions": {"fileId": "file-1"}},
            {"title": "01-b.png", "extensions": {"fileId": "file-2"}},
        ]
    }

    result = upload_diagrams(confluence, "12345", make_diagrams(tmp_path))

    assert _uploaded(confluence) == [
        ("/rest/api/content/12345/child/attachment", "00-a.png"),
        ("/rest/api/content/12345/child/attachment", "01-b.png"),
    ]
    confluence.get.assert_called_once_with(
        "/rest/api/content/12345/child/attachment",
        params={"expand": "extensions.fileId", "limit": 200},
    )
    assert result == {"00-a.png": "file-1", "01-b.png": "file-2"}


def test_upload_diagrams_raises_when_attachment_missing_on_reread(tmp_path):
    confluence = MagicMock()
    confluence.get.return_value = {"results": [{"title": "00-a.png", "extensions": {"fileId": "file-1"}}]}

    with pytest.raises(RuntimeError, match="01-b.png"):
        upload_diagrams(confluence, "12345", make_diagrams(tmp_path))


def test_upload_diagrams_uploads_every_file_a_diagram_produced(tmp_path):
    confluence = MagicMock()
    confluence.get.return_value = {
        "results": [
            {"title": "00-a.drawio", "extensions": {"fileId": "file-1"}},
            {"title": "00-a.drawio.png", "extensions": {"fileId": "file-2"}},
        ]
    }
    diagrams = [
        {
            "attachments": [
                {"path": _file(tmp_path, "00-a.drawio"), "filename": "00-a.drawio"},
                {"path": _file(tmp_path, "00-a.drawio.png"), "filename": "00-a.drawio.png"},
            ]
        }
    ]

    result = upload_diagrams(confluence, "12345", diagrams)

    assert confluence.put.call_count == 2
    assert result == {"00-a.drawio": "file-1", "00-a.drawio.png": "file-2"}


def test_upload_diagrams_with_nothing_to_attach_skips_the_round_trip():
    confluence = MagicMock()

    result = upload_diagrams(confluence, "12345", [{"attachments": []}, {"attachments": []}])

    assert result == {}
    confluence.put.assert_not_called()
    confluence.get.assert_not_called()


def test_upload_files_attaches_a_plain_list_of_local_files(tmp_path):
    confluence = MagicMock()
    confluence.get.return_value = {"results": [{"title": "notes.pdf", "extensions": {"fileId": "file-1"}}]}

    result = upload_files(confluence, "12345", [{"path": _file(tmp_path, "notes.pdf"), "filename": "notes.pdf"}])

    assert _uploaded(confluence) == [("/rest/api/content/12345/child/attachment", "notes.pdf")]
    assert result == {"notes.pdf": "file-1"}


def test_upload_files_with_an_empty_list_skips_the_round_trip():
    confluence = MagicMock()

    result = upload_files(confluence, "12345", [])

    assert result == {}
    confluence.put.assert_not_called()
    confluence.get.assert_not_called()
