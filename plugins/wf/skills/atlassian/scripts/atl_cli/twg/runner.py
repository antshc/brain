"""Run the `twg` CLI with the credentials from `.atlassian.json.user`.

twg reads `TWG_USER`/`TWG_TOKEN`/`TWG_SITE` as per-process overrides, so the config's
`email`/`apiToken`/`cloudId` reach the twg child process only: never this process's
environment, never a command line. Both output streams are copied with the email and token
replaced by `<redacted>`; files twg writes via `--output-file` are not redacted.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REDACTED = b"<redacted>"
MISSING_TWG_EXIT_CODE = 127
CONFIG_ERROR = "error: unreadable or malformed Atlassian config"
MISSING_TWG_ERROR = "error: twg CLI not found"


class ConfigError(Exception):
    """The config exists but cannot be read or parsed; the message never carries its values."""


class TwgNotFoundError(Exception):
    """No `twg` binary on PATH or in its default install directory."""


def load_config(config_path: Path | None) -> dict[str, object]:
    if config_path is None or not config_path.exists():
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


def secrets(config: dict[str, object]) -> list[str]:
    return [value for value in (str(config.get("email", "")).strip(), str(config.get("apiToken", "")).strip()) if value]


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


def redact(data: bytes, values: list[str]) -> bytes:
    for value in values:
        data = data.replace(value.encode("utf-8"), REDACTED)
    return data


def call_twg(args: list[str], config: dict[str, object]) -> subprocess.CompletedProcess[bytes]:
    """Run twg with injected credentials; stdout and stderr come back redacted."""
    binary = find_twg()
    if binary is None:
        raise TwgNotFoundError(MISSING_TWG_ERROR)
    result = subprocess.run(
        [binary, *args],
        env={**os.environ, **credential_env(config)},
        capture_output=True,
        check=False,
    )
    hidden = secrets(config)
    return subprocess.CompletedProcess(result.args, result.returncode, redact(result.stdout, hidden), redact(result.stderr, hidden))


def run_twg(args: list[str], config: dict[str, object]) -> int:
    """Forward `args` to twg, copy its redacted output to this process, and return its exit code."""
    try:
        result = call_twg(args, config)
    except TwgNotFoundError as exception:
        print(exception, file=sys.stderr)
        return MISSING_TWG_EXIT_CODE
    sys.stdout.buffer.write(result.stdout)
    sys.stdout.flush()
    sys.stderr.buffer.write(result.stderr)
    sys.stderr.flush()
    return result.returncode
