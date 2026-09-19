"""Attachment upload + fileId read-back (I/O: Confluence REST client, via `atlassian-python-api`
— the one thing the Atlassian MCP does not expose).

Only touches `confluence`; tested by passing a stub with `attach_file`/`get`.
"""
from __future__ import annotations

from atlassian import Confluence


def upload_files(confluence: Confluence, page_id: str, files: list[dict]) -> dict:
    """Upload every `{"path", "filename"}` entry, then re-read metadata for the media-service
    fileIds. Returns {filename: fileId}. Re-uploading a same-named file creates a new
    attachment *version*, so the fileId is never cached across runs — always read back after
    upload.
    """
    if not files:
        return {}

    for f in files:
        confluence.attach_file(f["path"], name=f["filename"], page_id=page_id)

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


def upload_diagrams(confluence: Confluence, page_id: str, diagrams: list[dict]) -> dict:
    """Upload every file the renderer produced, then re-read metadata for the media-service fileIds.

    Reads each diagram's `attachments` list rather than a single `filename`, because the
    count varies by renderer: one PNG for `png`, two files for `drawio`, none for `mermaid`
    when the macro carries the source inline. A renderer that attaches nothing is a normal
    case and skips the round trip entirely.

    Returns {filename: fileId}. Re-uploading a same-named file creates a new attachment
    *version*, so the fileId is never cached across runs — always read back after upload.
    """
    return upload_files(confluence, page_id, [a for d in diagrams for a in d.get("attachments", [])])
