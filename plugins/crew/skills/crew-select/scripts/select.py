#!/usr/bin/env python3
"""CLI: match changed file paths against installed Stack agents, print the result as JSON.

Usage: python3 select.py --agents-dir <path-to-agents/crew> [<changed-file> ...]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from crew_select.agents import discover_stack_agents  # noqa: E402
from crew_select.match import select_stacks  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents-dir", required=True)
    parser.add_argument("changed_files", nargs="*")
    args = parser.parse_args()

    stack_scopes = discover_stack_agents(Path(args.agents_dir))
    result = select_stacks(args.changed_files, stack_scopes)
    result["primaryAgent"] = f"codey-{result['primary']}" if result["primary"] else "codey"
    print(json.dumps(result))


if __name__ == "__main__":
    main()
