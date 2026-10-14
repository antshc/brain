#!/usr/bin/env python3
"""Entry point for fetching actionable issues for a repository."""

from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from github.features.fetch_issues.handler import fetch_issues

_USAGE = "Usage: fetch_issues.py <owner>/<repo> [--spec <number>]"
_REPOSITORY_RE = re.compile(r"^[^/]+/[^/]+$")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if not argv:
        print(_USAGE, file=sys.stderr)
        return 1

    repository = argv[0]
    if not _REPOSITORY_RE.match(repository):
        print(
            f"Error: Invalid repository. Expected <owner>/<repo>, got: {repository}",
            file=sys.stderr,
        )
        return 1
    owner, repo = repository.split("/", 1)

    options: dict[str, str] = {}
    if len(argv[1:]) % 2:
        print(_USAGE, file=sys.stderr)
        return 1
    for option, value in zip(argv[1::2], argv[2::2]):
        if option != "--spec" or option in options:
            print(_USAGE, file=sys.stderr)
            return 1
        options[option] = value
    spec = options.get("--spec")
    if spec is not None and not spec.isdecimal():
        print(_USAGE, file=sys.stderr)
        return 1

    print(json.dumps(fetch_issues(owner, repo, spec_number=int(spec) if spec else None), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
