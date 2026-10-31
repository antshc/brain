"""Inline-comment guard for an update publish (I/O: Confluence REST client).

A publish regenerates the whole page body from Markdown. An inline comment stays highlighted
only while the new body still carries its `annotation` mark (Markdown: an
`<!-- adf:comment id="..." -->` span); otherwise Confluence keeps the comment, still open, but
detached from any text. `plan` finds the open comments this publish will detach, before it
runs; `post_notice` then leaves one page comment explaining which ones and how to reattach them.

A comment already detached before this publish is not reported again, so republishing never
repeats a notice.
"""
from __future__ import annotations

import html
import json
import re

from atlassian import Confluence

_PAGE_LIMIT = 100
_TAG_RE = re.compile(r"<[^>]+>")
_EXCERPT_CHARS = 200


def comment_ids(adf: dict | list) -> set[str]:
    """Every inline-comment annotation id anywhere in an ADF tree."""
    ids: set[str] = set()
    stack = [adf]
    while stack:
        node = stack.pop()
        if isinstance(node, list):
            stack.extend(node)
            continue
        if not isinstance(node, dict):
            continue
        for mark in node.get("marks", []):
            attrs = mark.get("attrs", {})
            if mark.get("type") == "annotation" and attrs.get("annotationType", "inlineComment") == "inlineComment":
                ids.add(attrs.get("id", ""))
        stack.extend(node.get("content", []))
    ids.discard("")
    return ids


def _live_comment_ids(confluence: Confluence, page_id: str) -> set[str]:
    page = confluence.get(f"/api/v2/pages/{page_id}", params={"body-format": "atlas_doc_format"})
    value = page.get("body", {}).get("atlas_doc_format", {}).get("value") or "{}"
    return comment_ids(json.loads(value))


def _inline_comments(confluence: Confluence, page_id: str) -> list[dict]:
    results: list[dict] = []
    path = f"/api/v2/pages/{page_id}/inline-comments"
    params: dict | None = {"body-format": "storage", "limit": _PAGE_LIMIT}
    while path:
        response = confluence.get(path, params=params)
        results.extend(response.get("results", []))
        next_link = response.get("_links", {}).get("next")
        path = next_link.removeprefix("/wiki") if next_link else ""
        params = None
    return results


def _author(confluence: Confluence, account_id: str | None, cache: dict[str, str]) -> str:
    if not account_id:
        return "unknown"
    if account_id not in cache:
        user = confluence.get("/rest/api/user", params={"accountId": account_id}) or {}
        cache[account_id] = user.get("displayName") or account_id
    return cache[account_id]


def _excerpt(storage: str) -> str:
    text = " ".join(html.unescape(_TAG_RE.sub(" ", storage)).split())
    return text if len(text) <= _EXCERPT_CHARS else text[: _EXCERPT_CHARS - 1] + "…"


def plan(confluence: Confluence, page_id: str, final_adf: dict) -> dict:
    """`orphaned`: open comments anchored now but absent from `final_adf`.
    `unknownIds`: ids in `final_adf` that match no comment on the page (typo or foreign page)."""
    final_ids = comment_ids(final_adf)
    live_ids = _live_comment_ids(confluence, page_id)
    comments = _inline_comments(confluence, page_id)
    known = {c.get("properties", {}).get("inlineMarkerRef", "") for c in comments}
    authors: dict[str, str] = {}
    orphaned = []
    for comment in comments:
        properties = comment.get("properties", {})
        ref = properties.get("inlineMarkerRef", "")
        if comment.get("resolutionStatus", "open") != "open" or ref not in live_ids or ref in final_ids:
            continue
        orphaned.append(
            {
                "id": str(comment["id"]),
                "markerRef": ref,
                "selection": properties.get("inlineOriginalSelection", ""),
                "author": _author(confluence, comment.get("version", {}).get("authorId"), authors),
                "excerpt": _excerpt(comment.get("body", {}).get("storage", {}).get("value", "")),
                "link": comment.get("_links", {}).get("webui", ""),
            }
        )
    return {"orphaned": orphaned, "unknownIds": sorted(final_ids - known)}


def notice_storage(orphaned: list[dict], base_url: str) -> str:
    """Storage-format body for the page comment listing detached inline comments."""
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(c['selection'])}</td>"
        f"<td>{html.escape(c['author'])}</td>"
        f"<td>{html.escape(c['excerpt'])}</td>"
        f"<td><a href=\"{html.escape(base_url + c['link'], quote=True)}\">open</a></td>"
        f"<td><code>{html.escape(c['markerRef'])}</code></td>"
        "</tr>"
        for c in orphaned
    )
    count = len(orphaned)
    noun = "inline comment" if count == 1 else "inline comments"
    return (
        f"<p><strong>Publish note:</strong> this update from Markdown removed the highlighted text "
        f"of {count} open {noun}. Confluence keeps each comment and its replies, still open, but it "
        f"is no longer attached to any text on the page, so readers will not see it beside the "
        f"content it discusses.</p>"
        "<table><tbody>"
        "<tr><th>Highlighted text</th><th>Author</th><th>Comment</th><th>Link</th><th>Anchor id</th></tr>"
        f"{rows}</tbody></table>"
        "<p>To reattach a comment, wrap the text it belongs to in the page's Markdown as "
        "<code>&lt;!-- adf:comment id=\"ANCHOR-ID\" --&gt;text&lt;!-- /adf:comment --&gt;</code> "
        "using the anchor id above, and publish again. If the comment no longer applies, resolve "
        "it instead.</p>"
    )


def post_notice(confluence: Confluence, page_id: str, storage: str) -> str:
    created = confluence.post(
        "/api/v2/footer-comments",
        data={"pageId": page_id, "body": {"representation": "storage", "value": storage}},
    )
    return str(created["id"])
