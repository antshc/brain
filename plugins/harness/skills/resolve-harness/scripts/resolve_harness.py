#!/usr/bin/env python3
"""Resolve Harness Settings from the nearest ancestor .harness.json.user file."""

import json
from pathlib import Path
import sys


CONFIG_FILE_NAME = ".harness.json.user"
CREDENTIALS_KEY = "credentials"


def find_config_path(start_directory: Path) -> Path | None:
    current_directory = start_directory.resolve()
    while True:
        config_path = current_directory / CONFIG_FILE_NAME
        if config_path.is_file():
            return config_path
        if current_directory.parent == current_directory:
            return None
        current_directory = current_directory.parent


def main() -> int:
    config_path = find_config_path(Path.cwd())
    if config_path is None:
        print(json.dumps({"harnessRepoPath": "", "harness": {}, "atl": {}}))
        print("No .harness.json.user found; fall back to the current directory.", file=sys.stderr)
        return 0

    try:
        text = config_path.read_text(encoding="utf-8")
        data = json.loads(text) if text.strip() else {}
    except (OSError, json.JSONDecodeError) as error:
        print(f"Invalid harness configuration {config_path}: {error}", file=sys.stderr)
        return 1

    if not isinstance(data, dict):
        print(f"Invalid harness configuration {config_path}: expected a JSON object.", file=sys.stderr)
        return 1

    output = {key: value for key, value in data.items() if key != CREDENTIALS_KEY}
    output.setdefault("harness", {})
    output.setdefault("atl", {})
    print(json.dumps({"harnessRepoPath": str(config_path.parent), **output}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())