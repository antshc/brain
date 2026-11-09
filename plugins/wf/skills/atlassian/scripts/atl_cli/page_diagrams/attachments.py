"""Attachment upload + fileId read-back (I/O: Confluence REST v1 under `/wiki`, via the
client from `confluence_client.py`).

Only touches `confluence`; tested by passing a stub with `put`/`get`.
"""
from __future__ import annotations

import mimetypes
from typing import Any

_UPLOAD_HEADERS = {"X-Atlassian-Token": "no-check", "Accept": "application/json"}


def attach_file(confluence: Any, path: str, filename: str, page_id: str) -> None:
    """Create the attachment, or add a new version of a same-named one (`PUT .../child/attachment`)."""
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    with open(path, "rb") as handle:
        confluence.put(
            f"/rest/api/content/{page_id}/child/attachment",
            headers=_UPLOAD_HEADERS,
            files={"file": (filename, handle, content_type)},
            data={"minorEdit": "true"},
        )


def upload_files(confluence: Any, page_id: str, files: list[dict]) -> dict:
    """Upload every `{"path", "filename"}` entry, then re-read metadata for the media-service
    fileIds. Returns {filename: fileId}. Re-uploading a same-named file creates a new
    attachment *version*, so the fileId is never cached across runs — always read back after
    upload.
    """
    if not files:
        return {}

    for f in files:
        attach_file(confluence, f["path"], f["filename"], page_id)

    resp = confluence.get(
        f"/rest/api/content/{page_id}/child/attachment",
        params={"expand": "extensions.fileId", "limit": 200},
    )
    file_ids: dict[str, str] = {}
    for a in resp["results"]:
        file_ids[a["title"]] = a["extensions"]["fileId"]
    for f in files:
        if f["filename"] not in file_ids:
            raise RuntimeError(f"Uploaded attachment {f['filename']!r} not found on re-read")
    return file_ids


def upload_diagrams(confluence: Any, page_id: str, diagrams: list[dict]) -> dict:
    """Upload every file the renderer produced, then re-read metadata for the media-service fileIds.

    Reads each diagram's `attachments` list rather than a single `filename`, because the
    count varies by renderer: one PNG for `png`, two files for `drawio`, none for `mermaid`
    when the macro carries the source inline. A renderer that attaches nothing is a normal
    case and skips the round trip entirely.

    Returns {filename: fileId}. Re-uploading a same-named file creates a new attachment
    *version*, so the fileId is never cached across runs — always read back after upload.
    """
    return upload_files(confluence, page_id, [a for d in diagrams for a in d.get("attachments", [])])
