"""Attachment upload + fileId read-back (I/O: Confluence REST client).

Only touches `confluence`; tested by passing a stub with `attach_file`/`get`.
"""
from __future__ import annotations

from atlassian import Confluence


def upload_diagrams(confluence: Confluence, page_id: str, diagrams: list[dict]) -> dict:
    """Upload each PNG, then re-read attachment metadata for the media-service fileId.

    Returns {filename: fileId}. Re-uploading a same-named file creates a new attachment
    *version*, so the fileId is never cached across runs — always read back after upload.
    """
    for d in diagrams:
        confluence.attach_file(d["png_path"], name=d["filename"], page_id=page_id)

    resp = confluence.get(
        f"/rest/api/content/{page_id}/child/attachment",
        params={"expand": "extensions.fileId", "limit": 200},
    )
    file_ids: dict[str, str] = {}
    for a in resp["results"]:
        file_ids[a["title"]] = a["extensions"]["fileId"]
    for d in diagrams:
        if d["filename"] not in file_ids:
            raise RuntimeError(f"Uploaded attachment {d['filename']!r} not found on re-read")
    return file_ids
