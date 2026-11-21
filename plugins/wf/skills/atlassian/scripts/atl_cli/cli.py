"""Root dispatcher for `atl.py`, the single Atlassian entry point. Each atl command lives in its
own module and is imported only when selected, so `map-markdown`, `publish-page check-anchors`,
and twg passthrough run without `atlassian-python-api`.

Any other command is a twg command: Markdown page and work-item body commands are routed to the
atl commands (`twg/overrides.py`); everything else runs on twg with the config's credentials
(`twg/runner.py`).
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
from collections.abc import Callable
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .twg.overrides import Delegate

PROG = "atl.py"
NATIVE = "--native"
CONFIG_ACTIONS: dict[str, set[str] | None] = {
    "fetch-work": None,
    "fetch-page": None,
    "doctor": None,
    "rename-page": None,
    "copy-page": None,
    "publish-work": {"create", "update", "read-adf"},
    "publish-page": {"run", "verify", "render-attach", "publish-adf"},
}


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


def _doctor(argv: list[str], prog: str) -> int | None:
    from .doctor import main

    return main(argv, prog=prog)


def _rename_page(argv: list[str], prog: str) -> int | None:
    from .page_operations import main

    return main(argv, prog=prog)


def _copy_page(argv: list[str], prog: str) -> int | None:
    from .copy_page import main

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
    "doctor": Command("Inspect Python packages, CLIs, and configured interpreter", _doctor),
    "rename-page": Command("Rename a page with a live REST body/version snapshot", _rename_page),
    "copy-page": Command("Clone one page to another and verify the semantic result", _copy_page),
}


TWG_EPILOG = """\
Any other <command> is a twg command, run with the --config credentials and redacted output.
Markdown is the default body format; these twg commands are routed to the commands above:
  confluence content get <page> [--format md] --output-file <page.md>     -> fetch-page
  confluence content create --content-type page --body[-file] ...        -> publish-page run
  confluence content update <page> --body[-file] ...                     -> publish-page run
  jira workitem get <KEY> --output-file <work.md>                        -> fetch-work
  jira workitem create|update --description[-file] ...                   -> publish-work
An explicit html/plain format, --edits, or structured output (-o json, --select, --fields,
--comments, --full) runs on twg unchanged. --native always runs raw twg."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Single Atlassian entry point: body operations over REST + ADF, everything else on twg. "
        "Run `atl.py <command> --help` for a command's options.",
        epilog=TWG_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--config", metavar="<configPath>", help="`.atlassian.json.user` path; passed to atl commands and injected into twg")
    parser.add_argument(NATIVE, action="store_true", help="Run the twg command as-is, without Markdown overrides")
    sub = parser.add_subparsers(dest="command", metavar="<command>", required=True)
    for name, command in COMMANDS.items():
        sub.add_parser(name, help=command.summary, add_help=False)
    return parser


def split_globals(args: list[str]) -> tuple[Path | None, bool, list[str]]:
    """Leading `--config <path>` / `--config=<path>` / `--native` -> (config, native, remaining args)."""
    config: Path | None = None
    native = False
    while args:
        if args[0] == "--config" and len(args) > 1:
            config, args = Path(args[1]), args[2:]
        elif args[0].startswith("--config="):
            config, args = Path(args[0].removeprefix("--config=")), args[1:]
        elif args[0] == NATIVE:
            native, args = True, args[1:]
        else:
            break
    return config, native, args


def with_config(name: str, rest: list[str], config: Path | None) -> list[str]:
    """Append the leading `--config` to an atl command that takes one and was not given one."""
    if config is None or name not in CONFIG_ACTIONS:
        return rest
    if any(token in ("-h", "--help", "--config") or token.startswith("--config=") for token in rest):
        return rest
    actions = CONFIG_ACTIONS[name]
    if actions is not None and (not rest or rest[0] not in actions):
        return rest
    return [*rest, "--config", str(config)]


