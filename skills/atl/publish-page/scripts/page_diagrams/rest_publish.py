"""Large-document REST publish fallback (I/O: Confluence REST client, via
`atlassian-python-api` — the MCP's inline-body publish tools mangle/truncate bodies past
roughly 100-300KB, so a large ADF document needs to go over the REST v2 pages API instead.

Only touches `confluence`; tested by passing a stub with `get`/`put`/`post`, mirroring
`attachments.py`'s low-level `.get()` pattern.
"""
from __future__ import annotations

import json

from atlassian import Confluence


def adf_body_size(adf: dict) -> int:
    return len(json.dumps(adf).encode("utf-8"))


def get_page_version(confluence: Confluence, page_id: str) -> int:
    resp = confluence.get(f"/api/v2/pages/{page_id}")
    return resp["version"]["number"]


def update_page_adf(confluence: Confluence, page_id: str, title: str, adf: dict, version: int) -> dict:
    return confluence.put(
        f"/api/v2/pages/{page_id}",
        data={
            "id": page_id,
            "status": "current",
            "title": title,
            "body": {"representation": "atlas_doc_format", "value": json.dumps(adf)},
            "version": {"number": version + 1},
        },
    )


def create_page_adf(confluence: Confluence, space_id: str, title: str, adf: dict) -> dict:
    return confluence.post(
        "/api/v2/pages",
        data={
            "spaceId": space_id,
            "status": "current",
            "title": title,
            "body": {"representation": "atlas_doc_format", "value": json.dumps(adf)},
        },
    )
