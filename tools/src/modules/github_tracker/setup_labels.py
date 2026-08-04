#!/usr/bin/env python3
"""Entry point for the `manage-backlog` "Setup labels" action.

Creates any GitHub issue labels this repo's ticket tracker needs that are
missing. Resolves the repo the same way as the rest of this module
(`gh repo view --json nameWithOwner`), never via an unset shell variable.

Usage:
    python setup_labels.py

Output (stdout):
    One line per label in the catalog, in catalog order:
        exists:  <name>   (label already present, left unchanged)
        created: <name>   (label just created)

Exit codes:
    0 - success
"""

import importlib
import sys
from pathlib import Path

# This file is synced as-is (see .githooks/pre-commit) alongside its sibling
# domain/features/infrastructure/shared packages. That enclosing directory is
# named "github_tracker" in tools/src/modules/ but "scripts" once synced into
# the manage-backlog skill folder -- import the sibling packages by this
# directory's own runtime name rather than hardcoding one, since the two
# locations differ.
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR.parent))
_PACKAGE_NAME = _SCRIPT_DIR.name

_handler_module = importlib.import_module(f"{_PACKAGE_NAME}.features.setup_labels.handler")
setup_labels = _handler_module.setup_labels


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    for result in setup_labels():
        status = "created:" if result.created else "exists: "
        print(f"{status} {result.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
