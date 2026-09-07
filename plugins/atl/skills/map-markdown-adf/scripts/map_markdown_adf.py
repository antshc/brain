#!/usr/bin/env python3
"""CLI: the single externally observable boundary for Markdown <-> Atlassian Document Format
conversion. Pure and offline — no filesystem, no configuration, no network.

Usage:
    map_markdown_adf.py md-to-adf < input.md   > output.json
    map_markdown_adf.py adf-to-md < input.json > output.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from converter.adf_to_md import adf_to_markdown  # noqa: E402
from converter.md_to_adf import markdown_to_adf  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert between Markdown and Atlassian Document Format.")
    subparsers = parser.add_subparsers(dest="direction", required=True)
    subparsers.add_parser("md-to-adf", help="Markdown (stdin) -> ADF JSON (stdout)")
    subparsers.add_parser("adf-to-md", help="ADF JSON (stdin) -> Markdown (stdout)")
    args = parser.parse_args(argv)

    source = sys.stdin.read()

    try:
        if args.direction == "md-to-adf":
            doc = markdown_to_adf(source)
            json.dump(doc, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            doc = json.loads(source)
            sys.stdout.write(adf_to_markdown(doc))
            sys.stdout.write("\n")
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
