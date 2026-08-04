#!/usr/bin/env python3
"""Entry point for the `manage-backlog` "Label ticket" action.

Usage:
    python label_ticket.py <issue-number> <add-labels> <remove-labels>

Either <add-labels> or <remove-labels> may be an empty string.

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

_handler_module = importlib.import_module(f"{_PACKAGE_NAME}.features.label_ticket.handler")
label_ticket = _handler_module.label_ticket

_USAGE = "Usage: label_ticket.py <issue-number> <add-labels> <remove-labels>"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if len(argv) != 3:
        print(_USAGE, file=sys.stderr)
        return 1

    try:
        issue_number = int(argv[0])
    except ValueError:
        print(_USAGE, file=sys.stderr)
        return 1

    label_ticket(issue_number, argv[1], argv[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
