#!/usr/bin/env python3
"""Entry point for the `create-worktree` skill.

Creates or reuses an isolated git worktree for a feature branch, based off the
target branch, then actualizes the branch as needed. Intended as a drop-in
replacement for create-worktree's previously embedded bash.

Usage:
    python create_worktree.py <codebase-repo-path> <target-branch> <feature-branch>

Arguments:
    codebase-repo-path  Path to the codebase repo (caller-resolved; never re-derived here).
    target-branch       Branch to base a fresh worktree on / merge into an existing one.
    feature-branch      Branch the worktree is created for or reused from.

Output (stdout, on success):
    CODEBASE_REPO_PATH: <path>
    WORKTREE_PATH: <path>
    BRANCH: <branch>
    TARGET_BRANCH: <target-branch>

Exit codes:
    0 - success
    1 - usage / argument error
    2 - merge conflict during branch actualization (conflicting files printed to stderr)
    3 - worktree creation failed for a reason other than the worktree already existing
    4 - git pull or merge failed during branch actualization for a reason other than a
        merge conflict (e.g. missing upstream tracking, network, or auth failure); the
        real git error is printed to stderr
"""

import importlib
import sys
from pathlib import Path

# This file is synced as-is (see .githooks/pre-commit) alongside its sibling
# domain/features/infrastructure packages. That enclosing directory is named
# "git_worktree" in tools/src/modules/ but "scripts" once synced into the
# create-worktree skill folder -- import the sibling packages by this
# directory's own runtime name rather than hardcoding one, since the two
# locations differ.
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR.parent))
_PACKAGE_NAME = _SCRIPT_DIR.name

_handler_module = importlib.import_module(f"{_PACKAGE_NAME}.features.create_or_reuse_worktree.handler")
_errors_module = importlib.import_module(f"{_PACKAGE_NAME}.domain.errors")

create_or_reuse_worktree = _handler_module.create_or_reuse_worktree
MergeConflictError = _errors_module.MergeConflictError
WorktreeCreationError = _errors_module.WorktreeCreationError
GitCommandFailedError = _errors_module.GitCommandFailedError

_USAGE = "Usage: create_worktree.py <codebase-repo-path> <target-branch> <feature-branch>"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if len(argv) != 3:
        print(_USAGE, file=sys.stderr)
        return 1

    codebase_repo_path, target_branch, feature_branch = argv
    repo_path = Path(codebase_repo_path)
    if not repo_path.is_dir():
        print(f"Error: codebase-repo-path does not exist: {codebase_repo_path}", file=sys.stderr)
        return 1

    try:
        result = create_or_reuse_worktree(repo_path, target_branch, feature_branch)
    except MergeConflictError as error:
        print("Error: merge conflict during branch actualization. Conflicting files:", file=sys.stderr)
        for conflicting_path in error.conflicting_files:
            print(conflicting_path, file=sys.stderr)
        return 2
    except WorktreeCreationError as error:
        print(f"Error: worktree creation failed: {error.message}", file=sys.stderr)
        return 3
    except GitCommandFailedError as error:
        print(f"Error: git {error.command} failed: {error.stderr.strip() or '(no error output)'}", file=sys.stderr)
        return 4

    print(f"CODEBASE_REPO_PATH: {result.codebase_repo_path}")
    print(f"WORKTREE_PATH: {result.worktree_path}")
    print(f"BRANCH: {result.branch}")
    print(f"TARGET_BRANCH: {result.target_branch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
