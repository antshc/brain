from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from .branches import checkout, local_tip, sha
from .core import Git, UsageError


def commit_history(client: Git, args: argparse.Namespace) -> dict[str, Any]:
    root = checkout(client, args)
    tip = sha(args.tip) if args.tip else "HEAD"
    revision = f"{sha(args.base)}..{tip}" if args.base else tip
    raw = client.git("-C", root, "log", "-z", "--reverse", "--format=%H%x00%s%x00%b", revision, "--")
    fields = raw.split("\0")[:-1]
    commits = [
        {"sha": oid, "subject": subject, "body": body}
        for oid, subject, body in zip(fields[::3], fields[1::3], fields[2::3], strict=True)
        if not args.ccode or re.match(r"^ccode\([^)]*\):", subject)
    ]
    return {"commits": commits}


def commit_create(client: Git, args: argparse.Namespace) -> dict[str, Any]:
    root = checkout(client, args)
    expected = sha(args.expected)
    if local_tip(client, root, "HEAD") != expected:
        raise UsageError("checkout HEAD changed")
    if client.git("-C", root, "diff", "--cached", "--name-only"):
        raise UsageError("checkout has pre-existing staged changes")
    paths = []
    for value in args.paths:
        path = Path(value)
        if path.is_absolute() or ".." in path.parts or path == Path("."):
            raise UsageError(f"commit needs exact repository-relative file paths: {value}")
        if (Path(root) / path).is_dir() and not (Path(root) / path).is_symlink():
            raise UsageError(f"commit path names a directory: {value}")
        paths.append(path.as_posix())
    message = Path(args.message_file).resolve(strict=True)
    client.git("-C", root, "--literal-pathspecs", "add", "--", *paths)
    client.git("-C", root, "--literal-pathspecs", "commit", "--only", "-F", str(message), "--", *paths)
    return {"head": local_tip(client, root, "HEAD"), "previous": expected}
