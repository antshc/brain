"""ADF page publish over the Confluence REST v2 pages API (I/O: Confluence REST client, via
`atlassian-python-api`).

Only touches `confluence`; tested by passing a stub with `get`/`put`/`post`, mirroring
`attachments.py`'s low-level `.get()` pattern.
"""
from __future__ import annotations

import json

from typing import Any


def adf_body_size(adf: dict) -> int:
    return len(json.dumps(adf).encode("utf-8"))


def get_page_version(confluence: Any, page_id: str) -> int:
    resp = confluence.get(f"/api/v2/pages/{page_id}")
    return resp["version"]["number"]


def update_page_adf(confluence: Any, page_id: str, title: str, adf: dict, version: int) -> dict:
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


def create_page_adf(
    confluence: Any, space_id: str, title: str, adf: dict, parent_id: str | None = None,
) -> dict:
    return confluence.post(
        "/api/v2/pages",
        data={
            "spaceId": space_id,
            **({"parentId": parent_id} if parent_id is not None else {}),
            "status": "current",
            "title": title,
            "body": {"representation": "atlas_doc_format", "value": json.dumps(adf)},
        },
    )


def verify_page_parent(confluence: Any, page_id: str, parent_id: str) -> None:
    page = confluence.get(f"/api/v2/pages/{page_id}")
    if str(page.get("parentId")) != parent_id:
        raise ValueError(f"page {page_id} parent differs from requested parent {parent_id}")
