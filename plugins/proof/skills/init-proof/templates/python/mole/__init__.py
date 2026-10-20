"""Loads the repository's .env before the app config is read, so PROOF_URL and friends can live there."""

from __future__ import annotations

import os
from pathlib import Path


def _load_env(path: Path) -> None:
    try:
        text = path.read_text()
    except FileNotFoundError:
        return
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key.strip().removeprefix("export ").strip(), value)


_load_env(Path(__file__).resolve().parents[1] / ".env")
