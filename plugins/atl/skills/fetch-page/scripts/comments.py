"""Read a page's comment threads over REST and render them as a Markdown section that
`/publish-page` drops (`adf:ignore`), so the reader sees each discussion next to the
`<!-- adf:comment id="..." -->` anchors the body carries.

Every REST failure raises `CommentRetrievalError` carrying only a safe category (the exception
class name) — never the original exception text, which may carry a URL or token.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser

from requests.exceptions import RequestException

_ANCHOR_RE = re.compile(r'<!--\s*adf:comment\s+id="([A-Za-z0-9-]+)"\s*-->')
_BLOCK_TAGS = {"p", "br", "li", "div", "h1", "h2", "h3", "h4", "h5", "h6", "tr"}
_PAGE_LIMIT = 100


class CommentRetrievalError(Exception):
    """Reading comments failed; the message is a safe category only."""


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in _BLOCK_TAGS:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in _BLOCK_TAGS:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def storage_to_text(storage: str) -> str:
    """Flatten a comment's storage-format body to one line of plain text."""
    extractor = _TextExtractor()
    extractor.feed(storage)
    extractor.close()
    return " ".join("".join(extractor.parts).split())


def anchored_comment_ids(markdown: str) -> set[str]:
    return set(_ANCHOR_RE.findall(markdown))


def _get_all(confluence, path: str) -> list[dict]:
    results: list[dict] = []
    params: dict | None = {"body-format": "storage", "limit": _PAGE_LIMIT}
    while path:
        response = confluence.get(path, params=params)
        results.extend(response.get("results", []))
        next_link = response.get("_links", {}).get("next")
        # `next` is site-relative and already carries every query parameter, cursor included
        path = next_link.removeprefix("/wiki") if next_link else ""
        params = None
    return results


class _Authors:
    def __init__(self, confluence) -> None:
        self._confluence = confluence
        self._names: dict[str, str] = {}

    def name(self, account_id: str | None) -> str:
        if not account_id:
            return "unknown"
        if account_id not in self._names:
            user = self._confluence.get("/rest/api/user", params={"accountId": account_id}) or {}
            self._names[account_id] = user.get("displayName") or account_id
        return self._names[account_id]


def _entry(comment: dict, authors: _Authors) -> dict:
    version = comment.get("version", {})
    return {
        "author": authors.name(version.get("authorId")),
        "created": str(version.get("createdAt", ""))[:10],
        "text": storage_to_text(comment.get("body", {}).get("storage", {}).get("value", "")),
    }


def _thread(confluence, comment: dict, kind: str, authors: _Authors) -> dict:
    properties = comment.get("properties", {})
    replies = _get_all(confluence, f"/api/v2/{kind}-comments/{comment['id']}/children")
    return {
        **_entry(comment, authors),
        "id": str(comment["id"]),
        "kind": kind,
        "markerRef": properties.get("inlineMarkerRef", ""),
        "selection": properties.get("inlineOriginalSelection", ""),
        "status": comment.get("resolutionStatus", ""),
        "link": comment.get("_links", {}).get("webui", ""),
        "replies": [_entry(reply, authors) for reply in replies],
    }


def fetch_comment_threads(confluence, page_id: str) -> list[dict]:
    """Inline threads first, then footer threads, each with its replies in API order."""
    try:
        authors = _Authors(confluence)
        threads = []
        for kind in ("inline", "footer"):
            for comment in _get_all(confluence, f"/api/v2/pages/{page_id}/{kind}-comments"):
                threads.append(_thread(confluence, comment, kind, authors))
        return threads
    except RequestException as exception:
        raise CommentRetrievalError(type(exception).__name__) from None


def _quote(text: str) -> str:
    return text.replace("\n", " ").replace("|", "\\|")


def _heading(thread: dict, anchored: set[str]) -> str:
    if thread["kind"] == "footer":
        return "### Page comment"
    state = thread["status"] or "open"
    if thread["markerRef"] in anchored:
        where = f'anchored as `id="{thread["markerRef"]}"`'
    else:
        where = "**not anchored in the body**"
    return f'### Inline on "{_quote(thread["selection"])}" — {state}, {where}'


def render_comments_section(threads: list[dict], markdown: str, site: str) -> str:
    """Empty string when the page has no comments."""
    if not threads:
        return ""
    anchored = anchored_comment_ids(markdown)
    lines = [
        "<!-- adf:ignore:start -->",
        "## Comments",
        "",
        "Read-only snapshot; `publish-page` drops this section. Keep each "
        '`<!-- adf:comment id="..." -->...<!-- /adf:comment -->` span in the body, id unchanged, '
        "to keep its inline comment attached.",
    ]
    for thread in threads:
        lines += ["", _heading(thread, anchored), ""]
        lines.append(f"- **{thread['author']}** ({thread['created']}): {thread['text']}")
        lines += [f"  - **{r['author']}** ({r['created']}): {r['text']}" for r in thread["replies"]]
        if thread["link"]:
            lines.append(f"- [Open in Confluence]({site}/wiki{thread['link']})")
    lines.append("<!-- adf:ignore:end -->")
    return "\n".join(lines) + "\n"


def comments_note(reason: str) -> str:
    """Short ignored note used instead of the section when comments cannot be read."""
    return f"<!-- adf:ignore:start -->\n> Comments not listed: {reason}.\n<!-- adf:ignore:end -->\n"
