from pathlib import Path
import shutil
import subprocess


SCRIPT = Path(__file__).with_name("harness_path.py")


def git_init(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)


def install_script(outer: Path) -> Path:
    target = outer / ".github" / "skills" / "call-harness" / "scripts" / "harness_path.py"
    target.parent.mkdir(parents=True)
    shutil.copy2(SCRIPT, target)
    return target


def run(script: Path, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(script), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def test_nested_repo_does_not_capture_harness_resolution(tmp_path: Path) -> None:
    outer = tmp_path / "harness"
    nested = outer / "workspace" / "foo"
    git_init(outer)
    git_init(nested)
    script = install_script(outer)

    result = run(script, nested)

    assert result.returncode == 0
    assert Path(result.stdout.strip()) == outer.resolve()


def test_resolves_existing_harness_relative_path_from_nested_repo(tmp_path: Path) -> None:
    outer = tmp_path / "harness"
    nested = outer / "workspace" / "foo"
    git_init(outer)
    git_init(nested)
    script = install_script(outer)
    target = outer / "CONTEXT.md"
    target.write_text("context", encoding="utf-8")

    result = run(script, nested, "CONTEXT.md")

    assert result.returncode == 0
    assert Path(result.stdout.strip()) == target.resolve()


def test_rejects_path_outside_harness(tmp_path: Path) -> None:
    outer = tmp_path / "harness"
    git_init(outer)
    script = install_script(outer)
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")

    result = run(script, outer, "../outside.txt")

    assert result.returncode != 0
    assert "escapes the harness repository" in result.stderr
