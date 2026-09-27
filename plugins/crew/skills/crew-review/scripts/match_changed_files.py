#!/usr/bin/env python3
"""Map changed files to installed Codey stacks for Chorey's review rules."""
from __future__ import annotations

import json
import sys
from fnmatch import fnmatch
from pathlib import Path


def match_files(paths: list[str], scopes: dict[str, list[str]]) -> dict[str, list[str]]:
    detail: dict[str, list[str]] = {}
    for stack, patterns in sorted(scopes.items()):
        matched = []
        for path in paths:
            normalized = path.replace("\\", "/")
            name = normalized.rsplit("/", 1)[-1]
            if any(fnmatch(normalized, pattern) or fnmatch(name, pattern) for pattern in patterns):
                matched.append(path)
        if matched:
            detail[stack] = matched
    return detail


def main(paths: list[str]) -> None:
    script_dir = Path(__file__).resolve().parent
    scopes = json.loads((script_dir / "review_scopes.json").read_text(encoding="utf-8"))
    agents_dir = script_dir.parents[2] / "agents"
    installed = {path.name.removeprefix("codey-").removesuffix(".agent.md") for path in agents_dir.glob("codey-*.agent.md")}
    if set(scopes) != installed or any(not patterns for patterns in scopes.values()):
        raise ValueError("Review scopes must cover every installed Codey agent exactly once")
    print(json.dumps(match_files(paths, scopes)))


if __name__ == "__main__":
    main(sys.argv[1:])
