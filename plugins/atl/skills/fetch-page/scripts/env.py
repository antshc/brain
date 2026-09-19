"""Locate and parse `.atlassian` for the raw `site`/`email`/`token` an attachment download
needs — the one thing `preflight-atl`'s public contract deliberately never exposes (it reports
only `tokenAvailable`, a boolean, and never echoes the value). Bounded to `root`, mirroring
`preflight-atl`'s own config search.

This is a fetch-side copy of `/publish-page`'s `page_diagrams/env.py`, trimmed to what a
read-only attachment download needs — never imported across skill folders (Concept 0009). It
differs from that copy in one deliberate way: a missing credential here is `/fetch-page`'s
degraded mode, not a hard failure, so `load_credentials` returns `None` instead of raising.
"""
from __future__ import annotations

import os
from pathlib import Path

from atlassian import Confluence

CONFIG_FILENAME = ".atlassian"


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


def load_credentials(root: str) -> dict[str, str] | None:
    """Return `site`/`email`/`token`, or `None` when any is missing or `.atlassian` is absent."""
    path = find_config(root)
    config = parse_config(path) if path else {}
    site = config.get("ATLASSIAN_SITE", "").strip()
    email = config.get("ATLASSIAN_EMAIL", "").strip()
    token = config.get("ATLASSIAN_API_TOKEN", "").strip()
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
