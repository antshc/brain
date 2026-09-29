"""Locate and parse `atl` + `credentials.atl` from `.harness.json.user` for the raw `site`/`email`/`token`
an attachment download needs — the one thing `preflight-atl`'s public contract deliberately never
exposes (it reports only `tokenAvailable`, a boolean, and never echoes the value). Read at the
fixed path `<root>/.harness.json.user`, mirroring `preflight-atl`'s own resolution.

This is a fetch-side copy of `/publish-page`'s `page_diagrams/env.py`, trimmed to what a
read-only attachment download needs — never imported across skill folders (Concept 0009). It
differs from that copy in one deliberate way: a missing credential here is `/fetch-page`'s
degraded mode, not a hard failure, so `load_credentials` returns `None` instead of raising.
"""
from __future__ import annotations

import json
from pathlib import Path

from atlassian import Confluence

CONFIG_FILENAME = ".harness.json.user"


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


def load_credentials(root: str) -> dict[str, str] | None:
    """Return `site`/`email`/`token`, or `None` when any is missing or the `atl` section is absent."""
    config = load_settings(root)
    site = str(config.get("site", "")).strip()
    email = str(config.get("email", "")).strip()
    token = str(config.get("api_token", "")).strip()
    if not (site and email and token):
        return None
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
