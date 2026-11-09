"""`map-markdown`: the single boundary for Markdown <-> Atlassian Document Format conversion.
Pure and offline; no filesystem, configuration, network, or Atlassian dependency.

Usage:
    atl.py map-markdown md-to-adf        < input.md   > output.json
    atl.py map-markdown adf-to-md        < input.json > output.md
    atl.py map-markdown detect-adf-only  < input.md   > report.json

Other commands call `md_to_adf`/`adf_to_md` in-process; both raise `ConversionError` carrying
the same `<reason>` the CLI prints as `error: <reason>`.
"""
from __future__ import annotations

import argparse
import json
import sys

from .converter.adf_to_md import adf_to_markdown
from .converter.detect import detect_adf_only
from .converter.md_to_adf import markdown_to_adf


class ConversionError(Exception):
    """The converter rejected its input; the message is the reason only, never a traceback."""


def md_to_adf(markdown: str) -> dict:
    try:
        return markdown_to_adf(markdown)
    except (ValueError, NotImplementedError) as exception:
        raise ConversionError(str(exception)) from None


def adf_to_md(doc: object) -> str:
    """ADF document -> Markdown, newline-terminated exactly like the CLI's stdout."""
    try:
        return adf_to_markdown(doc) + "\n"
    except (ValueError, NotImplementedError) as exception:
        raise ConversionError(str(exception)) from None


def main(argv: list[str] | None = None, *, prog: str | None = None) -> int:
    parser = argparse.ArgumentParser(prog=prog, description="Convert between Markdown and Atlassian Document Format.")
    subparsers = parser.add_subparsers(dest="direction", required=True)
    subparsers.add_parser("md-to-adf", help="Markdown (stdin) -> ADF JSON (stdout)")
    subparsers.add_parser("adf-to-md", help="ADF JSON (stdin) -> Markdown (stdout)")
    subparsers.add_parser("detect-adf-only", help="Markdown (stdin) -> ADF-only construct report (stdout)")
    args = parser.parse_args(argv)

    source = sys.stdin.read()

    try:
        if args.direction == "md-to-adf":
            doc = markdown_to_adf(source)
            json.dump(doc, sys.stdout, indent=2)
            sys.stdout.write("\n")
        elif args.direction == "detect-adf-only":
            constructs = detect_adf_only(source)
            json.dump({"adfOnly": bool(constructs), "constructs": constructs}, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            doc = json.loads(source)
            sys.stdout.write(adf_to_markdown(doc))
            sys.stdout.write("\n")
    except (ValueError, NotImplementedError) as exception:
        print(f"error: {exception}", file=sys.stderr)
        return 1

    return 0
