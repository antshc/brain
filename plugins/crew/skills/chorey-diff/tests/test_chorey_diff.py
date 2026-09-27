import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


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
        "files": [],
    }
    assert (repo / "bin" / "crew_diff" / "diffs").is_dir()
    assert not (repo / "bin" / "crew_diff" / "snapshots").exists()


def test_uncommitted_capture_keeps_layers_and_restores_staged_versions(tmp_path):
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

    (repo / "mixed.txt").write_text("review edit", encoding="utf-8")
    (repo / "space name.bin").write_bytes(b"review edit")
    (repo / "cancelled.txt").write_text("review recreated", encoding="utf-8")
    (repo / "rename-target.txt").write_text("review edit", encoding="utf-8")
    invoke(
        repo,
        "restore",
        "--path",
        "mixed.txt",
        "--path",
        "space name.bin",
        "--path",
        "cancelled.txt",
        "--path",
        "deleted.txt",
        "--path",
        "rename-target.txt",
        "--path",
        "unstaged-rename-target.txt",
        "--path",
        "unstaged-rename-source.txt",
    )

    assert (repo / "mixed.txt").read_bytes() == b"staged\r\n"
    assert not (repo / "space name.bin").exists()
    assert (repo / "cancelled.txt").read_text(encoding="utf-8") == "staged addition\n"
    assert (repo / "deleted.txt").read_text(encoding="utf-8") == "delete me\n"
    assert (repo / "rename-target.txt").read_text(encoding="utf-8") == "rename me\n"
    assert not (repo / "unstaged-rename-target.txt").exists()
    assert (repo / "unstaged-rename-source.txt").read_text(encoding="utf-8") == "unstaged rename\n"
    assert git(repo, "diff", "--cached", "--binary") == index_before
    assert git(repo, "diff", "--binary") == b""


def test_commit_capture_handles_rename_delete_binary_and_restore(tmp_path):
    repo = tmp_path / "repo"
    initialize(repo)
    (repo / ".gitignore").write_text("bin/\n", encoding="utf-8")
    (repo / "old.txt").write_bytes(b"rename me\n")
    (repo / "deleted.txt").write_bytes(b"delete me\n")
    commit_all(repo, "base")
    git(repo, "mv", "old.txt", "renamed.txt")
    (repo / "deleted.txt").unlink()
    (repo / "space name.bin").write_bytes(b"\x00checkpoint\xff")
    checkpoint = commit_all(repo)

    result = invoke(repo, "capture", "--baseline", checkpoint)
    manifest = load_manifest(repo)
    entries = entries_by_path(manifest)

    assert f"Reviewing commit {checkpoint}:" in result.stdout.decode()
    assert manifest["mode"] == "commit"
    assert set(entries) == {"deleted.txt", "renamed.txt", "space name.bin"}
    assert entries["renamed.txt"]["previous_path"] == "old.txt"
    assert all("snapshot" not in entry for entry in entries.values())

    (repo / "renamed.txt").write_text("review edit", encoding="utf-8")
    (repo / "space name.bin").write_bytes(b"review edit")
    (repo / "deleted.txt").write_text("review recreated", encoding="utf-8")
    invoke(
        repo,
        "restore",
        "--path",
        "renamed.txt",
        "--path",
        "space name.bin",
        "--path",
        "deleted.txt",
    )

    assert (repo / "renamed.txt").read_bytes() == b"rename me\n"
    assert (repo / "space name.bin").read_bytes() == b"\x00checkpoint\xff"
    assert not (repo / "deleted.txt").exists()


