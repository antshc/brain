#!/usr/bin/env python3
"""Run the `twg` CLI with the REST credentials from the sibling `.atlassian.json.user`.

twg reads `TWG_USER`/`TWG_TOKEN`/`TWG_SITE` as per-process overrides, so the config's
`email`/`apiToken`/`cloudId` reach twg without a separate `twg login` and never appear on a
command line. Config values never leave this process: both output streams are redacted.

Usage:
    python3 twg.py <twg arguments...>
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / ".atlassian.json.user"
REDACTED = b"<redacted>"
MISSING_TWG_EXIT_CODE = 127


def load_config(config_path: Path) -> dict[str, object]:
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def site_host(site: str) -> str:
    return site.strip().removeprefix("https://").removeprefix("http://").rstrip("/")


def credential_env(config: dict[str, object]) -> dict[str, str]:
    """twg overrides for the configured credentials; empty when `email` or `apiToken` is missing,
    leaving twg on its own saved login."""
    email = str(config.get("email", "")).strip()
    token = str(config.get("apiToken", "")).strip()
    site = site_host(str(config.get("cloudId", "")))
    env: dict[str, str] = {}
    if email and token:
        env["TWG_USER"] = email
        env["TWG_TOKEN"] = token
    if site:
        env["TWG_SITE"] = site
    return env


def find_twg(*, home: Path | None = None, local_app_data: str | None = None) -> str | None:
    found = shutil.which("twg")
    if found:
        return found
    home = home or Path.home()
    local_app_data = local_app_data if local_app_data is not None else os.environ.get("LOCALAPPDATA", "")
    candidates = [home / ".local" / "bin" / "twg"]
    if local_app_data:
        candidates.append(Path(local_app_data) / "Programs" / "twg" / "bin" / "twg.exe")
    return next((str(path) for path in candidates if path.is_file()), None)


def redact(data: bytes, secrets: list[str]) -> bytes:
    for secret in secrets:
        data = data.replace(secret.encode("utf-8"), REDACTED)
    return data


def main(argv: list[str] | None = None, *, config_path: Path = CONFIG_PATH) -> int:
    args = sys.argv[1:] if argv is None else argv
    binary = find_twg()
    if binary is None:
        print(
            "error: twg CLI not found on PATH or in its default install directory; install it, "
            "then rerun",
            file=sys.stderr,
        )
        return MISSING_TWG_EXIT_CODE
    config = load_config(config_path)
    secrets = [value for value in (str(config.get("email", "")).strip(), str(config.get("apiToken", "")).strip()) if value]
    result = subprocess.run(
        [binary, *args],
        env={**os.environ, **credential_env(config)},
        capture_output=True,
        check=False,
    )
    sys.stdout.buffer.write(redact(result.stdout, secrets))
    sys.stdout.flush()
    sys.stderr.buffer.write(redact(result.stderr, secrets))
    sys.stderr.flush()
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
