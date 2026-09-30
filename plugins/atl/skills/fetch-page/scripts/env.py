"""Parse `.atlassian.json.user` for the raw `site`/`email`/`token` an attachment download needs.
The config path comes from `/preflight-atlassian`'s Locate command (`configPath`) — never
rebuilt or searched for here.

This is a fetch-side copy of `/publish-page`'s `page_diagrams/env.py`, trimmed to what a
read-only attachment download needs — never imported across skill folders (Concept 0009). It
differs from that copy in one deliberate way: a missing credential here is `/fetch-page`'s
degraded mode, not a hard failure, so `load_credentials` returns `None` instead of raising.
"""
from __future__ import annotations

import json
from pathlib import Path

from atlassian import Confluence

def load_config(config_path: str) -> dict:
    path = Path(config_path)
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_credentials(config_path: str) -> dict[str, str] | None:
    """Return `site`/`email`/`token`, or `None` when any is missing or the config is absent."""
    config = load_config(config_path)
    site = str(config.get("site", "")).strip()
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


def get_confluence(credentials: dict[str, str]) -> Confluence:
    return Confluence(
        url=site_url(credentials),
        username=credentials["email"],
        password=credentials["token"],
        cloud=True,
    )
