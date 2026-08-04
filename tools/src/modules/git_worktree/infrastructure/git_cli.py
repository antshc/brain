"""Thin wrapper around the `git` CLI for worktree and branch-actualization operations."""

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class WorktreeAddResult:
    """Outcome of a `git worktree add` invocation."""

    success: bool
    already_exists: bool
    stderr: str


@dataclass(frozen=True)
class GitCommandResult:
    """Outcome of a `git pull` or `git merge` invocation.

    Carries stderr alongside success so the caller can distinguish an actual merge
    conflict from any other failure (e.g. missing upstream tracking, network/auth
    failure) and surface the real error instead of a misleading empty conflict list.
    """

    success: bool
    stderr: str


class GitCli:
    """Executes `git` commands needed for worktree create/reuse and branch actualization."""

    def fetch_all_prune(self, cwd: Path) -> None:
        """Run `git fetch --all --prune`. Raises on failure."""
        subprocess.run(["git", "fetch", "--all", "--prune"], cwd=cwd, capture_output=True, text=True, check=True)

    def pull(self, cwd: Path) -> GitCommandResult:
        """Run `git pull`. Returns the outcome, including stderr on failure (e.g. conflicts)."""
        result = subprocess.run(["git", "pull"], cwd=cwd, capture_output=True, text=True, check=False)
        return GitCommandResult(success=result.returncode == 0, stderr=result.stderr)

    def merge(self, cwd: Path, ref: str) -> GitCommandResult:
        """Run `git merge <ref>`. Returns the outcome, including stderr on failure (e.g. conflicts)."""
        result = subprocess.run(["git", "merge", ref], cwd=cwd, capture_output=True, text=True, check=False)
        return GitCommandResult(success=result.returncode == 0, stderr=result.stderr)

    def current_branch(self, cwd: Path) -> str:
        """Run `git branch --show-current` and return the branch name (empty if detached)."""
        result = subprocess.run(
            ["git", "branch", "--show-current"], cwd=cwd, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()

    def ref_exists(self, cwd: Path, ref: str) -> bool:
        """Run `git rev-parse --verify --quiet <ref>` and return whether it resolves."""
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", ref], cwd=cwd, capture_output=True, text=True, check=False
        )
        return result.returncode == 0

    def worktree_add(self, cwd: Path, worktree_path: Path, branch: str, base_ref: str) -> WorktreeAddResult:
        """Run `git worktree add -b <branch> <worktree_path> <base_ref>`.

        Distinguishes an "already exists" failure (either the branch or the worktree
        path is already registered) from any other failure, so the caller can reuse
        an existing worktree instead of treating it as an error.
        """
        result = subprocess.run(
            ["git", "worktree", "add", "-b", branch, str(worktree_path), base_ref],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        already_exists = result.returncode != 0 and "already exists" in result.stderr.lower()
        return WorktreeAddResult(success=result.returncode == 0, already_exists=already_exists, stderr=result.stderr)

    def conflicted_files(self, cwd: Path) -> list[str]:
        """Run `git diff --name-only --diff-filter=U` and return the conflicting file paths."""
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return [line for line in result.stdout.splitlines() if line]
