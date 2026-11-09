#!/usr/bin/env python3
"""Run the `twg` CLI with the REST credentials from `.atlassian.json.user`.

twg reads `TWG_USER`/`TWG_TOKEN`/`TWG_SITE` as per-process overrides, so the config's
`email`/`apiToken`/`cloudId` reach the twg child process only: never this process's
environment, never a command line. Both output streams are copied with the email and token
replaced by `<redacted>`; files twg writes via `--output-file` are not redacted.

Usage:
    python3 twg_cred.py [--config <configPath>] <twg arguments...>

`--config` defaults to `.atlassian.json.user` beside this skill's `SKILL.md`, resolved from
this file's location, not the cwd.
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
CONFIG_ERROR = "error: unreadable or malformed Atlassian config"


class ConfigError(Exception):
    """The config exists but cannot be read or parsed; the message never carries its values."""


def split_config_arg(args: list[str]) -> tuple[Path | None, list[str]]:
    """A leading `--config <path>` / `--config=<path>` -> (path, remaining twg args)."""
    if args and args[0] == "--config" and len(args) > 1:
        return Path(args[1]), args[2:]
    if args and args[0].startswith("--config="):
        return Path(args[0].removeprefix("--config=")), args[1:]
    return None, args


def load_config(config_path: Path) -> dict[str, object]:
    if not config_path.exists():
        return {}
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        raise ConfigError(CONFIG_ERROR) from None
    if not isinstance(config, dict):
        raise ConfigError(CONFIG_ERROR)
    return config


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
    explicit_config, args = split_config_arg(sys.argv[1:] if argv is None else argv)
    try:
        config = load_config(explicit_config or config_path)
    except ConfigError as exception:
        print(exception, file=sys.stderr)
        return 1
    binary = find_twg()
    if binary is None:
        print("error: twg CLI not found", file=sys.stderr)
        return MISSING_TWG_EXIT_CODE
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
