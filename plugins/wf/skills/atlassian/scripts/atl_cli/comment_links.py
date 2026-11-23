"""Confluence page smart-link cards for Jira comment bodies (I/O: one Confluence REST lookup per page id).

A page reference becomes an ADF `inlineCard` on its own paragraph, the same card Jira shows when a
page URL is pasted. A reference is a page URL on the configured site, or a numeric page id that is
resolved to its canonical URL.
"""
from __future__ import annotations

from collections.abc import Callable
from urllib.parse import urlparse

import requests

from .config import site_url

PageResolver = Callable[[str], str]


def page_resolver(credentials: dict[str, str]) -> PageResolver:
    """A function mapping a page URL or numeric id to the page's canonical URL on the configured site."""
    site = site_url(credentials)
    host = urlparse(site).netloc

    def resolve(reference: str) -> str:
        reference = reference.strip()
        if reference.isdigit():
            response = requests.get(
                f"{site}/wiki/api/v2/pages/{reference}", auth=(credentials["email"], credentials["token"]), timeout=30
            )
            if response.status_code != 200:
                raise ValueError(f"page {reference} not found (HTTP {response.status_code})")
            links = response.json().get("_links", {})
            if not links.get("webui"):
                raise ValueError(f"page {reference} has no web link")
            return f"{links.get('base', f'{site}/wiki')}{links['webui']}"
        parts = urlparse(reference)
        if parts.scheme not in ("http", "https") or parts.netloc != host or not parts.path.startswith("/wiki/"):
            raise ValueError(f"{reference!r} is not a Confluence page URL on {host}; pass the page URL or its numeric id")
        return reference

    return resolve


def with_page_cards(adf: dict, urls: list[str]) -> dict:
    """Copy of `adf` with one smart-link card paragraph per page appended."""
    cards = [{"type": "paragraph", "content": [{"type": "inlineCard", "attrs": {"url": url}}]} for url in urls]
    return {**adf, "content": [*adf.get("content", []), *cards]}
