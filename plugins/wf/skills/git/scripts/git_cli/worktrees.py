from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

OWNER_FILE = "brain-worktree.json"
SHA = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
SEGMENT = re.compile(r"[A-Za-z0-9_.-]+")
GIT_ENV = {
    name: value
    for name, value in os.environ.items()
    if name not in {"GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
                    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"}
}


class WorktreeError(Exception):
    pass


def git(checkout: Path, *args: str, allowed: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(checkout), *args],
        capture_output=True, env=GIT_ENV,
    )
    if result.returncode not in allowed:
        detail = os.fsdecode(result.stderr).strip() or f"exit {result.returncode}"
        raise WorktreeError(f"git {args[0]}: {detail}")
    return result


def output(checkout: Path, *args: str) -> str:
    value = os.fsdecode(git(checkout, *args).stdout).removesuffix("\n")
    return value.removesuffix("\r") if os.name == "nt" else value


def checkout(path: Path) -> Path:
    if not path.is_absolute():
        raise WorktreeError(f"Checkout path must be absolute: {path}")
    root = path.resolve(strict=True)
    if Path(output(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise WorktreeError(f"Expected a Git checkout root: {path}")
    return root


def git_path(root: Path, option: str) -> Path:
    return Path(output(root, "rev-parse", "--path-format=absolute", option)).resolve()


def registrations(source: Path) -> dict[Path, dict[str, str]]:
    records = {}
    data = os.fsdecode(git(source, "worktree", "list", "--porcelain", "-z").stdout)
    for entry in data.strip("\0").split("\0\0"):
        fields = {key: value for key, _, value in (line.partition(" ") for line in entry.split("\0"))}
        if "worktree" not in fields:
            raise WorktreeError("Invalid Git worktree registration")
        path = Path(fields["worktree"]).resolve()
        if path in records:
            raise WorktreeError(f"Ambiguous Git worktree registration: {path}")
        records[path] = fields
    return records


def managed_path(harness: Path, repo: str, leaf: str) -> Path:
    for name in (repo, leaf):
        if not SEGMENT.fullmatch(name) or name.startswith("-") or name.endswith("."):
            raise WorktreeError(f"Invalid worktree path segment: {name!r}")
    path = harness / ".worktrees" / repo / leaf
    if path.resolve() != path:
        raise WorktreeError(f"Worktree path contains a symlink or escapes its root: {path}")
    return path


def verify_commit(source: Path, sha: str) -> None:
    if not SHA.fullmatch(sha) or output(source, "rev-parse", "--verify", f"{sha}^{{commit}}") != sha:
        raise WorktreeError(f"Expected a full local commit SHA: {sha}")


def check_state(
    path: Path, fields: dict[str, str], common: Path, branch: str | None, sha: str
) -> Path:
    branch_matches = "detached" in fields if branch is None else fields.get("branch") == f"refs/heads/{branch}"
    if not branch_matches or fields.get("HEAD") != sha:
        raise WorktreeError(f"Worktree branch or HEAD mismatch: {path}")
    if any(flag in fields for flag in ("locked", "prunable", "bare")):
        raise WorktreeError(f"Worktree is locked or unavailable: {path}")
    if checkout(path) != path or git_path(path, "--git-common-dir") != common:
        raise WorktreeError(f"Worktree belongs to another repository: {path}")
    admin = git_path(path, "--git-dir")
    if admin.parent != common / "worktrees":
        raise WorktreeError(f"Expected a linked worktree: {path}")
    return admin


def check_clean(path: Path, admin: Path) -> None:
    operations = ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-apply",
                  "rebase-merge", "sequencer", "BISECT_START")
    if any((admin / operation).exists() for operation in operations):
        raise WorktreeError(f"Worktree has a Git operation in progress: {path}")
    if git(path, "status", "--porcelain=v1", "-z", "--untracked-files=all",
           "--ignored=matching", "--ignore-submodules=none").stdout:
        raise WorktreeError(f"Worktree contains modified, untracked or ignored files: {path}")


def ensure_ignored(harness: Path, path: Path, changed: list[str]) -> None:
    relative = path.relative_to(harness).as_posix() + "/"
    if git(harness, "ls-files", "-z", "--", ".worktrees/").stdout:
        raise WorktreeError("Harness tracks files under .worktrees/")
    if git(harness, "check-ignore", "-q", "--", relative, allowed=(0, 1)).returncode == 0:
        return
    exclude = Path(output(harness, "rev-parse", "--path-format=absolute", "--git-path", "info/exclude"))
    if exclude.is_symlink():
        raise WorktreeError(f"Refusing to edit a symlinked Git exclude file: {exclude}")
    exclude.parent.mkdir(parents=True, exist_ok=True)
    with exclude.open("ab+") as file:
        file.seek(0)
        original = file.read()
        if b"/.worktrees/" not in original.splitlines():
            separator = b"\n" if original and not original.endswith(b"\n") else b""
            file.write(separator + b"/.worktrees/\n")
            changed.append(str(exclude))
    if git(harness, "check-ignore", "-q", "--", relative, allowed=(0, 1)).returncode != 0:
        raise WorktreeError(f"Harness still does not ignore {relative}")


def create(
    args: argparse.Namespace, harness: Path, source: Path, common: Path, result: dict[str, Any]
) -> None:
    path = managed_path(harness, args.repo_name, args.name)
    result["path"] = str(path)
    result["branch"] = args.new_branch
    if path in registrations(source) or path.exists():
        raise WorktreeError(f"Worktree path is occupied: {path}")
    if path.parent.is_dir():
        for sibling in path.parent.iterdir():
            if (sibling / ".git").exists() and git_path(sibling, "--git-common-dir") != common:
                raise WorktreeError(f"Worktree namespace contains another repository: {sibling}")
    verify_commit(source, args.commit)
    if not args.owner.strip():
        raise WorktreeError("Worktree owner must be nonempty")
    mode = ["--detach"]
    if args.new_branch is not None:
        if output(source, "check-ref-format", "--branch", args.new_branch) != args.new_branch:
            raise WorktreeError(f"Expected a literal branch name: {args.new_branch}")
        if git(source, "show-ref", "--verify", "--quiet", f"refs/heads/{args.new_branch}",
               allowed=(0, 1)).returncode == 0:
            raise WorktreeError(f"Local branch already exists: {args.new_branch}")
        mode = ["-b", args.new_branch]

    ensure_ignored(harness, path, result["changedExcludeFiles"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.mkdir()
    git(source, "worktree", "add", *mode, "--", str(path), args.commit)
    fields = registrations(source).get(path)
    if fields is None:
        raise WorktreeError(f"Created worktree is not registered: {path}")
    admin = check_state(path, fields, common, args.new_branch, args.commit)
    check_clean(path, admin)
    record = {
        "owner": args.owner, "token": uuid4().hex, "path": str(path), "commonDir": str(common),
        "gitDir": str(admin), "branch": args.new_branch, "head": args.commit,
    }
    with (admin / OWNER_FILE).open("x", encoding="utf-8") as file:
        json.dump(record, file)
    result.update(status="created", record=record)


def remove(
    args: argparse.Namespace, harness: Path, source: Path, common: Path, result: dict[str, Any]
) -> None:
    record = json.loads(args.record.read_text(encoding="utf-8"))
    fields = ("owner", "token", "path", "commonDir", "gitDir", "head")
    if (not isinstance(record, dict) or any(not isinstance(record.get(key), str) or not record[key] for key in fields)
            or "branch" not in record or not isinstance(record["branch"], (str, type(None)))):
        raise WorktreeError("Invalid worktree ownership record")
    path = Path(record["path"])
    if record["commonDir"] != str(common) or not path.is_relative_to(harness / ".worktrees"):
        raise WorktreeError("Ownership record belongs to another repository or harness")
    relative = path.relative_to(harness / ".worktrees")
    if len(relative.parts) != 2 or managed_path(harness, *relative.parts) != path:
        raise WorktreeError(f"Invalid managed worktree path: {path}")
    result["path"] = str(path)
    if source.is_relative_to(path) or Path.cwd().resolve().is_relative_to(path):
        raise WorktreeError(f"Remove from outside the target worktree: {path}")
    if not args.recoverable:
        raise WorktreeError("Verify recoverability before removal")

    registered = registrations(source).get(path)
    if registered is None and not path.exists():
        result["status"] = "absent"
        return
    if registered is None or not path.is_dir():
        raise WorktreeError(f"Worktree path and registration disagree: {path}")
    admin = check_state(path, registered, common, record["branch"], args.expect_head)
    marker = admin / OWNER_FILE
    if (str(admin) != record["gitDir"] or marker.is_symlink() or not marker.is_file()
            or json.loads(marker.read_text(encoding="utf-8")) != record):
        raise WorktreeError(f"Worktree ownership could not be verified: {path}")
    check_clean(path, admin)
    index_entries = git(path, "ls-files", "-v", "-z").stdout.split(b"\0")
    if any(entry[:1].islower() or entry.startswith(b"S ") for entry in index_entries):
        raise WorktreeError(f"Index flags may hide worktree changes: {path}")
    git(source, "worktree", "remove", "--", str(path))
    if path.exists() or path.is_symlink() or path in registrations(source):
        raise WorktreeError(f"Worktree removal could not be verified: {path}")
    result["status"] = "removed"


def register(actions: Any) -> None:
    create_parser = actions.add_parser("create")
    remove_parser = actions.add_parser("remove")
    for action_parser in (create_parser, remove_parser):
        action_parser.add_argument("--harness", type=Path, required=True)
        action_parser.add_argument("--source", type=Path, required=True)
    for name in ("repo-name", "name", "commit", "owner"):
        create_parser.add_argument(f"--{name}", required=True)
    mode = create_parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--new-branch")
    mode.add_argument("--detach", action="store_true")
    remove_parser.add_argument("--record", type=Path, required=True)
    remove_parser.add_argument("--expect-head", required=True)
    remove_parser.add_argument("--recoverable", action="store_true")
    for action_parser in (create_parser, remove_parser):
        action_parser.set_defaults(entry=run)
    for name in ("inspect", "reconcile", "reuse"):
        action_parser = actions.add_parser(name)
        action_parser.add_argument("--harness", type=Path, required=True)
        action_parser.add_argument("--source", type=Path, required=True)
        action_parser.add_argument("--record", type=Path)
        action_parser.add_argument("--repo-name")
        action_parser.add_argument("--name")
        action_parser.add_argument("--expect-head")
        action_parser.set_defaults(entry=run)


def run(args: argparse.Namespace) -> int:

    result: dict[str, Any] = {"changedExcludeFiles": []} if args.action == "create" else {}
    try:
        harness = checkout(args.harness)
        source = checkout(args.source)
        common = git_path(source, "--git-common-dir")
        if args.action == "create":
            create(args, harness, source, common, result)
        elif args.action == "remove":
            remove(args, harness, source, common, result)
        else:
            inspect(args, harness, source, common, result)
    except (WorktreeError, OSError, ValueError, RuntimeError) as exception:
        result.update(status="blocked", reason=str(exception))
        print(str(exception), file=sys.stderr)
    print(json.dumps(result))
    return 1 if result["status"] == "blocked" else 0


def inspect(
    args: argparse.Namespace, harness: Path, source: Path, common: Path, result: dict[str, Any]
) -> None:
    record = json.loads(args.record.read_text(encoding="utf-8")) if args.record else None
    if record is not None:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise WorktreeError("Invalid ownership record")
        path = Path(record["path"])
        if not path.is_relative_to(harness / ".worktrees"):
            raise WorktreeError("Ownership record belongs to another harness")
        parts = path.relative_to(harness / ".worktrees").parts
        if len(parts) != 2 or managed_path(harness, *parts) != path:
            raise WorktreeError("Invalid managed worktree path")
    elif args.repo_name and args.name and args.action != "reuse":
        path = managed_path(harness, args.repo_name, args.name)
    else:
        raise WorktreeError("Supply an ownership record or the managed repo name and leaf")

    result["path"] = str(path)
    fields = registrations(source).get(path)
    if fields is None and not path.exists():
        if args.action == "reuse":
            raise WorktreeError(f"Worktree is absent: {path}")
        result["status"] = "absent"
        return
    if fields is None or not path.is_dir():
        raise WorktreeError(f"Worktree path and registration disagree: {path}")
    head = fields.get("HEAD")
    branch = fields.get("branch", "").removeprefix("refs/heads/") or None
    if not head:
        raise WorktreeError(f"Registration has no HEAD: {path}")
    result.update(head=head, branch=branch, locked="locked" in fields, registered=True)
    if args.action == "inspect":
        if git_path(path, "--git-common-dir") != common:
            raise WorktreeError(f"Worktree belongs to another repository: {path}")
        admin = git_path(path, "--git-dir")
        try:
            check_clean(path, admin)
        except WorktreeError as exception:
            result.update(clean=False, reason=str(exception))
        else:
            result["clean"] = True
        result.update(status="present", gitDir=str(admin), commonDir=str(common))
        return
    if not record or not args.expect_head:
        raise WorktreeError("Verify ownership and expected HEAD before reuse or reconciliation")
    admin = check_state(path, fields, common, record.get("branch"), args.expect_head)
    marker = admin / OWNER_FILE
    if (not record.get("owner") or not record.get("token") or record.get("commonDir") != str(common)
            or record.get("gitDir") != str(admin) or marker.is_symlink() or not marker.is_file()
            or json.loads(marker.read_text(encoding="utf-8")) != record):
        raise WorktreeError(f"Worktree ownership could not be verified: {path}")
    check_clean(path, admin)
    result.update(status="reused" if args.action == "reuse" else "verified", record=record)
