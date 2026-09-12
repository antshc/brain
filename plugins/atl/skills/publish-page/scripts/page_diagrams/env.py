"""Locate and parse `.atlassian` for the raw `site`/`email`/`token` this skill's attachment
upload needs — the one thing `preflight-atl`'s public contract deliberately never exposes (it
reports only `tokenAvailable`, a boolean, and never echoes the value). Bounded to `root`,
mirroring `preflight-atl`'s own config search — but this module is not imported across skill
folders; it exists only because the raw secret is out of scope for what Preflight may return.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from atlassian import Confluence

from . import renderers

CONFIG_FILENAME = ".atlassian"
DRAWIO_EXTENSION_KEY = "ATLASSIAN_DRAWIO_EXTENSION_KEY"

_EXTENSION_KEY_RE = re.compile(r"\A[^/\s]+/[^/\s]+/static/[^/\s]+\Z")


def find_config(root: str) -> str | None:
    root_path = Path(root).resolve()
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames.sort()
        if CONFIG_FILENAME in filenames:
            return str(Path(dirpath) / CONFIG_FILENAME)
    return None


def parse_config(path: str) -> dict[str, str]:
    values: dict[str, str] = {}
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_credentials(root: str) -> dict[str, str]:
    """Return `site`/`email`/`token`; raises `SystemExit` naming the missing key(s)."""
    path = find_config(root)
    config = parse_config(path) if path else {}
    site = config.get("ATLASSIAN_SITE", "").strip()
    email = config.get("ATLASSIAN_EMAIL", "").strip()
    token = config.get("ATLASSIAN_API_TOKEN", "").strip()
    missing = [
        name
        for name, value in (
            ("ATLASSIAN_SITE", site),
            ("ATLASSIAN_EMAIL", email),
            ("ATLASSIAN_API_TOKEN", token),
        )
        if not value
    ]
    if missing:
        raise SystemExit(f"error: .atlassian missing required key(s): {', '.join(missing)}")
    return {"site": site, "email": email, "token": token}


def site_url(credentials: dict[str, str]) -> str:
    """The configured site as an absolute URL, defaulting a bare host to `https://`."""
    site = credentials["site"].rstrip("/")
    if not site.startswith(("http://", "https://")):
        site = f"https://{site}"
    return site


def get_confluence(credentials: dict[str, str]) -> Confluence:
    return Confluence(
        url=site_url(credentials),
        username=credentials["email"],
        password=credentials["token"],
        cloud=True,
    )


def load_renderer(root: str) -> str:
    """Return the configured diagram renderer, defaulting to `png` when the key is absent.

    Unlike `load_credentials`, a missing `.atlassian` is not an error here — the default keeps
    existing repos publishing exactly as they did before the key existed.
    """
    path = find_config(root)
    config = parse_config(path) if path else {}
    name = config.get("ATLASSIAN_DIAGRAM_RENDERER", "").strip() or renderers.DEFAULT
    return renderers.validate(name)


def load_swimlane_drawio_enabled(root: str) -> bool:
    """Whether `ATLASSIAN_SWIMLANE_DRAWIO` opts into the native swimlane-beta-to-drawio
    converter; defaults to `False` so existing repos keep the PNG fallback until they opt in.
    """
    path = find_config(root)
    config = parse_config(path) if path else {}
    return config.get("ATLASSIAN_SWIMLANE_DRAWIO", "").strip().lower() in ("1", "true", "yes")


def load_drawio_extension_key(root: str) -> str:
    """Return the Draw.io Forge extension key; raise `ValueError` when absent or malformed.

    The key embeds the app id and the environment id, both of which differ per site and per
    install, so it cannot be hard-coded and has no usable default.
    """
    path = find_config(root)
    config = parse_config(path) if path else {}
    key = config.get(DRAWIO_EXTENSION_KEY, "").strip()
    if not key:
        raise ValueError(
            f"ATLASSIAN_DIAGRAM_RENDERER=drawio needs {DRAWIO_EXTENSION_KEY} in .atlassian; it embeds "
            "the Draw.io app id and environment id, which differ per site. To find it, read a page "
            "that already carries a Draw.io diagram with contentFormat=adf and copy the diagram "
            "node's attrs.extensionKey."
        )
    if not _EXTENSION_KEY_RE.match(key):
        raise ValueError(
            f"{DRAWIO_EXTENSION_KEY}={key!r} is malformed; expected <appId>/<envId>/static/drawio"
        )
    return key