def test_restore_related_paths_uses_commit_baseline(tmp_path):
    repo = tmp_path / "repo"
    initialize(repo)
    (repo / ".gitignore").write_text("bin/\n", encoding="utf-8")
    (repo / "changed.txt").write_text("base\n", encoding="utf-8")
    (repo / "related.txt").write_text("committed\n", encoding="utf-8")
    commit_all(repo, "base")
    (repo / "changed.txt").write_text("checkpoint\n", encoding="utf-8")
    checkpoint = commit_all(repo, "checkpoint")
    invoke(repo, "capture", "--baseline", checkpoint)
    assert "related.txt" not in entries_by_path(load_manifest(repo))

    (repo / "related.txt").write_text("review edit\n", encoding="utf-8")
    (repo / "new-related.txt").write_text("review addition\n", encoding="utf-8")
    invoke(repo, "restore", "--path", "related.txt", "--path", "new-related.txt")

    assert (repo / "related.txt").read_text(encoding="utf-8") == "committed\n"
    assert not (repo / "new-related.txt").exists()


def test_restore_rejects_artifact_paths(tmp_path):
    repo = tmp_path / "repo"
    initialize(repo)
    (repo / ".gitignore").write_text("bin/\n", encoding="utf-8")
    commit_all(repo)
    invoke(repo, "capture")

    result = invoke(repo, "restore", "--path", "bin/crew_diff/escape.txt", check=False)

    assert result.returncode == 1
    assert b"refusing to restore chorey-diff artifacts" in result.stderr


def test_root_commit_uses_empty_tree_and_invalid_commit_leaves_no_bundle(tmp_path):
    repo = tmp_path / "repo"
    initialize(repo)
    (repo / ".gitignore").write_text("bin/\n", encoding="utf-8")
    (repo / "root.txt").write_text("root\n", encoding="utf-8")
    root_commit = commit_all(repo, "root")

    invoke(repo, "capture", "--baseline", root_commit)
    manifest = load_manifest(repo)
    assert [entry["path"] for entry in manifest["files"]] == [".gitignore", "root.txt"]

    result = invoke(repo, "capture", "--baseline", "not-a-commit", check=False)
    assert result.returncode == 1
    assert b"chorey-diff:" in result.stderr
    assert not (repo / "bin" / "crew_diff").exists()
    assert git(repo, "status", "--porcelain") == b""


def test_staged_symlink_restores_from_index_when_supported(tmp_path):
    repo = tmp_path / "repo"
    initialize(repo)
    (repo / ".gitignore").write_text("bin/\n", encoding="utf-8")
    (repo / "target.txt").write_text("target\n", encoding="utf-8")
    commit_all(repo)
    try:
        os.symlink("target.txt", repo / "link.txt")
    except OSError:
        pytest.skip("symlinks are not available")
    git(repo, "add", "link.txt")

    invoke(repo, "capture")
    (repo / "link.txt").unlink()
    (repo / "link.txt").write_text("review replacement", encoding="utf-8")

    invoke(repo, "restore", "--path", "link.txt")

    assert (repo / "link.txt").is_symlink()
    assert os.readlink(repo / "link.txt") == "target.txt"


def test_restore_related_index_paths_and_discard_is_scoped(tmp_path):
    repo = tmp_path / "repo"
    initialize(repo)
    (repo / ".gitignore").write_text("bin/\n", encoding="utf-8")
    (repo / "tracked.txt").write_text("initial\n", encoding="utf-8")
    (repo / "related.txt").write_text("baseline\n", encoding="utf-8")
    commit_all(repo)
    (repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
    invoke(repo, "capture")
    (repo / "related.txt").write_text("review edit\n", encoding="utf-8")
    (repo / "new-related.txt").write_text("review addition\n", encoding="utf-8")
    sibling = repo / "bin" / "keep.txt"
    sibling.write_text("keep", encoding="utf-8")

    invoke(repo, "restore", "--path", "related.txt", "--path", "new-related.txt")

    assert (repo / "tracked.txt").read_text(encoding="utf-8") == "changed\n"
    assert (repo / "related.txt").read_text(encoding="utf-8") == "baseline\n"
    assert not (repo / "new-related.txt").exists()

    invoke(repo, "discard")
    assert not (repo / "bin" / "crew_diff").exists()
    assert sibling.read_text(encoding="utf-8") == "keep"
