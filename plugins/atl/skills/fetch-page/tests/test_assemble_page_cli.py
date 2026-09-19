"""CLI-level tests for `--md-path`/`--assets-dir` wiring, invoked as a real subprocess
(mirroring `/map-markdown-adf`'s `run_cli` fixture pattern)."""
import json
import subprocess
import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "assemble_page.py"


def _run(args: list[str], stdin_text: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_SCRIPT), *args],
        input=stdin_text,
        capture_output=True,
        text=True,
    )


def _raw(title: str, body: dict) -> str:
    return json.dumps({"content": {"nodes": [{"title": title, "body": body}]}})


def test_main_writes_markdown_to_md_path_with_default_assets_dir(tmp_path):
    md_path = tmp_path / "page.md"
    raw = _raw("Simple Page", {"type": "doc", "version": 1, "content": []})

    result = _run(["--page-id", "123", "--root", str(tmp_path), "--md-path", str(md_path)], raw)

    assert result.returncode == 0, result.stderr
    assert md_path.read_text() == "# Simple Page\n\n\n"
    # a page with no attachment reference never creates the default `.tmp` assets folder
    assert not (tmp_path / "page.md.tmp").exists()


def test_main_accepts_an_explicit_assets_dir_override(tmp_path):
    md_path = tmp_path / "page.md"
    assets_dir = tmp_path / "custom-assets"
    raw = _raw("Simple Page", {"type": "doc", "version": 1, "content": []})

    result = _run(
        [
            "--page-id",
            "123",
            "--root",
            str(tmp_path),
            "--md-path",
            str(md_path),
            "--assets-dir",
            str(assets_dir),
        ],
        raw,
    )

    assert result.returncode == 0, result.stderr
    assert md_path.read_text() == "# Simple Page\n\n\n"
    assert not assets_dir.exists()
