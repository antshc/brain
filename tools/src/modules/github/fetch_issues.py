#!/usr/bin/env python3
"""Entry point for fetching actionable issues for a repository."""

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from github.features.fetch_issues.handler import fetch_issues

_USAGE = "Usage: fetch_issues.py <owner>/<repo> [--milestone <title>]"
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

    milestone_title: str | None = None
    if len(argv) == 1:
        pass
    elif len(argv) == 3 and argv[1] == "--milestone":
        milestone_title = argv[2]
    else:
        print(_USAGE, file=sys.stderr)
        return 1

    print(json.dumps(fetch_issues(owner, repo, milestone_title=milestone_title), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
