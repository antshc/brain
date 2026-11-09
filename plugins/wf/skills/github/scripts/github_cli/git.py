from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from .gh import Gh, UsageError


def checkout(gh: Gh, args: argparse.Namespace) -> str:
    root = Path(args.checkout)
    if not root.is_absolute():
        raise UsageError("checkout must be absolute")
    actual = Path(gh.git("-C", str(root), "rev-parse", "--show-toplevel").strip())
    if actual.resolve() != root.resolve():
        raise UsageError("checkout must name the repository root")
    return str(actual)


def sha(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
        raise UsageError("expected a full commit SHA")
    return value


def branch_ref(gh: Gh, root: str, name: str) -> str:
    ref = f"refs/heads/{name}"
    gh.git("-C", root, "check-ref-format", ref)
    return ref


def local_tip(gh: Gh, root: str, ref: str) -> str:
    return gh.git("-C", root, "rev-parse", "--verify", ref).strip()


def remote_tip(gh: Gh, root: str, remote: str, ref: str) -> str | None:
    lines = gh.git("-C", root, "ls-remote", "--heads", "--", remote, ref).splitlines()
    matches = [line.split("\t", 1)[0] for line in lines if line.endswith(f"\t{ref}")]
    if len(matches) > 1:
        raise UsageError(f"ambiguous remote ref: {ref}")
    return matches[0] if matches else None


def verify_remote(gh: Gh, root: str, remote: str, repository: str, *, push: bool = False) -> None:
    flags = ["--push", "--all"] if push else ["--all"]
    urls = gh.git("-C", root, "remote", "get-url", *flags, remote).splitlines()
    prefix = r"(?:https://github\.com/|ssh://git@github\.com/|git@github\.com:)"
    if len(urls) != 1 or not re.fullmatch(prefix + re.escape(repository) + r"(?:\.git)?/?", urls[0], re.I):
        raise UsageError(f"{remote} does not uniquely identify {repository}")


def branch_inspect(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    root = checkout(gh, args)
    ref = branch_ref(gh, root, args.name)
    rows = gh.git("-C", root, "for-each-ref", "--format=%(objectname) %(refname)", ref).splitlines()
    result = {"ref": ref, "local": next((row.split()[0] for row in rows if row.endswith(f" {ref}")), None)}
    if args.remote:
        if not args.repo:
            raise UsageError("remote inspection requires --repo")
        verify_remote(gh, root, args.remote, args.repo)
        result["remote"] = remote_tip(gh, root, args.remote, ref)
    return result


def branch_create(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    root = checkout(gh, args)
    ref = branch_ref(gh, root, args.name)
    expected = sha(args.start)
    if local_tip(gh, root, f"{expected}^{{commit}}") != expected:
        raise UsageError("branch start must identify a commit")
    gh.git("-C", root, "branch", "--", args.name, expected)
    return {"ref": ref, "head": local_tip(gh, root, ref)}


def branch_fetch(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    root = checkout(gh, args)
    verify_remote(gh, root, args.remote, args.repo)
    expected = sha(args.expected)
    gh.git("-C", root, "fetch", "--no-tags", "--no-write-fetch-head", "--", args.remote, expected)
    gh.git("-C", root, "cat-file", "-e", f"{expected}^{{commit}}")
    return {"head": expected}


def branch_push(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    root = checkout(gh, args)
    ref = branch_ref(gh, root, args.name)
    verify_remote(gh, root, args.remote, args.repo)
    verify_remote(gh, root, args.remote, args.repo, push=True)
    head = sha(args.expected)
    previous = None if args.previous == "absent" else sha(args.previous)
    if local_tip(gh, root, ref) != head:
        raise UsageError(f"local head changed: {ref}")
    observed = remote_tip(gh, root, args.remote, ref)
    if observed != head:
        if observed != previous:
            raise UsageError(f"remote head changed: {ref} is {observed}")
        if previous:
            gh.git("-C", root, "merge-base", "--is-ancestor", previous, head)
        flags = ["--set-upstream"] if args.set_upstream else []
        source = ref if args.set_upstream else head
        gh.git("-C", root, "-c", "push.followTags=false", "push", *flags, "--", args.remote, f"{source}:{ref}")
    if remote_tip(gh, root, args.remote, ref) != head:
        raise UsageError(f"push could not be verified: {ref}")
    return {"ref": ref, "head": head}


def branch_delete(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    root = checkout(gh, args)
    ref = branch_ref(gh, root, args.name)
    head = sha(args.expected)
    if local_tip(gh, root, ref) != head:
        raise UsageError(f"local head changed: {ref}")
    gh.git("-C", root, "merge-base", "--is-ancestor", head, sha(args.integrated_into))
    gh.git("-C", root, "branch", "-d", "--", args.name)
    return {"ref": ref, "deleted": True}


def commit_history(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    root = checkout(gh, args)
    tip = sha(args.tip) if args.tip else "HEAD"
    revision = f"{sha(args.base)}..{tip}" if args.base else tip
    raw = gh.git("-C", root, "log", "-z", "--reverse", "--format=%H%x00%s%x00%b", revision, "--")
    fields = raw.split("\0")[:-1]
    commits = [
        {"sha": oid, "subject": subject, "body": body}
        for oid, subject, body in zip(fields[::3], fields[1::3], fields[2::3], strict=True)
        if not args.ccode or re.match(r"^ccode\([^)]*\):", subject)
    ]
    return {"commits": commits}


def commit_create(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    root = checkout(gh, args)
    expected = sha(args.expected)
    if local_tip(gh, root, "HEAD") != expected:
        raise UsageError("checkout HEAD changed")
    if gh.git("-C", root, "diff", "--cached", "--name-only"):
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
    gh.git("-C", root, "--literal-pathspecs", "add", "--", *paths)
    gh.git("-C", root, "--literal-pathspecs", "commit", "--only", "-F", str(message), "--", *paths)
    return {"head": local_tip(gh, root, "HEAD"), "previous": expected}
