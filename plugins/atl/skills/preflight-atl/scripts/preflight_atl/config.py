"""Locate and parse the `atl` + `credentials.atl` sections of `.harness.json.user`.

The settings file lives at exactly `<root>/.harness.json.user` — never searched for,
never walked up or down from an ancestor/descendant directory.
"""
from __future__ import annotations

import json
from pathlib import Path

CONFIG_FILENAME = ".harness.json.user"


def config_path(root: str) -> Path:
    """Return the fixed settings-file path beneath root.

    Raises ValueError for a blank root — callers must resolve HARNESS_REPO_PATH first.
    """
    if not root or not root.strip():
        raise ValueError("root is required — resolve HARNESS_REPO_PATH before reading .harness.json.user")
    return Path(root) / CONFIG_FILENAME


def load_config(root: str) -> dict:
    """Read `atl` merged with `credentials.atl`; an absent file or section yields {}."""
    path = config_path(root)
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    atl = data.get("atl") or {}
    atl_credentials = (data.get("credentials") or {}).get("atl") or {}
    return {**atl, **atl_credentials}
