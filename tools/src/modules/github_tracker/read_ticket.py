#!/usr/bin/env python3
"""Entry point for the `manage-backlog` "Read ticket" action.

Usage:
    python read_ticket.py <issue-number>

Output (stdout):
    JSON object {"number", "title", "body", "labels", "comments"}.

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

_handler_module = importlib.import_module(f"{_PACKAGE_NAME}.features.read_ticket.handler")
read_ticket = _handler_module.read_ticket

_USAGE = "Usage: read_ticket.py <issue-number>"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if len(argv) != 1:
        print(_USAGE, file=sys.stderr)
        return 1

    try:
        issue_number = int(argv[0])
    except ValueError:
        print(_USAGE, file=sys.stderr)
        return 1

    print(json.dumps(read_ticket(issue_number)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
