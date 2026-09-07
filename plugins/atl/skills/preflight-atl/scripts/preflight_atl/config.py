"""Locate and parse the `.atlassian` config file, bounded to the Harness Repo Path.

Search descends from `root` only — it never ascends past it and never reaches an
ancestor directory.
"""
from __future__ import annotations

import os
from pathlib import Path

CONFIG_FILENAME = ".atlassian"


def find_config(root: str) -> str | None:
    """Return the path to the first `.atlassian` file at or beneath root, or None."""
    root_path = Path(root).resolve()
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames.sort()
        if CONFIG_FILENAME in filenames:
            return str(Path(dirpath) / CONFIG_FILENAME)
    return None


def parse_config(path: str) -> dict[str, str]:
    """Parse `KEY=VALUE` lines; blank lines, `#` comments, and malformed lines are skipped."""
    values: dict[str, str] = {}
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_config(root: str) -> dict[str, str]:
    """Locate and parse the config; an absent file yields an empty dict, never an error."""
    path = find_config(root)
    if path is None:
        return {}
    return parse_config(path)
