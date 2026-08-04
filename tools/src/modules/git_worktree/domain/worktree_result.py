"""Result of a create-or-reuse worktree operation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WorktreeResult:
    """Outcome reported back to the caller, matching the skill's documented output shape."""

    codebase_repo_path: str
    worktree_path: str
    branch: str
    target_branch: str
