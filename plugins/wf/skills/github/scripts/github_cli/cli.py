from __future__ import annotations

import argparse
import json
import sys
from pathlib import PurePosixPath
from typing import Any, Callable
from urllib.parse import quote

from . import implement_spec, issues, pulls, reviews, specs

from .gh import Gh, GhError, UsageError, repository
from .pr_git import sha


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Brain Git and GitHub operations")
    groups = parser.add_subparsers(dest="group", required=True)
    nested = {
        group: groups.add_parser(group).add_subparsers(dest="action", required=True)
        for group in ("repo", "spec", "graph", "ticket", "issue", "label", "artifact", "pr", "review", "checks", "run")
    }

    def command(group: str | None, name: str, handler: Callable[..., dict[str, Any]]) -> argparse.ArgumentParser:
        sub = (groups if group is None else nested[group]).add_parser(name)
        sub.set_defaults(handler=handler)
        return sub

    for group in (None, "spec"):
        p = command(group, "preflight", implement_spec.cmd_preflight)
        p.add_argument("--spec")
        p.add_argument("--harness-root")
        p.add_argument("--source-repository")
        p.add_argument("--base-branch")
        p.add_argument("--initiative-id")
        p.add_argument("--mode", choices=("sequential", "parallel"), default="sequential")
        p.add_argument("--max-parallel", type=int)
        p.add_argument("--pin-base", action="store_true")
        p.add_argument("--integration-branch")

    p = command("run", "checkpoint", implement_spec.cmd_run_checkpoint)
    p.add_argument("--run-dir", required=True)
    p.add_argument("--input", required=True)

    p = command("spec", "create", specs.spec_create)
    for flag in ("source-repository", "base-branch", "initiative-id", "summary", "body-file"):
        p.add_argument(f"--{flag}", required=True)
    p.add_argument("--tracker-repository")
    p.add_argument("--source-note")
    p.add_argument("--profile", choices=("implement-spec", "design"), default="implement-spec")

    p = command("graph", "read", implement_spec.cmd_graph_read)
    p.add_argument("--spec", required=True)
    p.add_argument("--out", required=True)

    p = command("graph", "frontier", implement_spec.cmd_graph_frontier)
    p.add_argument("--graph", required=True)
    p.add_argument("--planner")
    p.add_argument("--out")
    p.add_argument("--done", action="extend", nargs="+", default=[])

    p = command("ticket", "create", implement_spec.cmd_ticket_create)
    for flag in ("spec", "title", "body-file"):
        p.add_argument(f"--{flag}", required=True)

    p = command("issue", "block", implement_spec.cmd_issue_block)
    p.add_argument("ref")
    p.add_argument("--by", action="extend", nargs="+", required=True)

    for name, handler in (("edit-body", implement_spec.cmd_issue_edit_body), ("comment", implement_spec.cmd_issue_comment)):
        p = command("issue", name, handler)
        p.add_argument("ref")
        p.add_argument("--body-file", required=True)
        if name == "comment":
            p.add_argument("--run-id")

    p = command("issue", "close", implement_spec.cmd_issue_close)
    p.add_argument("ref")
    for flag in ("commit", "branch", "pr", "comment", "run-id"):
        p.add_argument(f"--{flag}")
    p.add_argument("--evidence-comment", type=int)

    p = command("pr", "publish", implement_spec.cmd_pr_publish)
    for flag in ("source-repository", "base", "head", "title", "initiative-id", "rationale-file", "changes-file", "evidence-file"):
        p.add_argument(f"--{flag}", required=True)
    p.add_argument("--refs", action="extend", nargs="+", default=[])

    p = command("pr", "diff-split", pulls.pr_diff_split)
    p.add_argument("--pr", required=True)
    p.add_argument("--source-repository")
    p.add_argument("--expected")
    p.add_argument("--base")

    p = command("pr", "read", implement_spec.cmd_pr_read)
    p.add_argument("--source-repository", required=True)
    p.add_argument("--number", type=int)
    p.add_argument("--head")
    p.add_argument("--initiative-id")
    p.add_argument("--expect-refs", action="extend", nargs="+", default=[])
    register_commands(command, nested)
    return parser


