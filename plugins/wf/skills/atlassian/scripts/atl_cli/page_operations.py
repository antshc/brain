"""Focused Confluence page operations that keep REST semantics explicit."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from atlassian.errors import ApiError
from requests.exceptions import RequestException

from .config import load_credentials, require_supported_library, site_url
from .confluence_client import get_confluence
from .fetch_page.assemble_page import extract_title_and_body, parse_page_reference
from .page_diagrams.rest_publish import update_page_adf


def _read_page(confluence: Any, page_id: str) -> dict:
    return confluence.get(
        f"/api/v2/pages/{page_id}",
        params={"body-format": "atlas_doc_format"},
    )


def _version_changed(exception: BaseException) -> bool:
    return getattr(getattr(exception, "response", None), "status_code", None) == 409


def rename_page(confluence: Any, page_id: str, title: str, site: str) -> dict:
    original = _read_page(confluence, page_id)
    old_title, body = extract_title_and_body(original)
    if not isinstance(body, dict):
        raise ValueError("page body is not parsed ADF; refusing title update")
    version = int(original["version"]["number"])
    if title == old_title:
        return {
            "ok": True,
            "changed": False,
            "pageId": page_id,
            "title": title,
            "version": version,
            "url": f"{site}/wiki/pages/{page_id}",
        }
    try:
        update_page_adf(confluence, page_id, title, body, version)
    except RequestException as exception:
        if not _version_changed(exception):
            raise
        current = _read_page(confluence, page_id)
        current_title, current_body = extract_title_and_body(current)
        if current_title != old_title or not isinstance(current_body, dict) or current_body != body:
            raise RuntimeError("page changed concurrently during rename; refetch and retry") from None
        version = int(current["version"]["number"])
        update_page_adf(confluence, page_id, title, body, version)

    live = _read_page(confluence, page_id)
    if live.get("title") != title:
        raise RuntimeError(f"rename verification failed: expected {title!r}, found {live.get('title')!r}")
    return {
        "ok": True,
        "changed": True,
        "pageId": page_id,
        "title": title,
        "previousTitle": old_title,
        "version": int(live["version"]["number"]),
        "url": f"{site}/wiki/pages/{page_id}",
    }


def main(argv: list[str] | None = None, *, prog: str | None = None) -> int:
    parser = argparse.ArgumentParser(prog=prog, description="Rename a Confluence page safely.")
    parser.add_argument("page")
    parser.add_argument("--title", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--yes", action="store_true", help="Confirm an explicitly named title update")
    args = parser.parse_args(argv)
    if not args.yes:
        parser.error("--yes is required for rename-page")

    require_supported_library()
    credentials = load_credentials(args.config)
    if credentials is None:
        print("error: .atlassian.json.user needs cloudId, email, and apiToken to rename a page", file=sys.stderr)
        return 1
    try:
        page_id, reference_site = parse_page_reference(args.page)
        configured_site = site_url(credentials).rstrip("/")
        if reference_site and reference_site.rstrip("/") != configured_site:
            raise ValueError("page reference must use the configured Atlassian site")
        result = rename_page(get_confluence(credentials), page_id, args.title, configured_site)
    except (ApiError, RequestException, RuntimeError, ValueError) as exception:
        print(f"error: {exception}", file=sys.stderr)
        return 1
    json.dump(result, sys.stdout)
    sys.stdout.write("\n")
    return 0
