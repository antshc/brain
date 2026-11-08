"""The one place this skill builds its Confluence client and fixes the REST base path.

The client's base URL is always `<site>/wiki`, so every raw path (`/api/v2/...`,
`/rest/api/...`, `/download/...`) resolves under `<site>/wiki/...`. `atlassian-python-api`
5.x stopped appending `/wiki` itself; it is explicit here instead.

Skill-local copy (Concept 0009); `publish-page` keeps its own.
"""
from __future__ import annotations

import re
from importlib import metadata
from typing import Any

LIBRARY = "atlassian-python-api"
MIN_VERSION = "5.0.5"
MAX_VERSION: str | None = None


def _version_tuple(version: str) -> tuple[int, int, int]:
    parts = []
    for piece in version.split(".")[:3]:
        digits = re.match(r"\d+", piece)
        parts.append(int(digits.group()) if digits else 0)
    parts += [0] * (3 - len(parts))
    return parts[0], parts[1], parts[2]


def supported_range() -> str:
    return f"{MIN_VERSION}-{MAX_VERSION}" if MAX_VERSION else f">={MIN_VERSION}"


def installed_version() -> str | None:
    try:
        return metadata.version(LIBRARY)
    except metadata.PackageNotFoundError:
        return None


def version_error(found: str | None) -> str | None:
    """The user-facing message when `found` is outside the supported range, else `None`."""
    supported = found is not None and _version_tuple(found) >= _version_tuple(MIN_VERSION)
    if supported and MAX_VERSION is not None:
        supported = _version_tuple(found) < _version_tuple(MAX_VERSION)
    if supported:
        return None
    return f"{LIBRARY} {supported_range()} required, found {found or 'none'}; follow Brain's plugins/atl/install/install.md in Copilot CLI"


def require_supported_library() -> None:
    message = version_error(installed_version())
    if message:
        raise SystemExit(message)


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
    require_supported_library()
    from atlassian import ConfluenceCloud

    return ConfluenceCloud(
        url=wiki_url(credentials["site"]),
        username=credentials["email"],
        password=credentials["token"],
    )
