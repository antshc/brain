#!/usr/bin/env python3
"""Create missing GitHub issue labels for the AFK/HITL task workflow."""

import subprocess
import sys

LABELS: list[tuple[str, str, str]] = [
    ("hitl", "fbca04", "Requires human implementation"),
    ("spec", "5319e7", "Spec task with implementation context"),
    ("wayfinder:map", "0e8a16", "Marks the map issue itself"),
    ("wayfinder:research", "1d76db", "Research-type decision ticket"),
    ("wayfinder:prototype", "5319e7", "Prototype-type decision ticket"),
    ("wayfinder:grilling", "fbca04", "Grilling-type decision ticket"),
    ("wayfinder:task", "d93f0b", "Manual-work decision ticket"),
]


def run_gh(args: list[str]) -> str:
    result = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def resolve_repo() -> str:
    return run_gh(["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]).strip()


def label_exists(repo: str, name: str) -> bool:
    output = run_gh(["label", "list", "--repo", repo, "--json", "name", "-q", ".[].name"])
    return name in output.splitlines()


def create_label_if_missing(repo: str, name: str, color: str, description: str) -> None:
    if label_exists(repo, name):
        print(f"exists:  {name}")
        return

    run_gh([
        "label", "create", name,
        "--repo", repo,
        "--color", color,
        "--description", description,
    ])
    print(f"created: {name}")


def main() -> int:
    try:
        repo = resolve_repo()
        for name, color, description in LABELS:
            create_label_if_missing(repo, name, color, description)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
