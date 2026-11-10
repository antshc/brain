from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from .core import Git, UsageError


def checkout(client: Git, args: argparse.Namespace) -> str:
    root = Path(args.checkout)
    if not root.is_absolute():
        raise UsageError("checkout must be absolute")
    actual = Path(client.git("-C", str(root), "rev-parse", "--show-toplevel").strip())
    if actual.resolve() != root.resolve():
        raise UsageError("checkout must name the repository root")
    return str(actual)


def sha(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
        raise UsageError("expected a full commit SHA")
    return value


def branch_ref(client: Git, root: str, name: str) -> str:
    ref = f"refs/heads/{name}"
    client.git("-C", root, "check-ref-format", ref)
    return ref


def local_tip(client: Git, root: str, ref: str) -> str:
    return client.git("-C", root, "rev-parse", "--verify", ref).strip()


def remote_tip(client: Git, root: str, remote: str, ref: str) -> str | None:
    lines = client.git("-C", root, "ls-remote", "--heads", "--", remote, ref).splitlines()
    matches = [line.split("\t", 1)[0] for line in lines if line.endswith(f"\t{ref}")]
    if len(matches) > 1:
        raise UsageError(f"ambiguous remote ref: {ref}")
    return matches[0] if matches else None


def verify_remote(client: Git, root: str, remote: str, repository: str, *, push: bool = False) -> None:
    flags = ["--push", "--all"] if push else ["--all"]
    urls = client.git("-C", root, "remote", "get-url", *flags, remote).splitlines()
    prefix = r"(?:https://github\.com/|ssh://git@github\.com/|git@github\.com:)"
    if len(urls) != 1 or not re.fullmatch(prefix + re.escape(repository) + r"(?:\.git)?/?", urls[0], re.I):
        raise UsageError(f"{remote} does not uniquely identify {repository}")


def branch_inspect(client: Git, args: argparse.Namespace) -> dict[str, Any]:
    root = checkout(client, args)
    ref = branch_ref(client, root, args.name)
    rows = client.git("-C", root, "for-each-ref", "--format=%(objectname) %(refname)", ref).splitlines()
    result = {"ref": ref, "local": next((row.split()[0] for row in rows if row.endswith(f" {ref}")), None)}
    if args.remote:
        if not args.repo:
            raise UsageError("remote inspection requires --repo")
        verify_remote(client, root, args.remote, args.repo)
        result["remote"] = remote_tip(client, root, args.remote, ref)
    return result


def branch_create(client: Git, args: argparse.Namespace) -> dict[str, Any]:
    root = checkout(client, args)
    ref = branch_ref(client, root, args.name)
    expected = sha(args.start)
    if local_tip(client, root, f"{expected}^{{commit}}") != expected:
        raise UsageError("branch start must identify a commit")
    client.git("-C", root, "branch", "--", args.name, expected)
    return {"ref": ref, "head": local_tip(client, root, ref)}


def branch_fetch(client: Git, args: argparse.Namespace) -> dict[str, Any]:
    root = checkout(client, args)
    verify_remote(client, root, args.remote, args.repo)
    expected = sha(args.expected)
    client.git("-C", root, "fetch", "--no-tags", "--no-write-fetch-head", "--", args.remote, expected)
    client.git("-C", root, "cat-file", "-e", f"{expected}^{{commit}}")
    return {"head": expected}


def branch_push(client: Git, args: argparse.Namespace) -> dict[str, Any]:
    root = checkout(client, args)
    ref = branch_ref(client, root, args.name)
    verify_remote(client, root, args.remote, args.repo)
    verify_remote(client, root, args.remote, args.repo, push=True)
    head = sha(args.expected)
    previous = None if args.previous == "absent" else sha(args.previous)
    if local_tip(client, root, ref) != head:
        raise UsageError(f"local head changed: {ref}")
    observed = remote_tip(client, root, args.remote, ref)
    if observed != head:
        if observed != previous:
            raise UsageError(f"remote head changed: {ref} is {observed}")
        if previous:
            client.git("-C", root, "merge-base", "--is-ancestor", previous, head)
        flags = ["--set-upstream"] if args.set_upstream else []
        source = ref if args.set_upstream else head
        client.git("-C", root, "-c", "push.followTags=false", "push", *flags, "--", args.remote, f"{source}:{ref}")
    if remote_tip(client, root, args.remote, ref) != head:
        raise UsageError(f"push could not be verified: {ref}")
    return {"ref": ref, "head": head}


def branch_delete(client: Git, args: argparse.Namespace) -> dict[str, Any]:
    root = checkout(client, args)
    ref = branch_ref(client, root, args.name)
    head = sha(args.expected)
    if local_tip(client, root, ref) != head:
        raise UsageError(f"local head changed: {ref}")
    client.git("-C", root, "merge-base", "--is-ancestor", head, sha(args.integrated_into))
    client.git("-C", root, "branch", "-d", "--", args.name)
    return {"ref": ref, "deleted": True}


