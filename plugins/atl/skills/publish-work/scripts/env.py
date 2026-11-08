"""Parse `.atlassian.json.user` for the raw `site`/`email`/`token` a Jira REST call needs.
The config path comes from `/preflight-atlassian`'s Locate command (`configPath`) — never
rebuilt or searched for here.

A publish-side copy of `/fetch-work`'s own `env.py` — never imported across skill folders
(Concept 0009). `load_credentials` returns `None` on a missing credential so the CLI can name it.
"""
from __future__ import annotations

import json
import re
from importlib import metadata
from pathlib import Path
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
    supported_range = f"{MIN_VERSION}-{MAX_VERSION}" if MAX_VERSION else f">={MIN_VERSION}"
    return f"{LIBRARY} {supported_range} required, found {found or 'none'}; follow Brain's plugins/atl/install/install.md in Copilot CLI"


def require_supported_library() -> None:
    message = version_error(installed_version())
    if message:
        raise SystemExit(message)


def load_config(config_path: str) -> dict:
    path = Path(config_path)
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_credentials(config_path: str) -> dict[str, str] | None:
    """Return `site`/`email`/`token`, or `None` when any is missing or the config is absent."""
    config = load_config(config_path)
    site = str(config.get("cloudId", "")).strip()  # config key is `cloudId`, not `site`
    email = str(config.get("email", "")).strip()
    token = str(config.get("apiToken", "")).strip()
    if not (site and email and token):
        return None
    return {"site": site, "email": email, "token": token}


def site_url(credentials: dict[str, str]) -> str:
    """The configured site as an absolute URL, defaulting a bare host to `https://`."""
    site = credentials["site"].rstrip("/")
    if not site.startswith(("http://", "https://")):
        site = f"https://{site}"
    return site


def get_jira(credentials: dict[str, str]) -> Any:
    require_supported_library()
    from atlassian import Jira

    return Jira(
        url=site_url(credentials),
        username=credentials["email"],
        password=credentials["token"],
        cloud=True,
    )
