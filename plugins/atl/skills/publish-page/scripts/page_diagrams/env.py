"""Locate and parse `.atlassian` for the raw `site`/`email`/`token` this skill's attachment
upload needs — the one thing `preflight-atl`'s public contract deliberately never exposes (it
reports only `tokenAvailable`, a boolean, and never echoes the value). Bounded to `root`, per
Concept 0008, mirroring `preflight-atl`'s own config search — but this module is not imported
across skill folders (Concept 0009); it exists only because the raw secret is out of scope for
what Preflight may return.
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


def get_confluence(credentials: dict[str, str]) -> Confluence:
    site = credentials["site"]
    if not site.startswith(("http://", "https://")):
        site = f"https://{site}"
    return Confluence(url=site, username=credentials["email"], password=credentials["token"], cloud=True)
