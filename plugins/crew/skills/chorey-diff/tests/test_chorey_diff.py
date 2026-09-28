import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "chorey_diff.py"


def run(command, cwd, *, check=True):
    result = subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(result.stderr.decode("utf-8", errors="replace"))
    return result


def git(repo, *args):
    return run(("git", *args), repo).stdout


def invoke(repo, *args, check=True):
    return run((sys.executable, str(SCRIPT), *args), repo, check=check)


def initialize(repo):
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "chorey@example.invalid")
    git(repo, "config", "user.name", "Chorey Test")
    git(repo, "config", "core.autocrlf", "false")


def commit_all(repo, message="checkpoint"):
    git(repo, "add", "-A")
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD").decode("ascii").strip()


def load_manifest(repo):
    return json.loads((repo / "bin" / "crew_diff" / "_manifest.json").read_text(encoding="utf-8"))


def entries_by_path(manifest):
    return {entry["path"]: entry for entry in manifest["files"]}


def test_empty_uncommitted_capture_writes_empty_bundle(tmp_path):
    repo = tmp_path / "repo"
    initialize(repo)
    (repo / "tracked.txt").write_text("initial\n", encoding="utf-8")
    commit_all(repo)

    result = invoke(repo, "capture")

    assert result.stdout.decode().strip() == "No work to review."
    assert load_manifest(repo) == {
        "schema_version": 1,
        "mode": "uncommitted",
        "baseline_commit": None,
        "stacks": [],
        "files": [],
    }
    assert (repo / "bin" / "crew_diff" / "diffs").is_dir()
    assert not (repo / "bin" / "crew_diff" / "snapshots").exists()


def test_uncommitted_capture_detects_sorted_aggregate_stacks(tmp_path):
    repo = tmp_path / "repo"
    initialize(repo)
    (repo / ".gitignore").write_text("bin/\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("initial guidance\n", encoding="utf-8")
    commit_all(repo)

    (repo / "AGENTS.md").unlink()
    (repo / "rules").mkdir()
    (repo / "rules" / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
    (repo / "rules" / "helper.prompt.md").write_text("prompt\n", encoding="utf-8")
    (repo / "rules" / "review.instructions.md").write_text("instructions\n", encoding="utf-8")
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('hello')\n", encoding="utf-8")
    (repo / "src" / "App.cs").write_text("class App {}\n", encoding="utf-8")
    (repo / "requirements-dev.txt").write_text("pytest\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    (repo / "Pipfile").write_text("[packages]\n", encoding="utf-8")
    (repo / "Directory.Build.props").write_text("<Project />\n", encoding="utf-8")
    (repo / "Directory.Packages.props").write_text("<Project />\n", encoding="utf-8")
    (repo / "notes.rst").write_text("unmatched\n", encoding="utf-8")

    invoke(repo, "capture")

    assert load_manifest(repo)["stacks"] == ["ai", "dotnet", "py"]


def test_unmatched_changed_paths_produce_empty_stacks(tmp_path):
    repo = tmp_path / "repo"
    initialize(repo)
    (repo / ".gitignore").write_text("bin/\n", encoding="utf-8")
    (repo / "notes.rst").write_text("initial\n", encoding="utf-8")
    commit_all(repo)
    (repo / "notes.rst").write_text("changed\n", encoding="utf-8")

    invoke(repo, "capture")

    assert load_manifest(repo)["stacks"] == []


def test_uncommitted_capture_keeps_layers(tmp_path):
    repo = tmp_path / "repo"
    initialize(repo)
    (repo / ".gitignore").write_text("ignored.txt\nbin/\n", encoding="utf-8")
    (repo / "mixed.txt").write_text("initial\n", encoding="utf-8")
    (repo / "deleted.txt").write_text("delete me\n", encoding="utf-8")
    (repo / "rename-source.txt").write_text("rename me\n", encoding="utf-8")
    (repo / "unstaged-rename-source.txt").write_text("unstaged rename\n", encoding="utf-8")
    commit_all(repo)

    (repo / "mixed.txt").write_text("staged\n", encoding="utf-8")
    git(repo, "add", "mixed.txt")
    (repo / "mixed.txt").write_bytes(b"working\r\n")
    (repo / "deleted.txt").unlink()
    (repo / "space name.bin").write_bytes(b"\x00\x01new\xff")
    (repo / "ignored.txt").write_text("ignored", encoding="utf-8")
    (repo / "cancelled.txt").write_text("staged addition\n", encoding="utf-8")
    git(repo, "add", "cancelled.txt")
    (repo / "cancelled.txt").unlink()
    git(repo, "mv", "rename-source.txt", "rename-target.txt")
    (repo / "rename-target.txt").write_text("renamed and edited\n", encoding="utf-8")
    (repo / "unstaged-rename-source.txt").rename(repo / "unstaged-rename-target.txt")
    index_before = git(repo, "diff", "--cached", "--binary")
    status_before = git(repo, "status", "--porcelain=v1", "-z")

    result = invoke(repo, "capture")
    manifest = load_manifest(repo)
    entries = entries_by_path(manifest)

    assert "Reviewing uncommitted files:" in result.stdout.decode()
    assert set(entries) == {
        "cancelled.txt",
        "deleted.txt",
        "mixed.txt",
        "rename-target.txt",
        "space name.bin",
        "unstaged-rename-source.txt",
        "unstaged-rename-target.txt",
    }
    assert "ignored.txt" not in entries
    mixed_patch = (repo / "bin" / "crew_diff" / entries["mixed.txt"]["diff"]).read_bytes()
    assert b"=== STAGED ===" in mixed_patch
    assert b"=== UNSTAGED ===" in mixed_patch
    untracked_patch = (repo / "bin" / "crew_diff" / entries["space name.bin"]["diff"]).read_bytes()
    assert b"=== UNTRACKED ===" in untracked_patch
    assert entries["rename-target.txt"]["previous_paths"] == ["rename-source.txt"]
    assert "snapshot" not in entries["space name.bin"]
    assert "previous_snapshots" not in entries["rename-target.txt"]
    assert git(repo, "diff", "--cached", "--binary") == index_before
    assert git(repo, "status", "--porcelain=v1", "-z") == status_before


def test_discard_is_scoped_to_bundle(tmp_path):
    repo = tmp_path / "repo"
    initialize(repo)
    (repo / ".gitignore").write_text("bin/\n", encoding="utf-8")
    (repo / "tracked.txt").write_text("initial\n", encoding="utf-8")
    commit_all(repo)
    (repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
    invoke(repo, "capture")
    sibling = repo / "bin" / "keep.txt"
    sibling.write_text("keep", encoding="utf-8")

    invoke(repo, "discard")

    assert not (repo / "bin" / "crew_diff").exists()
    assert sibling.read_text(encoding="utf-8") == "keep"
