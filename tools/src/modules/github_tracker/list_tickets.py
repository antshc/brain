#!/usr/bin/env python3
"""Entry point for the `manage-backlog` "List tickets" action.

Usage:
    python list_tickets.py <state> <label>

Output (stdout):
    JSON array of {"number", "title", "body", "labels", "comments"}.

Exit codes:
    0 - success
    1 - usage error
"""

import importlib
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR.parent))
_PACKAGE_NAME = _SCRIPT_DIR.name

_handler_module = importlib.import_module(f"{_PACKAGE_NAME}.features.list_tickets.handler")
list_tickets = _handler_module.list_tickets

_USAGE = "Usage: list_tickets.py <state> <label>"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if len(argv) != 2:
        print(_USAGE, file=sys.stderr)
        return 1

    state, label = argv
    print(json.dumps(list_tickets(state, label)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
