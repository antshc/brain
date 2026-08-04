"""Test double for GitCli — returns configured outcomes without spawning subprocesses."""

from pathlib import Path

from ..git_cli import GitCli, GitCommandResult, WorktreeAddResult


class FakeGitCli(GitCli):
    """In-memory GitCli substitute for use in handler tests.

    Usage::

        git = FakeGitCli(current_branch_output="main", pull_success=False, conflicted_files_output=["a.py"])
        result = create_or_reuse_worktree(repo_path, "main", "feature", git=git)
    """

    def __init__(
        self,
        *,
        current_branch_output: str = "",
        ref_exists_map: dict[str, bool] | None = None,
        pull_success: bool = True,
        pull_stderr: str = "",
        merge_success: bool = True,
        merge_stderr: str = "",
        worktree_add_result: WorktreeAddResult | None = None,
        conflicted_files_output: list[str] | None = None,
    ) -> None:
        self._current_branch_output = current_branch_output
        self._ref_exists_map = ref_exists_map or {}
        self._pull_success = pull_success
        self._pull_stderr = pull_stderr
        self._merge_success = merge_success
        self._merge_stderr = merge_stderr
        self._worktree_add_result = worktree_add_result or WorktreeAddResult(
            success=True, already_exists=False, stderr=""
        )
        self._conflicted_files_output = conflicted_files_output or []
        self.fetch_calls: list[Path] = []
        self.pull_calls: list[Path] = []
        self.merge_calls: list[tuple[Path, str]] = []
        self.worktree_add_calls: list[tuple[Path, Path, str, str]] = []

    def fetch_all_prune(self, cwd: Path) -> None:
        self.fetch_calls.append(cwd)

    def pull(self, cwd: Path) -> GitCommandResult:
        self.pull_calls.append(cwd)
        return GitCommandResult(success=self._pull_success, stderr=self._pull_stderr)

    def merge(self, cwd: Path, ref: str) -> GitCommandResult:
        self.merge_calls.append((cwd, ref))
        return GitCommandResult(success=self._merge_success, stderr=self._merge_stderr)

    def current_branch(self, cwd: Path) -> str:
        return self._current_branch_output

    def ref_exists(self, cwd: Path, ref: str) -> bool:
        return self._ref_exists_map.get(ref, False)

    def worktree_add(self, cwd: Path, worktree_path: Path, branch: str, base_ref: str) -> WorktreeAddResult:
        self.worktree_add_calls.append((cwd, worktree_path, branch, base_ref))
        return self._worktree_add_result

    def conflicted_files(self, cwd: Path) -> list[str]:
        return self._conflicted_files_output
