"""Env-file loading and Confluence client construction.

The only seam that touches credentials; kept tiny so it never needs mocking beyond a
tmp env file and a stub `Confluence` class.
"""
from __future__ import annotations

import re

from atlassian import Confluence


def load_env(env_path: str) -> dict:
    env = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k] = v.strip('"')
    for required in ("ACLI_SITE", "ACLI_EMAIL", "ACLI_API_TOKEN"):
        if not env.get(required):
            raise SystemExit(f"Missing or blank {required} in {env_path}")
    return env


def get_confluence(env: dict) -> Confluence:
    site = env["ACLI_SITE"]
    if not re.match(r"^https?://", site):
        site = "https://" + site
    return Confluence(url=site, username=env["ACLI_EMAIL"], password=env["ACLI_API_TOKEN"], cloud=True)
