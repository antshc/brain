"""Verify that the configured Confluence credentials can read the Test page."""
from __future__ import annotations

import base64
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

PAGE_ID = "131406"


def require_environment(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"error: required environment variable is missing: {name}")
    return value


def confluence_api_url(site_url: str, page_id: str) -> str:
    site = urlsplit(site_url.strip())
    if site.scheme not in {"https", "http"} or not site.netloc:
        raise ValueError("ATLASSIAN_SITE_URL must be an absolute HTTP(S) URL")

    path = site.path.rstrip("/")
    if path.endswith("/wiki"):
        path = path[: -len("/wiki")]
    return urlunsplit((site.scheme, site.netloc, f"{path}/wiki/api/v2/pages/{page_id}", "body-format=storage", ""))


def get_page(site_url: str, email: str, token: str, page_id: str = PAGE_ID) -> dict:
    credentials = base64.b64encode(f"{email}:{token}".encode()).decode()
    request = Request(
        confluence_api_url(site_url, page_id),
        headers={"Accept": "application/json", "Authorization": f"Basic {credentials}"},
    )
    with urlopen(request, timeout=30) as response:  # noqa: S310 - URL comes from repository config
        return json.load(response)


def main() -> None:
    try:
        page = get_page(
            require_environment("ATLASSIAN_SITE_URL"),
            require_environment("ATLASSIAN_EMAIL"),
            require_environment("ATLASSIAN_API_TOKEN"),
        )
    except HTTPError as error:
        raise SystemExit(f"error: Confluence page request failed with HTTP {error.code}") from error
    except URLError as error:
        raise SystemExit(f"error: Confluence page request could not be completed: {error.reason}") from error
    except ValueError as error:
        raise SystemExit(f"error: {error}") from error

    print(f"Confluence page read succeeded: id={page['id']}, title={page['title']}")


if __name__ == "__main__":
    main()
