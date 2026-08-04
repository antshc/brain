#!/usr/bin/env python3
"""Entry point for the `manage-backlog` "Create ticket" action.

Usage:
    python create_ticket.py <title> <body> <milestone-title> <label>

Output (stdout):
    <issue-number>

Exit codes:
    0 - success
    1 - usage error
"""

import importlib
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR.parent))
_PACKAGE_NAME = _SCRIPT_DIR.name

_handler_module = importlib.import_module(f"{_PACKAGE_NAME}.features.create_ticket.handler")
create_ticket = _handler_module.create_ticket

_USAGE = "Usage: create_ticket.py <title> <body> <milestone-title> <label>"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if len(argv) != 4:
        print(_USAGE, file=sys.stderr)
        return 1

    title, body, milestone_title, label = argv
    issue_number = create_ticket(title, body, milestone_title, label)
    print(issue_number)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
