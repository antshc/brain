"""Draw.io custom content upsert (I/O: Confluence REST client, via `atlassian-python-api`).

A published Draw.io diagram is four objects: the `.drawio` attachment, its `.drawio.png`
preview, a custom content record of the app's own type, and the ADF extension node pointing
at that record. This module owns the third. The macro is a Forge extension, but its storage
is the classic mxGraph model — ordinary custom content, writable with an API token.

The body is search metadata only; the diagram itself never lives here, it lives in the
attachment. Republishing looks the record up by container and title first, so a second
publish bumps the existing record instead of stacking a duplicate beside it.

A create without `space` is rejected (`Could not create content with type ...drawio-diagram`),
even though `container` already names the page — hence the extra page read. The type is also
only addressable per page: the site-wide `GET /rest/api/content?type=<DIAGRAM_TYPE>` answers
`Cannot find custom content type` on sites where the app is installed and working, so it can't
be used to probe availability.

Only touches `confluence`; tested by passing a stub with `get`/`post`/`put`.
"""
from __future__ import annotations

import json

from atlassian import Confluence

DIAGRAM_TYPE = "ac:com.mxgraph.confluence.plugins.diagramly:drawio-diagram"


def _body(page_id: str, diagram_name: str, search: str, revision: int) -> str:
    return json.dumps(
        {
            "search": search,
            "pageId": page_id,
            "type": "page",
            "diagramName": diagram_name,
            "revision": revision,
            "isSketch": False,
        }
    )


def page_space_key(confluence: Confluence, page_id: str) -> str:
    """The space key of `page_id` — a create without it is rejected, `container` notwithstanding."""
    page = confluence.get(f"/rest/api/content/{page_id}", params={"expand": "space"})
    return page["space"]["key"]


def find_diagram(confluence: Confluence, page_id: str, diagram_name: str) -> dict | None:
    """The page's existing custom content for `diagram_name`, or `None` on a first publish."""
    resp = confluence.get(
        f"/rest/api/content/{page_id}/child/{DIAGRAM_TYPE}",
        params={"expand": "version", "limit": 200},
    )
    for item in resp.get("results", []):
        if item.get("title") == diagram_name:
            return item
    return None


def upsert_diagram(confluence: Confluence, page_id: str, diagram_name: str, search: str) -> dict:
    """Create or update the diagram's custom content; returns `{"id", "revision"}`.

    `revision` tracks the custom content version, which the extension node carries as both
    `revision` and `contentVer` so the app re-reads the attachment instead of serving a
    cached render of the previous publish.
    """
    existing = find_diagram(confluence, page_id, diagram_name)
    if existing is None:
        created = confluence.post(
            "/rest/api/content",
            data={
                "type": DIAGRAM_TYPE,
                "status": "current",
                "title": diagram_name,
                "space": {"key": page_space_key(confluence, page_id)},
                "container": {"id": page_id, "type": "page"},
                "body": {"raw": {"value": _body(page_id, diagram_name, search, 1), "representation": "raw"}},
            },
        )
        return {"id": str(created["id"]), "revision": 1}

    revision = existing["version"]["number"] + 1
    content_id = str(existing["id"])
    confluence.put(
        f"/rest/api/content/{content_id}",
        data={
            "id": content_id,
            "type": DIAGRAM_TYPE,
            "status": "current",
            "title": diagram_name,
            "container": {"id": page_id, "type": "page"},
            "body": {"raw": {"value": _body(page_id, diagram_name, search, revision), "representation": "raw"}},
            "version": {"number": revision},
        },
    )
    return {"id": content_id, "revision": revision}
