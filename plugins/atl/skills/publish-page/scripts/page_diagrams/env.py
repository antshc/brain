"""Locate and parse `atl` + `credentials.atl` from `.harness.json.user` for the raw `site`/`email`/`token`
this skill's attachment upload needs — the one thing `preflight-atl`'s public contract deliberately
never exposes (it reports only `tokenAvailable`, a boolean, and never echoes the value). Read at
the fixed path `<root>/.harness.json.user`, mirroring `preflight-atl`'s own resolution — but this
module is not imported across skill folders; it exists only because the raw secret is out of scope
for what Preflight may return.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from atlassian import Confluence

from . import renderers

CONFIG_FILENAME = ".harness.json.user"
DRAWIO_EXTENSION_KEY = "drawio_extension_key"

_EXTENSION_KEY_RE = re.compile(r"\A[^/\s]+/[^/\s]+/static/[^/\s]+\Z")


def load_settings(root: str) -> dict:
    path = Path(root) / CONFIG_FILENAME
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    atl = data.get("atl") or {}
    atl_credentials = (data.get("credentials") or {}).get("atl") or {}
    return {**atl, **atl_credentials}


def load_credentials(root: str) -> dict[str, str]:
    """Return `site`/`email`/`token`; raises `SystemExit` naming the missing key(s)."""
    config = load_settings(root)
    site = str(config.get("site", "")).strip()
    email = str(config.get("email", "")).strip()
    token = str(config.get("api_token", "")).strip()
    missing = [
        name
        for name, value in (
            ("atl.site", site),
            ("credentials.atl.email", email),
            ("credentials.atl.api_token", token),
        )
        if not value
    ]
    if missing:
        raise SystemExit(f"error: .harness.json.user missing required key(s): {', '.join(missing)}")
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

    Unlike `load_credentials`, a missing `.harness.json.user` is not an error here — the default
    keeps existing repos publishing exactly as they did before the key existed.
    """
    config = load_settings(root)
    name = str(config.get("diagram_renderer", "")).strip() or renderers.DEFAULT
    return renderers.validate(name)


def load_swimlane_drawio_enabled(root: str) -> bool:
    """Whether `swimlane_drawio` opts into the native swimlane-beta-to-drawio
    converter; defaults to `True`, opting out only on an explicit falsy value.
    """
    config = load_settings(root)
    value = str(config.get("swimlane_drawio", "")).strip().lower()
    if not value:
        return True
    return value not in ("0", "false", "no")


def load_drawio_extension_key(root: str) -> str:
    """Return the Draw.io Forge extension key; raise `ValueError` when absent or malformed.

    The key embeds the app id and the environment id, both of which differ per site and per
    install, so it cannot be hard-coded and has no usable default.
    """
    config = load_settings(root)
    key = str(config.get(DRAWIO_EXTENSION_KEY, "")).strip()
    if not key:
        raise ValueError(
            f"diagram_renderer=drawio needs atl.{DRAWIO_EXTENSION_KEY} in .harness.json.user; it embeds "
            "the Draw.io app id and environment id, which differ per site. To find it, read a page "
            "that already carries a Draw.io diagram with contentFormat=adf and copy the diagram "
            "node's attrs.extensionKey."
        )
    if not _EXTENSION_KEY_RE.match(key):
        raise ValueError(
            f"atl.{DRAWIO_EXTENSION_KEY}={key!r} is malformed; expected <appId>/<envId>/static/drawio"
        )
    return key
