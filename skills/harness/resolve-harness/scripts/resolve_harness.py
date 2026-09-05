#!/usr/bin/env python3
"""Resolve Harness Settings from the nearest ancestor .harness.env file."""

from pathlib import Path
import sys


CONFIG_FILE_NAME = ".harness.env"
HARNESS_ROOT_KEY = "HARNESS_REPO_PATH"


def find_config_path(start_directory: Path) -> Path | None:
    current_directory = start_directory.resolve()
    while True:
        config_path = current_directory / CONFIG_FILE_NAME
        if config_path.is_file():
            return config_path
        if current_directory.parent == current_directory:
            return None
        current_directory = current_directory.parent


def parse_settings(config_path: Path) -> list[tuple[str, str]]:
    settings: list[tuple[str, str]] = []
    for line_number, line in enumerate(config_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Invalid setting in {config_path} at line {line_number}: expected KEY=value")
        key, value = line.split("=", 1)
        if not key:
            raise ValueError(f"Invalid setting in {config_path} at line {line_number}: key is empty")
        settings.append((key, value))
    return settings


def main() -> int:
    config_path = find_config_path(Path.cwd())
    if config_path is None:
        print(f"{HARNESS_ROOT_KEY}=")
        print("No .harness.env found; fall back to the current directory.", file=sys.stderr)
        return 0

    try:
        settings = parse_settings(config_path)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1

    harness_root = next((value for key, value in settings if key == HARNESS_ROOT_KEY), None)
    if harness_root is None or not harness_root:
        print(f"Invalid harness configuration {config_path}: HARNESS_REPO_PATH is required.", file=sys.stderr)
        return 1

    for key, value in settings:
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())