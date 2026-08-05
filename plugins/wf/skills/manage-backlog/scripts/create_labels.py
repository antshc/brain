#!/usr/bin/env python3
"""Create missing GitHub issue labels for the AFK/HITL task workflow."""

import subprocess
import sys

LABELS: list[tuple[str, str, str]] = [
    ("hitl", "fbca04", "Requires human implementation"),
    ("spec", "5319e7", "Spec task with implementation context"),
]


def resolve_repo() -> str:
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def label_exists(repo: str, name: str) -> bool:
    result = subprocess.run(
        ["gh", "label", "list", "--repo", repo, "--json", "name", "-q", ".[].name"],
        capture_output=True,
        text=True,
        check=True,
    )
    existing_names = result.stdout.splitlines()
    return name in existing_names


def create_label_if_missing(repo: str, name: str, color: str, description: str) -> None:
    if label_exists(repo, name):
        print(f"exists:  {name}")
        return

    subprocess.run(
        [
            "gh", "label", "create", name,
            "--repo", repo,
            "--color", color,
            "--description", description,
        ],
        check=True,
    )
    print(f"created: {name}")


def main() -> int:
    repo = resolve_repo()
    for name, color, description in LABELS:
        create_label_if_missing(repo, name, color, description)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
