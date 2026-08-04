#!/usr/bin/env python3
"""Entry point for the `manage-backlog` "Close ticket" action.

Usage:
    python close_ticket.py <issue-number> <comment>

<comment> may be an empty string to close without a closing comment.

Output (stdout):
    nothing.

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

_handler_module = importlib.import_module(f"{_PACKAGE_NAME}.features.close_ticket.handler")
close_ticket = _handler_module.close_ticket

_USAGE = "Usage: close_ticket.py <issue-number> <comment>"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if len(argv) != 2:
        print(_USAGE, file=sys.stderr)
        return 1

    try:
        issue_number = int(argv[0])
    except ValueError:
        print(_USAGE, file=sys.stderr)
        return 1

    close_ticket(issue_number, argv[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
