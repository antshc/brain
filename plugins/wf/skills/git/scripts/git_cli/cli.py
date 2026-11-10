from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, Callable

from . import branches, commits, worktrees
from .core import Git, GitError, UsageError


def repo_resolve(client: Git, args: argparse.Namespace) -> dict[str, Any]:
    root = branches.checkout(client, args)
    url = client.git("-C", root, "remote", "get-url", args.remote).strip()
    name = args.repo
    if not name:
        match = re.fullmatch(r"(?:https://github\.com/|ssh://git@github\.com/|git@github\.com:)(.+?)(?:\.git)?/?", url)
        if not match:
            raise UsageError("remote is not a GitHub repository")
        name = match[1]
    branches.verify_remote(client, root, args.remote, name)
    return {"repo": name, "checkout": root, "remote": args.remote}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Brain Git repository operations")
    groups = parser.add_subparsers(dest="group", required=True)
    nested = {name: groups.add_parser(name).add_subparsers(dest="action", required=True)
              for name in ("repo", "branch", "commit", "worktree")}

    p = nested["repo"].add_parser("resolve")
    p.set_defaults(handler=repo_resolve)
    p.add_argument("--checkout", required=True)
    p.add_argument("--repo")
    p.add_argument("--remote", default="origin")

    for action, handler, required in (
        ("inspect", branches.branch_inspect, ("name",)),
        ("create", branches.branch_create, ("name", "start")),
        ("fetch", branches.branch_fetch, ("repo", "remote", "expected")),
        ("push", branches.branch_push, ("repo", "remote", "name", "expected", "previous")),
        ("delete", branches.branch_delete, ("name", "expected", "integrated-into")),
    ):
        p = nested["branch"].add_parser(action)
        p.set_defaults(handler=handler)
        for name in ("checkout", *required):
            p.add_argument(f"--{name}", required=True)
        if action == "inspect":
            p.add_argument("--repo")
            p.add_argument("--remote")
        if action == "push":
            p.add_argument("--set-upstream", action="store_true")

    p = nested["commit"].add_parser("history")
    p.set_defaults(handler=commits.commit_history)
    p.add_argument("--checkout", required=True)
    p.add_argument("--base")
    p.add_argument("--tip")
    p.add_argument("--ccode", action="store_true")
    p = nested["commit"].add_parser("create")
    p.set_defaults(handler=commits.commit_create)
    for name in ("checkout", "expected", "message-file"):
        p.add_argument(f"--{name}", required=True)
    p.add_argument("paths", nargs="+")
    worktrees.register(nested["worktree"])
    return parser


def main(argv: list[str] | None = None, *, git_client: Git | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if hasattr(args, "entry"):
            return args.entry(args)
        result = args.handler(git_client or Git(), args)
    except (UsageError, GitError) as exception:
        print(f"error: {exception}", file=sys.stderr)
        return exception.exit_code
    except (KeyError, TypeError, json.JSONDecodeError) as exception:
        print(f"error: incomplete operation data: {exception}", file=sys.stderr)
        return GitError.exit_code
    except (OSError, UnicodeError) as exception:
        print(f"error: {exception}", file=sys.stderr)
        return UsageError.exit_code
    print(json.dumps(result, indent=2))
    return 3 if result.get("problems") else 0
