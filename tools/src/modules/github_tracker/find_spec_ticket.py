#!/usr/bin/env python3
"""Entry point for the `manage-backlog` "Find spec ticket" action.

Finds the open `spec`-labeled issue assigned to <milestone-title>.

Usage:
    python find_spec_ticket.py <milestone-title>

Output (stdout):
    JSON object {"number", "title", "body", "comments"} if found, else JSON `null`.

Exit codes:
    0 - success (found or not found)
    1 - usage error
"""

import importlib
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR.parent))
_PACKAGE_NAME = _SCRIPT_DIR.name

_handler_module = importlib.import_module(f"{_PACKAGE_NAME}.features.find_spec_ticket.handler")
find_spec_ticket = _handler_module.find_spec_ticket

_USAGE = "Usage: find_spec_ticket.py <milestone-title>"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if len(argv) != 1:
        print(_USAGE, file=sys.stderr)
        return 1

    ticket = find_spec_ticket(argv[0])
    print(json.dumps(ticket))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
