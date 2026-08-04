"""Actualize Branch use case: brings the current branch up to date with remote and the target branch."""

from pathlib import Path

from ...domain.errors import GitCommandFailedError, MergeConflictError
from ...infrastructure.git_cli import GitCli


def actualize_branch(
    cwd: Path,
    target_branch: str,
    *,
    git: GitCli | None = None,
) -> None:
    """Fetch, pull, and merge `origin/<target_branch>` into the branch checked out at `cwd`.

    Raises MergeConflictError (carrying the conflicting file list) if the pull or merge
    hits an actual merge conflict. Never resolves conflicts itself — resolution happens
    in-context by the caller once the conflicting files are known.

    Raises GitCommandFailedError (carrying the command name and its stderr) if the pull
    or merge fails for a reason other than a merge conflict — e.g. missing upstream
    tracking information, a network, or an auth failure — determined by no conflicted
    files being present after the failure.
    """
    git = git or GitCli()

    git.fetch_all_prune(cwd)

    pull_result = git.pull(cwd)
    if not pull_result.success:
        conflicted_files = git.conflicted_files(cwd)
        if conflicted_files:
            raise MergeConflictError(conflicted_files)
        raise GitCommandFailedError("pull", pull_result.stderr)

    merge_result = git.merge(cwd, f"origin/{target_branch}")
    if not merge_result.success:
        conflicted_files = git.conflicted_files(cwd)
        if conflicted_files:
            raise MergeConflictError(conflicted_files)
        raise GitCommandFailedError("merge", merge_result.stderr)
