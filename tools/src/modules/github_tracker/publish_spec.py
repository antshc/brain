#!/usr/bin/env python3
"""Entry point for the `manage-backlog` "Publish spec" action.

Reuses (never renames) an existing capability milestone matching <feature-id>,
or creates one, then creates the spec issue and assigns it to that milestone.

Usage:
    python publish_spec.py <feature-id> <spec-title> <target-branch>

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

_handler_module = importlib.import_module(f"{_PACKAGE_NAME}.features.publish_spec.handler")
publish_spec = _handler_module.publish_spec

_USAGE = "Usage: publish_spec.py <feature-id> <spec-title> <target-branch>"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if len(argv) != 3:
        print(_USAGE, file=sys.stderr)
        return 1

    feature_id, spec_title, target_branch = argv
    issue_number = publish_spec(feature_id, spec_title, target_branch)
    print(issue_number)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
