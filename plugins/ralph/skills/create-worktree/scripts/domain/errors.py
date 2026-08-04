"""Domain errors for git worktree operations."""


class MergeConflictError(Exception):
    """Raised when a branch actualization pull/merge hits a conflict.

    Carries the list of conflicting file paths so the caller can surface
    them for manual, in-context resolution — this module never resolves
    conflicts itself.
    """

    def __init__(self, conflicting_files: list[str]) -> None:
        self.conflicting_files = conflicting_files
        super().__init__(f"Merge conflict in: {', '.join(conflicting_files) or '(unknown files)'}")


class WorktreeCreationError(Exception):
    """Raised when `git worktree add` fails for a reason other than the worktree already existing."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class GitCommandFailedError(Exception):
    """Raised when a branch actualization `pull` or `merge` fails for a reason other than a merge conflict.

    E.g. missing upstream tracking information, network, or auth failures. Carries the
    failing command's name and raw stderr so the caller can surface the real underlying
    error instead of misreporting it as a MergeConflictError with an empty file list.
    """

    def __init__(self, command: str, stderr: str) -> None:
        self.command = command
        self.stderr = stderr
        super().__init__(f"git {command} failed: {stderr.strip() or '(no error output)'}")
