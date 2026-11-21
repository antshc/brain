"""Runtime diagnostics for the Atlassian skill."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from importlib import metadata
from pathlib import Path

from .config import MIN_VERSION, _version_tuple, load_config

_PACKAGES = ("atlassian-python-api", "requests", "pymarkdownlnt")
_COMMANDS = ("twg", "mmdc", "drawio")


def _package_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def inspect_runtime(config_path: str | None = None) -> dict:
    config = load_config(config_path) if config_path else {}
    configured_python = str(config.get("pythonPath", "")).strip()
    packages = {name: _package_version(name) for name in _PACKAGES}
    commands = {name: shutil.which(name) for name in _COMMANDS}
    package_missing = [name for name, version in packages.items() if version is None]
    atlassian_version = packages["atlassian-python-api"]
    compatible = atlassian_version is not None and _version_tuple(atlassian_version) >= _version_tuple(MIN_VERSION)
    problems: list[str] = []
    if package_missing:
        problems.append("missing Python packages: " + ", ".join(package_missing))
    if not compatible:
        problems.append(f"atlassian-python-api >={MIN_VERSION} is required")
    return {
        "ok": not problems,
        "pythonExecutable": sys.executable,
        "configuredPython": configured_python or None,
        "packages": packages,
        "commands": commands,
        "twgAvailable": commands["twg"] is not None,
        "installCommand": f"{sys.executable} -m pip install -r {Path(__file__).resolve().parents[1] / 'requirements.txt'}",
        "problems": problems,
    }


def main(argv: list[str] | None = None, *, prog: str | None = None) -> int:
    parser = argparse.ArgumentParser(prog=prog, description="Inspect the Atlassian skill runtime.")
    parser.add_argument("--config")
    args = parser.parse_args(argv)
    report = inspect_runtime(args.config)
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if report["ok"] else 1
