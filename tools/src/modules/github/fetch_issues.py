#!/usr/bin/env python3
"""Entry point for fetching actionable open issues for an owner/repo.

Fetches open, actionable issues for a given GitHub repository and prints them
as a JSON array to stdout.

Usage:
    python3 fetch_issues.py <owner/repo>

Arguments:
    owner/repo  GitHub repository in "owner/repo" format, e.g. octocat/hello-world.

Output:
    JSON array of actionable issue objects printed to stdout:
        [
          {
            "number": 1,
            "title": "...",
            "body": "...",
            "url": "https://github.com/owner/repo/issues/1",
            "labels": ["ready"],
            "comments": [{"id": "...", "body": "...", "created_at": "..."}]
          },
          ...
        ]

Exit codes:
    0 - success (may output an empty array)
    1 - usage / argument error
"""

import json
import pathlib
import re
import sys

# Add the parent of the github/ folder to sys.path so "github" is importable
# regardless of where this file lives (tools/src/modules/ or any plugin copy).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from github.features.fetch_issues.handler import fetch_issues

_USAGE = "Usage: fetch_issues.py <owner/repo>"
_REPO_RE = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")


def main() -> None:
    if len(sys.argv) != 2:
        print(_USAGE, file=sys.stderr)
        sys.exit(1)

    owner_repo = sys.argv[1]

    if not _REPO_RE.match(owner_repo):
        print(
            f"Error: Invalid owner/repo format. Expected <owner>/<repo>, got: {owner_repo}",
            file=sys.stderr,
        )
        sys.exit(1)

    owner, repo = owner_repo.split("/", 1)
    issues = fetch_issues(owner, repo)
    print(json.dumps(issues, indent=2))


if __name__ == "__main__":
    main()