def main(argv: list[str] | None = None, *, gh: Gh | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if hasattr(args, 'entry'):
            return args.entry(args)
        result = args.handler(gh or Gh(), args)
    except (UsageError, GhError) as exception:
        print(f"error: {exception}", file=sys.stderr)
        return exception.exit_code
    except (KeyError, TypeError, json.JSONDecodeError) as exception:
        print(f"error: incomplete operation data: {exception}", file=sys.stderr)
        return GhError.exit_code
    except (OSError, UnicodeError) as exception:
        print(f"error: {exception}", file=sys.stderr)
        return UsageError.exit_code
    print(json.dumps(result, indent=2))
    return 3 if result.get("problems") else 0


def repo_read(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    endpoint = f"repos/{repository(args.repo)}"
    if args.path:
        path = PurePosixPath(args.path)
        if path.is_absolute() or ".." in path.parts or path == PurePosixPath("."):
            raise UsageError("expected a repository-relative file path")
        if not args.ref:
            raise UsageError("file reads require a pinned commit SHA")
        endpoint += f"/contents/{quote(args.path, safe='/')}?ref={sha(args.ref)}"
    elif args.ref:
        endpoint += f"/commits/{sha(args.ref)}"
    return gh.json("api", endpoint)


def repo_search(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    fields = "path,repository,sha,url"
    return {"matches": gh.json("search", "code", "--repo", repository(args.repo), "--json", fields, "--", args.query)}


def register_commands(command: Callable[..., argparse.ArgumentParser], nested: dict[str, Any]) -> None:
    def flags(parser: argparse.ArgumentParser, *names: str) -> None:
        for name in names:
            parser.add_argument(f"--{name}", required=True)

    p = command("repo", "read", repo_read)
    flags(p, "repo")
    p.add_argument("--ref")
    p.add_argument("--path")
    p = command("repo", "search", repo_search)
    flags(p, "repo")
    p.add_argument("query")

    p = command("issue", "read", issues.issue_read)
    p.add_argument("ref")
    p.add_argument("--comments", action="store_true")
    p = command("issue", "list", issues.issue_list)
    flags(p, "repo")
    p.add_argument("--label", action="append", default=[])
    p = command("issue", "create", issues.issue_create)
    flags(p, "repo", "title", "body-file")
    p.add_argument("--label", action="append", default=[])
    for action, handler in (
        ("children", issues.children), ("blockers", issues.blockers), ("link-child", issues.link_child),
        ("assign", issues.change_assignment), ("unassign", issues.change_assignment),
    ):
        p = command("issue", action, handler)
        p.add_argument("ref")
        if action == "link-child":
            p.add_argument("child")
        if action in {"assign", "unassign"}:
            p.add_argument("--login", default="@me")
    for action in ("post-comment", "upsert-comment"):
        p = command("issue", action, pulls.issue_comment)
        p.add_argument("ref")
        flags(p, "body-file")
        p.add_argument("--marker", required=action == "upsert-comment")

    for action in ("ensure", "verify"):
        p = command("label", action, issues.manage_labels)
        flags(p, "repo")
        p.add_argument("--manifest")
        p.add_argument("--name")
        p.add_argument("--color")
        p.add_argument("--description", default="")

    for action in ("list", "get", "put"):
        p = command("artifact", action, specs.artifacts)
        p.add_argument("ref")
        if action == "get":
            p.add_argument("number", type=int)
        if action == "put":
            flags(p, "name", "type", "body-file")

    p = command("pr", "open", pulls.pr_open)
    flags(p, "repo", "head", "base", "expected", "title", "body-file")
    p.add_argument("--draft", action="store_true")
    p = command("pr", "find", pulls.pr_find)
    flags(p, "repo", "head")
    p = command("pr", "snapshot", pulls.pr_snapshot)
    p.add_argument("ref")
    p.add_argument("--inline", action="store_true")
    p.add_argument("--comments", action="store_true")
    for action, handler in (("diff", pulls.pr_diff), ("checkout", pulls.pr_checkout), ("fetch", pulls.pr_fetch)):
        p = command("pr", action, handler)
        p.add_argument("ref")
        flags(p, "expected", "base")
        if action != "diff":
            flags(p, "checkout", "remote")
        if action == "fetch":
            flags(p, "run-id")
    for action in ("comment", "upsert-comment"):
        p = command("pr", action, pulls.pr_comment)
        p.add_argument("ref")
        flags(p, "body-file")
        p.add_argument("--marker", required=action == "upsert-comment")
    p = command("checks", "read", pulls.checks)
    p.add_argument("ref")
    flags(p, "expected")

    reviews.register(nested["review"].add_parser("discussion"))
    p = command("review", "inline", reviews.post_inline)
    p.add_argument("ref")
    flags(p, "expected", "path", "body-file")
    p.add_argument("--base")
    p.add_argument("--line", required=True, type=int)
    for action in ("reply", "resolve"):
        p = command("review", action, reviews.change_thread)
        p.add_argument("ref")
        flags(p, "expected", "thread", "snapshot")
        if action == "reply":
            flags(p, "body-file")
