"""Parse `.atlassian.json.user` for the raw `site`/`email`/`token` a Jira REST call needs.
The config path comes from `/preflight-atlassian`'s Locate command (`configPath`) — never
rebuilt or searched for here.

A Jira-flavored copy of `/fetch-page`'s own `env.py` — never imported across skill folders
(Concept 0009). A missing credential here is `/fetch-work`'s degraded mode, not a hard failure,
so `load_credentials` returns `None` instead of raising.
"""
from __future__ import annotations

import json
from pathlib import Path

from atlassian import Jira

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


def get_jira(credentials: dict[str, str]) -> Jira:
    return Jira(
        url=site_url(credentials),
        username=credentials["email"],
        password=credentials["token"],
        cloud=True,
    )
