"""Root dispatcher for `atl.py`. Each command lives in its own module and is imported only when
selected, so `map-markdown` and `publish-page check-anchors` run offline without
`atlassian-python-api` or credentials.
"""
from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from dataclasses import dataclass

PROG = "atl.py"


def _fetch_work(argv: list[str], prog: str) -> int | None:
    from .fetch_work.assemble_work import main

    return main(argv, prog=prog)


def _publish_work(argv: list[str], prog: str) -> int | None:
    from .publish_work import main

    return main(argv, prog=prog)


def _fetch_page(argv: list[str], prog: str) -> int | None:
    from .fetch_page.assemble_page import main

    return main(argv, prog=prog)


def _publish_page(argv: list[str], prog: str) -> int | None:
    action = argv[0] if argv else None
    if action == "check-anchors":
        from .page_diagrams.anchor_check import main as check_anchors

        return check_anchors(argv[1:], prog=f"{prog} check-anchors")
    if action == "verify":
        from .verify_publish import main as verify

        return verify(argv[1:], prog=f"{prog} verify")
    if action not in (None, "-h", "--help"):
        from .config import require_supported_library

        require_supported_library()
    from .page_diagrams.cli import main

    return main(argv, prog=prog)


def _map_markdown(argv: list[str], prog: str) -> int | None:
    from .map_markdown import main

    return main(argv, prog=prog)


@dataclass(frozen=True)
class Command:
    summary: str
    run: Callable[[list[str], str], int | None]


COMMANDS: dict[str, Command] = {
    "fetch-work": Command("Fetch a Jira work item as Markdown with attachments (REST v3, ADF)", _fetch_work),
    "publish-work": Command("create | update | read-adf a Jira work item from Markdown or ADF", _publish_work),
    "fetch-page": Command("Fetch a Confluence page as Markdown with anchors, attachments, comments", _fetch_page),
    "publish-page": Command(
        "run | verify | check-anchors | extract | render-attach | substitute-media | replace-markers | publish-adf | combine",
        _publish_page,
    ),
    "map-markdown": Command("md-to-adf | adf-to-md | detect-adf-only; offline, no config", _map_markdown),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Atlassian body operations over REST + ADF. Run `atl.py <command> --help` for a command's options.",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>", required=True)
    for name, command in COMMANDS.items():
        sub.add_parser(name, help=command.summary, add_help=False)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] not in COMMANDS:
        build_parser().parse_args(args)
        return 2
    name, rest = args[0], args[1:]
    return COMMANDS[name].run(rest, f"{PROG} {name}") or 0
