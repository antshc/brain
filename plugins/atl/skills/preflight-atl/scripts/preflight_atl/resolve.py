"""Resolve the offline Preflight facts from `.harness.json.user`'s `atl` section — never echoes a secret.

`mcpConnected` and instance-identifier discovery (when no site is configured) require a
live MCP call, which this module deliberately does not make — see SKILL.md Steps 2-3.
"""
from __future__ import annotations

from .config import load_config


def _first_entry(values: list[str] | None) -> str:
    for item in values or []:
        item = str(item).strip()
        if item:
            return item
    return ""


def derive_cloud_id(site: str) -> str:
    """`cloudId` is the configured site, prefixed with `https://` unless it already has a scheme."""
    if not site:
        return ""
    if site.startswith("http://") or site.startswith("https://"):
        return site
    return f"https://{site}"


def resolve(root: str) -> dict:
    """Return the config-derived subset of the eight-field Preflight shape.

    `mcpConnected` always comes back `False` here — only a live MCP call may set it `True`.
    `accountId`/`displayName` come from a prior `/init-atl` cache when present, empty otherwise —
    a live `atlassianUserInfo` call is the only other way to populate them (see SKILL.md Step 3).
    """
    config = load_config(root)
    site = str(config.get("site", "")).strip()
    token = str(config.get("api_token", "")).strip()
    return {
        "site": site,
        "cloudId": derive_cloud_id(site),
        "defaultProjectKey": _first_entry(config.get("jira_project_keys")),
        "defaultSpaceId": _first_entry(config.get("confluence_space_ids")),
        "tokenAvailable": bool(token),
        "mcpConnected": False,
        "accountId": str(config.get("account_id", "")).strip(),
        "displayName": str(config.get("display_name", "")).strip(),
    }
