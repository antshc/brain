"""CLI orchestration: prints the six-field Preflight shape as JSON. Offline only — no network."""
from __future__ import annotations

import argparse
import json

from .resolve import resolve


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve Atlassian Preflight facts from `.atlassian`.")
    parser.add_argument("--root", required=True, help="Harness Repo Path to bound the config search to")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    print(json.dumps(resolve(args.root)))


if __name__ == "__main__":
    main()