def _resolver(config: dict[str, object], workdir: Path) -> Callable[[list[str]], dict]:
    from .twg import runner
    from .twg.overrides import ResolveError

    def resolve(args: list[str]) -> dict:
        output = workdir / "resolve.json"
        output.unlink(missing_ok=True)
        result = runner.call_twg([*args, "-o", "json", "--output-file", str(output)], config)
        payload = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}
        if result.returncode != 0 or payload.get("ok") is False:
            detail = (payload.get("error") or {}).get("message") or result.stderr.decode("utf-8", "replace").strip()
            raise ResolveError(f"twg {' '.join(args[:3])} failed (exit {result.returncode}){': ' + detail if detail else ''}")
        return payload

    return resolve


def _run_delegate(delegate: Delegate, config_path: Path, config: dict[str, object], workdir: Path) -> int:
    from .twg import runner

    argv = [*delegate.argv, "--config", str(config_path)]
    command = COMMANDS[delegate.command]
    prog = f"{PROG} {delegate.command}"
    if not delegate.publishes:
        return command.run(argv, prog) or 0
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            code = command.run(argv, prog) or 0
    except SystemExit:
        sys.stdout.write(buffer.getvalue())
        raise
    try:
        result = json.loads(buffer.getvalue())
    except json.JSONDecodeError:
        sys.stdout.write(buffer.getvalue())
        return code
    # Inline bodies publish from the temp workdir, which is gone once this command returns.
    for name in ("adfPath", "manifestPath"):
        if str(result.get(name, "")).startswith(str(workdir)):
            del result[name]
    if delegate.follow_up and code == 0:
        key = result["key"]
        follow_up = ["jira", "workitem", "update", "--id", key, *delegate.follow_up]
        try:
            completed = runner.call_twg(follow_up, config)
        except runner.TwgNotFoundError as exception:
            print(exception, file=sys.stderr)
            completed = None
        exit_code = completed.returncode if completed else runner.MISSING_TWG_EXIT_CODE
        if completed:
            sys.stderr.buffer.write(completed.stdout + completed.stderr)
            sys.stderr.flush()
        result["followUp"] = {"command": "jira workitem update", "exitCode": exit_code}
        if exit_code:
            print(
                f"error: {key} was published but the remaining twg fields failed; retry only them with "
                f"`atl.py jira workitem update --id {key} {' '.join(delegate.follow_up)}`",
                file=sys.stderr,
            )
            code = exit_code
    text = json.dumps(result)
    if delegate.output_file:
        Path(delegate.output_file).write_text(text + "\n", encoding="utf-8")
    print(text)
    return code


def run_twg_command(args: list[str], config_path: Path | None, *, native: bool) -> int:
    from .twg import overrides, runner

    try:
        config = runner.load_config(config_path)
    except runner.ConfigError as exception:
        print(exception, file=sys.stderr)
        return 1
    if native:
        return runner.run_twg(args, config)
    with tempfile.TemporaryDirectory(prefix="atl-") as workdir:
        context = overrides.Context(workdir=Path(workdir), resolve=_resolver(config, Path(workdir)))
        try:
            delegate = overrides.plan(args, context)
        except overrides.OverrideError as exception:
            print(f"error: {exception}", file=sys.stderr)
            return 2
        except overrides.ResolveError as exception:
            print(f"error: {exception}", file=sys.stderr)
            return 1
        except runner.TwgNotFoundError as exception:
            print(exception, file=sys.stderr)
            return runner.MISSING_TWG_EXIT_CODE
        if delegate is None:
            return runner.run_twg(args, config)
        if config_path is None:
            print(f"error: `{PROG} --config <configPath>` is required for Markdown body commands", file=sys.stderr)
            return 2
        return _run_delegate(delegate, config_path, config, Path(workdir))


def main(argv: list[str] | None = None) -> int:
    config, native, args = split_globals(list(sys.argv[1:] if argv is None else argv))
    if not args or args[0] in ("-h", "--help"):
        build_parser().parse_args(args)
        return 2
    if args[0] in COMMANDS and not native:
        name, rest = args[0], args[1:]
        return COMMANDS[name].run(with_config(name, rest, config), f"{PROG} {name}") or 0
    if NATIVE in args:
        native, args = True, [token for token in args if token != NATIVE]
    return run_twg_command(args, config, native=native)
