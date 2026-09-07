"""Resolve the offline Preflight facts from `.atlassian` — never echoes a secret.

`mcpConnected` and instance-identifier discovery (when no site is configured) require a
live MCP call, which this module deliberately does not make — see SKILL.md Steps 2-3.
"""
from __future__ import annotations

from .config import load_config


def _first_entry(csv: str) -> str:
    for item in csv.split(","):
        item = item.strip()
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
    """Return the config-derived subset of the six-field Preflight shape.

    `mcpConnected` always comes back `False` here — only a live MCP call may set it `True`.
    """
    config = load_config(root)
    site = config.get("ATLASSIAN_SITE", "").strip()
    token = config.get("ATLASSIAN_API_TOKEN", "").strip()
    return {
        "site": site,
        "cloudId": derive_cloud_id(site),
        "defaultProjectKey": _first_entry(config.get("ATLASSIAN_JIRA_PROJECT_KEYS", "")),
        "defaultSpaceId": _first_entry(config.get("ATLASSIAN_CONFLUENCE_SPACE_IDS", "")),
        "tokenAvailable": bool(token),
        "mcpConnected": False,
    }
