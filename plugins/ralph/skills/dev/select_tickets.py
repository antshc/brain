"""Select Ralph's queue from a paginated GitHub issues snapshot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def select_tickets(pages: list[list[dict[str, Any]]], kind: str) -> list[dict[str, Any]]:
    if not isinstance(pages, list) or any(not isinstance(page, list) for page in pages):
        raise ValueError("Expected the page array from gh api --paginate --slurp")
    selected = []
    for page in pages:
        for issue in page:
            if "pull_request" in issue or issue["state"] != "open":
                continue
            labels = {label["name"].casefold() for label in issue["labels"]}
            if labels & {"hitl", "spec"}:
                continue
            if ("tests" in labels) == (kind == "tests"):
                selected.append(issue)
    return sorted(selected, key=lambda issue: issue["number"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--kind", choices=("implementation", "tests"), required=True)
    args = parser.parse_args()
    pages = json.loads(args.snapshot.read_text(encoding="utf-8"))
    print(json.dumps(select_tickets(pages, args.kind), indent=2))


if __name__ == "__main__":
    main()
