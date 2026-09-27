#!/usr/bin/env python3
"""Capture and restore Chorey's review scope without mutating Git state."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence


ARTIFACT_DIR = Path("bin") / "crew_diff"
MANIFEST_NAME = "_manifest.json"

AI_BASENAMES = {"AGENTS.md", "SKILL.md"}
AI_SUFFIXES = (".agent.md", ".instructions.md", ".prompt.md")
DOTNET_BASENAMES = {"Directory.Build.props", "Directory.Packages.props"}
DOTNET_SUFFIXES = (".cs", ".csproj", ".sln")
PY_BASENAMES = {
    "Pipfile",
    "Pipfile.lock",
    "poetry.lock",
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "tox.ini",
}


class ChoreyDiffError(RuntimeError):
    pass


@dataclass(frozen=True)
class Change:
    status: str
    path: str
    old_path: str | None = None

    def as_dict(self) -> dict[str, str]:
        value = {"status": self.status, "path": self.path}
        if self.old_path is not None:
            value["old_path"] = self.old_path
        return value


def _run(
    args: Sequence[str],
    *,
    cwd: Path,
    input_bytes: bytes | None = None,
    allowed_codes: Iterable[int] = (0,),
) -> bytes:
    result = subprocess.run(
        args,
        cwd=cwd,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode not in set(allowed_codes):
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise ChoreyDiffError(message or f"command failed ({result.returncode}): {' '.join(args)}")
    return result.stdout


def _git(repo: Path, *args: str, allowed_codes: Iterable[int] = (0,)) -> bytes:
    return _run(("git", *args), cwd=repo, allowed_codes=allowed_codes)


def _repo_root(cwd: Path) -> Path:
    output = _run(("git", "rev-parse", "--show-toplevel"), cwd=cwd)
    return Path(os.fsdecode(output.rstrip(b"\r\n"))).resolve()


def _artifact_root(repo: Path) -> Path:
    return repo / ARTIFACT_DIR


def _discard(repo: Path) -> None:
    target = _artifact_root(repo)
    expected = (repo / "bin" / "crew_diff").resolve()
    if target.resolve() != expected:
        raise ChoreyDiffError("refusing to remove an unexpected artifact path")
    if target.exists():
        shutil.rmtree(target)


def _decode_path(value: bytes) -> str:
    return os.fsdecode(value)


def _parse_name_status(data: bytes) -> list[Change]:
    fields = data.split(b"\0")
    if fields and fields[-1] == b"":
        fields.pop()
    changes: list[Change] = []
    index = 0
    while index < len(fields):
        status = fields[index].decode("ascii", errors="strict")
        index += 1
        kind = status[:1]
        if kind in {"R", "C"}:
            if index + 1 >= len(fields):
                raise ChoreyDiffError("Git returned an incomplete rename/copy record")
            old_path = _decode_path(fields[index])
            path = _decode_path(fields[index + 1])
            index += 2
            changes.append(Change(status=status, path=path, old_path=old_path))
        else:
            if index >= len(fields):
                raise ChoreyDiffError("Git returned an incomplete changed-path record")
            changes.append(Change(status=status, path=_decode_path(fields[index])))
            index += 1
    return changes


def _name_status(repo: Path, *diff_args: str) -> list[Change]:
    return _parse_name_status(_git(repo, *diff_args, "--name-status", "-z", "-M", "-C", "--"))


def _safe_workspace_path(repo: Path, repo_path: str) -> Path:
    path = PurePosixPath(repo_path)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ChoreyDiffError(f"unsafe repository path in Git output: {repo_path!r}")
    return repo.joinpath(*path.parts)


def _normalize_repo_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts or not path.parts or normalized in {"", "."}:
        raise ChoreyDiffError(f"unsafe repository path: {value!r}")
    repo_path = path.as_posix()
    if repo_path == ".git" or repo_path.startswith(".git/"):
        raise ChoreyDiffError(f"refusing to restore Git internals: {value!r}")
    if repo_path == "bin/crew_diff" or repo_path.startswith("bin/crew_diff/"):
        raise ChoreyDiffError(f"refusing to restore chorey-diff artifacts: {value!r}")
    return repo_path


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _write_patch(path: Path, sections: Sequence[tuple[str, bytes]]) -> None:
    content = bytearray()
    for label, patch in sections:
        content.extend(f"=== {label} ===\n".encode("ascii"))
        content.extend(patch)
        if patch and not patch.endswith(b"\n"):
            content.extend(b"\n")
    path.write_bytes(bytes(content))


def _detect_stacks(paths: Iterable[str]) -> list[str]:
    stacks: set[str] = set()
    for repo_path in paths:
        name = PurePosixPath(repo_path).name
        if name in AI_BASENAMES or name.endswith(AI_SUFFIXES):
            stacks.add("ai")
        if name in DOTNET_BASENAMES or name.endswith(DOTNET_SUFFIXES):
            stacks.add("dotnet")
        if (
            name in PY_BASENAMES
            or name.endswith(".py")
            or fnmatch.fnmatchcase(name, "requirements*.txt")
        ):
            stacks.add("py")
    return sorted(stacks)


def _prepare_artifacts(repo: Path) -> tuple[Path, Path]:
    root = _artifact_root(repo)
    _discard(repo)
    diffs = root / "diffs"
    diffs.mkdir(parents=True)
    return root, diffs


def _resolve_commit(repo: Path, baseline: str) -> str:
    output = _git(repo, "rev-parse", "--verify", f"{baseline}^{{commit}}")
    return output.decode("ascii").strip()


def _empty_tree(repo: Path) -> str:
    return _run(("git", "hash-object", "-t", "tree", "--stdin"), cwd=repo, input_bytes=b"").decode(
        "ascii"
    ).strip()


def _capture_commit(repo: Path, baseline: str) -> dict[str, object]:
    commit = _resolve_commit(repo, baseline)
    parent_line = _git(repo, "rev-list", "--parents", "-n", "1", commit).decode("ascii").split()
    base = parent_line[1] if len(parent_line) > 1 else _empty_tree(repo)
    changes = _name_status(repo, "diff", base, commit)
    artifact_root, diffs_dir = _prepare_artifacts(repo)
    files: list[dict[str, object]] = []
    for number, change in enumerate(sorted(changes, key=lambda item: item.path), start=1):
        identifier = f"{number:04d}"
        pathspecs = [value for value in (change.old_path, change.path) if value]
        patch = _git(
            repo,
            "diff",
            "--binary",
            "--full-index",
            "--find-renames",
            "--find-copies",
            base,
            commit,
            "--",
            *pathspecs,
        )
        diff_rel = Path("diffs") / f"{identifier}.patch"
        _write_patch(diffs_dir / f"{identifier}.patch", (("COMMIT", patch),))
        files.append(
            {
                "id": identifier,
                "path": change.path,
                "previous_path": change.old_path,
                "changes": {"commit": [change.as_dict()]},
                "diff": diff_rel.as_posix(),
            }
        )
    manifest: dict[str, object] = {
        "schema_version": 1,
        "mode": "commit",
        "baseline_commit": commit,
        "base_commit": base,
        "stacks": _detect_stacks(
            path
            for change in changes
            for path in (change.old_path, change.path)
            if path is not None
        ),
        "files": files,
    }
    _write_json(artifact_root / MANIFEST_NAME, manifest)
    names = [entry["path"] for entry in files]
    if names:
        print(f"Reviewing commit {commit}: {json.dumps(names, ensure_ascii=True)}")
    else:
        print("No work to review.")
    return manifest


def _group_uncommitted(
    staged: Sequence[Change], unstaged: Sequence[Change], untracked: Sequence[str]
) -> dict[str, dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}

    def add(layer: str, change: Change) -> None:
        entry = grouped.setdefault(
            change.path,
            {"path": change.path, "previous_paths": set(), "staged": [], "unstaged": [], "untracked": False},
        )
        if change.old_path is not None:
            entry["previous_paths"].add(change.old_path)  # type: ignore[union-attr]
        entry[layer].append(change)  # type: ignore[union-attr]

    for change in staged:
        add("staged", change)
    for change in unstaged:
        add("unstaged", change)
    for path in untracked:
        entry = grouped.setdefault(
            path,
            {"path": path, "previous_paths": set(), "staged": [], "unstaged": [], "untracked": False},
        )
        entry["untracked"] = True
    return grouped


def _untracked_paths(repo: Path) -> list[str]:
    output = _git(repo, "ls-files", "--others", "--exclude-standard", "-z")
    return [_decode_path(value) for value in output.split(b"\0") if value]


def _untracked_patch(repo: Path, repo_path: str) -> bytes:
    return _git(
        repo,
        "diff",
        "--no-index",
        "--binary",
        "--full-index",
        "--",
        os.devnull,
        repo_path,
        allowed_codes=(0, 1),
    )


def _capture_uncommitted(repo: Path) -> dict[str, object]:
    staged = _name_status(repo, "diff", "--cached")
    unstaged = _name_status(repo, "diff")
    untracked = _untracked_paths(repo)
    grouped = _group_uncommitted(staged, unstaged, untracked)
    artifact_root, diffs_dir = _prepare_artifacts(repo)
    files: list[dict[str, object]] = []
    for number, repo_path in enumerate(sorted(grouped), start=1):
        grouped_entry = grouped[repo_path]
        identifier = f"{number:04d}"
        previous_paths = sorted(grouped_entry["previous_paths"])
        pathspecs = [*previous_paths, repo_path]
        sections: list[tuple[str, bytes]] = []
        if grouped_entry["staged"]:
            sections.append(
                (
                    "STAGED",
                    _git(repo, "diff", "--cached", "--binary", "--full-index", "--", *pathspecs),
                )
            )
        if grouped_entry["unstaged"]:
            sections.append(("UNSTAGED", _git(repo, "diff", "--binary", "--full-index", "--", *pathspecs)))
        if grouped_entry["untracked"]:
            sections.append(("UNTRACKED", _untracked_patch(repo, repo_path)))
        diff_rel = Path("diffs") / f"{identifier}.patch"
        _write_patch(diffs_dir / f"{identifier}.patch", sections)
        files.append(
            {
                "id": identifier,
                "path": repo_path,
                "previous_paths": previous_paths,
                "changes": {
                    "staged": [change.as_dict() for change in grouped_entry["staged"]],
                    "unstaged": [change.as_dict() for change in grouped_entry["unstaged"]],
                    "untracked": bool(grouped_entry["untracked"]),
                },
                "diff": diff_rel.as_posix(),
            }
        )
    manifest: dict[str, object] = {
        "schema_version": 1,
        "mode": "uncommitted",
        "baseline_commit": None,
        "stacks": _detect_stacks(
            path
            for repo_path, grouped_entry in grouped.items()
            for path in (*grouped_entry["previous_paths"], repo_path)
        ),
        "files": files,
    }
    _write_json(artifact_root / MANIFEST_NAME, manifest)
    names = [entry["path"] for entry in files]
    if names:
        print(f"Reviewing uncommitted files: {json.dumps(names, ensure_ascii=True)}")
    else:
        print("No work to review.")
    return manifest


def _load_manifest(repo: Path) -> dict[str, object]:
    path = _artifact_root(repo) / MANIFEST_NAME
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ChoreyDiffError(f"missing manifest: {path}") from error
    if (
        not isinstance(value, dict)
        or not isinstance(value.get("files"), list)
        or not isinstance(value.get("stacks"), list)
        or not all(isinstance(stack, str) for stack in value["stacks"])
    ):
        raise ChoreyDiffError("invalid chorey-diff manifest")
    return value


def _remove_workspace_path(path: Path) -> None:
    try:
        file_stat = path.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISDIR(file_stat.st_mode) and not stat.S_ISLNK(file_stat.st_mode):
        try:
            path.rmdir()
        except OSError as error:
            raise ChoreyDiffError(f"refusing to recursively remove directory: {path}") from error
    else:
        path.unlink()


def _commit_contains(repo: Path, commit: str, repo_path: str) -> bool:
    output = _git(repo, "ls-tree", "-z", commit, "--", repo_path)
    return bool(output)


def _restore_commit(repo: Path, commit: str, repo_path: str) -> None:
    workspace_path = _safe_workspace_path(repo, repo_path)
    if _commit_contains(repo, commit, repo_path):
        _git(repo, "restore", f"--source={commit}", "--worktree", "--", repo_path)
    else:
        _remove_workspace_path(workspace_path)


def _index_contains(repo: Path, repo_path: str) -> bool:
    output = _git(repo, "ls-files", "--stage", "-z", "--", repo_path)
    for record in output.split(b"\0"):
        if not record:
            continue
        _, separator, returned_path = record.partition(b"\t")
        if not separator:
            raise ChoreyDiffError(f"invalid index entry for {repo_path}")
        if os.fsdecode(returned_path) == repo_path:
            return True
    return False


def _restore_index(repo: Path, repo_path: str) -> None:
    workspace_path = _safe_workspace_path(repo, repo_path)
    if not _index_contains(repo, repo_path):
        _remove_workspace_path(workspace_path)
        return
    _git(repo, "restore", "--worktree", "--", repo_path)


def _restore(repo: Path, paths: Sequence[str]) -> None:
    manifest = _load_manifest(repo)
    entries = {entry.get("path"): entry for entry in manifest["files"] if isinstance(entry, dict)}
    restore_paths: list[str] = []
    for path in paths:
        repo_path = _normalize_repo_path(path)
        if repo_path not in restore_paths:
            restore_paths.append(repo_path)
        entry = entries.get(repo_path)
        if isinstance(entry, dict):
            previous_paths = entry.get("previous_paths", [])
            if not isinstance(previous_paths, list) or not all(
                isinstance(previous_path, str) for previous_path in previous_paths
            ):
                raise ChoreyDiffError(f"invalid previous paths for {repo_path}")
            for previous_path in previous_paths:
                normalized_previous = _normalize_repo_path(previous_path)
                if normalized_previous not in restore_paths:
                    restore_paths.append(normalized_previous)
    mode = manifest.get("mode")
    if mode == "commit":
        commit = manifest.get("baseline_commit")
        if not isinstance(commit, str):
            raise ChoreyDiffError("commit manifest has no baseline_commit")
        for repo_path in restore_paths:
            _restore_commit(repo, commit, repo_path)
    elif mode == "uncommitted":
        for repo_path in restore_paths:
            _restore_index(repo, repo_path)
    else:
        raise ChoreyDiffError(f"unknown manifest mode: {mode!r}")
    print(f"Restored review baseline files: {json.dumps(restore_paths, ensure_ascii=True)}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    capture = subparsers.add_parser("capture", help="capture the review scope")
    capture.add_argument("--baseline", help="checkpoint commit to review")
    restore = subparsers.add_parser("restore", help="restore touched paths to the selected baseline")
    restore.add_argument("--path", action="append", required=True, dest="paths")
    subparsers.add_parser("discard", help="remove bin/crew_diff")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        repo = _repo_root(Path.cwd())
        if args.command == "capture":
            _discard(repo)
            if args.baseline:
                _capture_commit(repo, args.baseline)
            else:
                _capture_uncommitted(repo)
        elif args.command == "restore":
            _restore(repo, args.paths)
        elif args.command == "discard":
            _discard(repo)
            print("Discarded chorey-diff artifacts.")
        return 0
    except (ChoreyDiffError, OSError) as error:
        print(f"chorey-diff: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
