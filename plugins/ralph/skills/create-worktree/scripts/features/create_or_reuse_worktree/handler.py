"""Create Or Reuse Worktree use case: creates an isolated git worktree for a feature branch,
or reuses one that already exists, then actualizes the branch as needed.
"""

from pathlib import Path

from ...domain.errors import WorktreeCreationError
from ...domain.worktree_result import WorktreeResult
from ...infrastructure.git_cli import GitCli
from ..actualize_branch.handler import actualize_branch


def create_or_reuse_worktree(
    codebase_repo_path: Path,
    target_branch: str,
    feature_branch: str,
    *,
    git: GitCli | None = None,
) -> WorktreeResult:
    """Create or reuse the worktree for `feature_branch`, based off `codebase_repo_path`.

    - If the current branch already equals `feature_branch`, skip worktree creation,
      actualize the branch in place, and report the current directory as the worktree path.
    - Otherwise, create a new worktree at `<codebase_repo_path>.worktrees/<feature_branch>`,
      based on `origin/<feature_branch>` if it exists, else `origin/<target_branch>`.
    - If a worktree already exists at that path, reuse it and actualize the branch.
    - Any other worktree-creation failure raises WorktreeCreationError.

    Raises MergeConflictError (via actualize_branch) if branch actualization hits a conflict.
    """
    git = git or GitCli()
    codebase_repo_path = Path(codebase_repo_path)

    current_branch = git.current_branch(codebase_repo_path)
    if current_branch == feature_branch:
        actualize_branch(codebase_repo_path, target_branch, git=git)
        return WorktreeResult(
            codebase_repo_path=str(codebase_repo_path),
            worktree_path=str(codebase_repo_path),
            branch=current_branch,
            target_branch=target_branch,
        )

    worktree_path = codebase_repo_path.parent / f"{codebase_repo_path.name}.worktrees" / feature_branch
    worktree_path.parent.mkdir(parents=True, exist_ok=True)

    git.fetch_all_prune(codebase_repo_path)
    base_ref = (
        f"origin/{feature_branch}" if git.ref_exists(codebase_repo_path, f"origin/{feature_branch}")
        else f"origin/{target_branch}"
    )

    add_result = git.worktree_add(codebase_repo_path, worktree_path, feature_branch, base_ref)
    if not add_result.success:
        if not add_result.already_exists:
            raise WorktreeCreationError(add_result.stderr)
        actualize_branch(worktree_path, target_branch, git=git)

    return WorktreeResult(
        codebase_repo_path=str(codebase_repo_path),
        worktree_path=str(worktree_path),
        branch=feature_branch,
        target_branch=target_branch,
    )
