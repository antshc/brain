"""Feature: Deterministic Source Repository development."""

from pathlib import Path
import subprocess


SCRIPT = Path(__file__).with_name("prepare_worktree.sh")
RESOLVER = Path(__file__).with_name("resolve_source_repository.sh")


def git(*arguments: str, cwd: Path | None = None) -> str:
    return subprocess.run(["git", *arguments], cwd=cwd, check=True, text=True, capture_output=True).stdout


def initialize_repository(path: Path, remote: Path | None = None) -> None:
    git("init", "--initial-branch", "main", str(path))
    git("config", "user.email", "test@example.com", cwd=path)
    git("config", "user.name", "Test User", cwd=path)
    (path / "README.md").write_text("initial\n")
    git("add", "README.md", cwd=path)
    git("commit", "-m", "initial", cwd=path)
    if remote is not None:
        git("remote", "add", "origin", str(remote), cwd=path)
        git("push", "-u", "origin", "main", cwd=path)


def run_worktree(harness_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(SCRIPT), str(harness_root), "main", "feature/test"], text=True, capture_output=True)


def resolve_source_repository(harness_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(RESOLVER), str(harness_root)], text=True, capture_output=True)


def expected_output(source_repo: Path) -> str:
    return f"SOURCE_REPO: {source_repo}\nWORKTREE_PATH: {source_repo}.worktrees/feature/test\nBRANCH: feature/test\nTARGET_BRANCH: main\n"


def test_selects_harness_root_when_workspace_is_absent(tmp_path: Path) -> None:
    """Scenario: Direct-source Harness Root selects itself."""
    remote = tmp_path / "remote.git"
    git("init", "--bare", str(remote))
    harness_root = tmp_path / "harness"
    initialize_repository(harness_root, remote)

    result = run_worktree(harness_root)

    assert result.returncode == 0
    assert result.stdout == expected_output(harness_root)
    assert result.stderr == ""


def test_source_repository_resolver_selects_the_harness_root_without_a_workspace(tmp_path: Path) -> None:
    """Scenario: Source Repository resolver selects the Harness Root without a workspace."""
    harness_root = tmp_path / "harness"
    initialize_repository(harness_root)

    result = resolve_source_repository(harness_root)

    assert result.returncode == 0
    assert result.stdout == f"{harness_root}\n"
    assert result.stderr == ""


def test_selects_only_direct_workspace_child_repository(tmp_path: Path) -> None:
    """Scenario: Wrapped Harness Root selects its sole direct child repository."""
    harness_root = tmp_path / "harness"
    initialize_repository(harness_root)
    remote = tmp_path / "remote.git"
    git("init", "--bare", str(remote))
    source_repo = harness_root / "workspace" / "source"
    source_repo.parent.mkdir()
    initialize_repository(source_repo, remote)

    result = run_worktree(harness_root)

    assert result.returncode == 0
    assert result.stdout == expected_output(source_repo)
    assert result.stderr == ""


def test_source_repository_resolver_selects_the_sole_direct_workspace_child(tmp_path: Path) -> None:
    """Scenario: Source Repository resolver selects the sole direct workspace child."""
    harness_root = tmp_path / "harness"
    initialize_repository(harness_root)
    source_repo = harness_root / "workspace" / "source"
    source_repo.parent.mkdir()
    initialize_repository(source_repo)

    result = resolve_source_repository(harness_root)

    assert result.returncode == 0
    assert result.stdout == f"{source_repo}\n"
    assert result.stderr == ""


def test_rejects_workspace_without_a_direct_child_repository(tmp_path: Path) -> None:
    """Scenario: Wrapped Harness Root without a source repository fails closed."""
    harness_root = tmp_path / "harness"
    initialize_repository(harness_root)
    workspace = harness_root / "workspace"
    workspace.mkdir()
    (workspace / "nested").mkdir()
    initialize_repository(workspace / "nested" / "source")

    result = run_worktree(harness_root)

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == f"No Source Repository found in workspace: {workspace}\n"


def test_source_repository_resolver_rejects_a_workspace_without_a_direct_child_repository(tmp_path: Path) -> None:
    """Scenario: Source Repository resolver rejects a workspace without a direct child repository."""
    harness_root = tmp_path / "harness"
    initialize_repository(harness_root)
    workspace = harness_root / "workspace"
    workspace.mkdir()

    result = resolve_source_repository(harness_root)

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == f"No Source Repository found in workspace: {workspace}\n"


def test_rejects_multiple_direct_workspace_child_repositories(tmp_path: Path) -> None:
    """Scenario: Wrapped Harness Root with multiple source repositories is ambiguous."""
    harness_root = tmp_path / "harness"
    initialize_repository(harness_root)
    workspace = harness_root / "workspace"
    workspace.mkdir()
    initialize_repository(workspace / "first")
    initialize_repository(workspace / "second")

    result = run_worktree(harness_root)

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == f"Source Repository selection is ambiguous in workspace: {workspace}\n"


def test_source_repository_resolver_rejects_an_ambiguous_workspace(tmp_path: Path) -> None:
    """Scenario: Source Repository resolver rejects an ambiguous workspace."""
    harness_root = tmp_path / "harness"
    initialize_repository(harness_root)
    workspace = harness_root / "workspace"
    workspace.mkdir()
    initialize_repository(workspace / "first")
    initialize_repository(workspace / "second")

    result = resolve_source_repository(harness_root)

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == f"Source Repository selection is ambiguous in workspace: {workspace}\n"


def test_reuses_and_actualizes_an_existing_worktree(tmp_path: Path) -> None:
    """Scenario: Existing feature worktree is reused and merged with its target branch."""
    remote = tmp_path / "remote.git"
    git("init", "--bare", str(remote))
    harness_root = tmp_path / "harness"
    initialize_repository(harness_root, remote)
    first_result = run_worktree(harness_root)
    assert first_result.returncode == 0
    (harness_root / "README.md").write_text("updated\n")
    git("add", "README.md", cwd=harness_root)
    git("commit", "-m", "updated", cwd=harness_root)
    git("push", cwd=harness_root)

    result = run_worktree(harness_root)

    assert result.returncode == 0
    assert result.stdout == expected_output(harness_root)
    assert result.stderr == ""
    assert git("log", "-1", "--format=%s", cwd=harness_root.with_name("harness.worktrees") / "feature" / "test") == "updated\n"