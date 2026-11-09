"""The one place this skill builds its Confluence client and fixes the REST base path.

The client's base URL is always `<site>/wiki`, so every raw path (`/api/v2/...`,
`/rest/api/...`, `/download/...`) resolves under `<site>/wiki/...`. `atlassian-python-api`
5.x stopped appending `/wiki` itself; it is explicit here instead.

Shared by `fetch-page`, `publish-page`, and `verify`; the library version gate lives in
`config`.
"""
from __future__ import annotations

from typing import Any

from . import config
from .config import installed_version, version_error  # noqa: F401  re-exported for callers

def wiki_url(site: str) -> str:
    site = site.strip().rstrip("/")
    if not site.startswith(("http://", "https://")):
        site = f"https://{site}"
    return site if site.endswith("/wiki") else f"{site}/wiki"


_HINTS = {
    401: "check email/apiToken",
    403: "check email/apiToken",
    404: "check site URL and page id; wrong API base?",
}


def _status(exception: BaseException) -> int | None:
    response = getattr(exception, "response", None)
    return getattr(response, "status_code", None) if response is not None else None


def error_category(exception: BaseException) -> str:
    """Safe failure label: exception class plus HTTP status when known; never the exception text."""
    status = _status(exception)
    name = type(exception).__name__
    return f"{name} {status}" if status is not None else name


def error_hint(exception: BaseException) -> str | None:
    status = _status(exception)
    return _HINTS.get(status) if status is not None else None


def error_label(exception: BaseException) -> str:
    """`error_category`, plus a fixed hint for 401/403/404, e.g. `HTTPError 404: check ...`."""
    hint = error_hint(exception)
    category = error_category(exception)
    return f"{category}: {hint}" if hint else category


def get_confluence(credentials: dict[str, str]) -> Any:
    config.require_supported_library()
    from atlassian import ConfluenceCloud

    return ConfluenceCloud(
        url=wiki_url(credentials["site"]),
        username=credentials["email"],
        password=credentials["token"],
    )
