from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import bundle_artifacts
from bundle_artifacts import BundleError, bundle

SCRIPT = Path(bundle_artifacts.__file__)


def tree(root: Path, files: dict[str, str | bytes]) -> Path:
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
    return root


def by_name(artifacts) -> dict:
    return {artifact.name: artifact for artifact in artifacts}


class TestCollect:
    def test_one_artifact_per_file_index_first_sorted(self, tmp_path):
        sketch = tree(tmp_path / "s", {"b/z.py": "x = 1\n", "a.go": "package a\n", "b/a.txt": "note\n"})
        artifacts, skipped = bundle(sketch)
        assert [a.name for a in artifacts] == ["Sketch index", "a.go", "b/a.txt", "b/z.py"]
        assert artifacts[0].type == "plan" and {a.type for a in artifacts[1:]} == {"generic"}
        assert skipped == []

    def test_single_file_sketch_named_after_file(self, tmp_path):
        path = tree(tmp_path, {"only.ts": "export type T = 1;\n"}) / "only.ts"
        artifacts, _ = bundle(path)
        assert [a.name for a in artifacts] == ["Sketch index", "only.ts"]

    def test_metadata_and_empty_files_skipped(self, tmp_path):
        sketch = tree(tmp_path / "s", {
            "a.cs": "class A {}\n", "a.cs:Zone.Identifier": "[ZoneTransfer]\n", ".DS_Store": "x", "blank.txt": "  \n",
            ".git/config": "[core]\n",
        })
        artifacts, skipped = bundle(sketch)
        assert [a.name for a in artifacts][1:] == ["a.cs"]
        assert {s["path"]: s["reason"] for s in skipped} == {
            ".DS_Store": "metadata", "a.cs:Zone.Identifier": "metadata", "blank.txt": "empty"}

    def test_binary_file_is_an_error_not_dropped(self, tmp_path):
        sketch = tree(tmp_path / "s", {"a.txt": "ok\n", "img.png": b"\x89PNG\x00\x01"})
        with pytest.raises(BundleError, match="img.png"):
            bundle(sketch)

    def test_missing_or_textless_sketch_fails(self, tmp_path):
        with pytest.raises(BundleError, match="not found"):
            bundle(tmp_path / "absent")
        with pytest.raises(BundleError, match="no text files"):
            bundle(tree(tmp_path / "s", {"e.txt": ""}))


class TestRender:
    def test_code_fenced_with_language_and_path_heading(self, tmp_path):
        artifact = by_name(bundle(tree(tmp_path / "s", {"src/m.py": "def f(): ...\n"}))[0])["src/m.py"]
        assert artifact.body == "# `src/m.py`\n\n```python\ndef f(): ...\n```\n"

    def test_unknown_extension_has_bare_fence(self, tmp_path):
        artifact = by_name(bundle(tree(tmp_path / "s", {"notes.weird": "data\n"}))[0])["notes.weird"]
        assert "```\ndata\n```" in artifact.body

    def test_fence_longer_than_any_backtick_run(self, tmp_path):
        artifact = by_name(bundle(tree(tmp_path / "s", {"x.txt": "a ```` b\n"}))[0])["x.txt"]
        assert artifact.body.split("\n")[2] == "`````"

    def test_markdown_kept_unfenced_under_heading(self, tmp_path):
        artifact = by_name(bundle(tree(tmp_path / "s", {"d.md": "## Part\n\n```js\nx\n```\n"}))[0])["d.md"]
        assert artifact.body == "# `d.md`\n\n## Part\n\n```js\nx\n```\n"

    def test_html_becomes_embedded_html_raw(self, tmp_path):
        artifact = by_name(bundle(tree(tmp_path / "s", {"p.html": "<p>hi</p>"}))[0])["p.html"]
        assert (artifact.type, artifact.body) == ("embedded_html", "<p>hi</p>")

    def test_index_maps_every_path_to_its_artifacts(self, tmp_path):
        artifacts, _ = bundle(tree(tmp_path / "s", {"a (1).txt": "x\n", "b.txt": "y\n"}))
        index = artifacts[0].body
        assert "| `a (1).txt` | `a 1.txt` |" in index and "| `b.txt` | `b.txt` |" in index


class TestNames:
    def test_disallowed_characters_removed(self, tmp_path):
        artifacts, _ = bundle(tree(tmp_path / "s", {"List<T> (v2).cs": "x\n"}))
        assert artifacts[1].name == "ListT v2.cs"

    def test_collision_after_normalization_fails(self, tmp_path):
        with pytest.raises(BundleError, match="collision"):
            bundle(tree(tmp_path / "s", {"a(b).txt": "x\n", "ab.txt": "y\n"}))

    def test_collision_with_index_name_fails(self, tmp_path):
        with pytest.raises(BundleError, match="collision"):
            bundle(tree(tmp_path / "s", {"Sketch index": "x\n"}))


class TestSplit:
    def test_oversized_file_split_at_line_boundaries(self, tmp_path):
        text = "".join(f"line {n:04d}\n" for n in range(300))
        artifacts, _ = bundle(tree(tmp_path / "s", {"big.txt": text}), max_chars=1000)
        parts = [a for a in artifacts if a.source == "big.txt"]
        assert len(parts) > 1 and all(len(a.body) <= 1000 for a in parts)
        assert parts[0].name == f"big.txt part 1 of {len(parts)}"
        rebuilt = "".join(re.search(r"```\n(.*)\n```\n$", a.body, re.S).group(1) + "\n" for a in parts)
        assert rebuilt == text

    def test_single_long_line_hard_split(self, tmp_path):
        artifacts, _ = bundle(tree(tmp_path / "s", {"one.txt": "x" * 2500}), max_chars=1000)
        assert all(len(a.body) <= 1000 for a in artifacts[1:]) and len(artifacts) > 3

    def test_oversized_html_fails(self, tmp_path):
        with pytest.raises(BundleError, match="HTML"):
            bundle(tree(tmp_path / "s", {"p.html": "<p>" + "x" * 2000 + "</p>"}), max_chars=1000)


class TestCli:
    def run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)

    def test_writes_bodies_and_manifest(self, tmp_path):
        sketch = tree(tmp_path / "s", {"a.py": "a = 1\n", "v.html": "<b>x</b>"})
        done = self.run("--sketch", str(sketch), "--out-dir", str(tmp_path / "out"))
        assert done.returncode == 0, done.stderr
        manifest = json.loads(done.stdout)
        assert manifest == json.loads((tmp_path / "out" / "manifest.json").read_text())
        assert [(e["name"], e["type"], Path(e["file"]).name) for e in manifest["artifacts"]] == [
            ("Sketch index", "plan", "001.md"), ("a.py", "generic", "002.md"), ("v.html", "embedded_html", "003.html")]
        assert Path(manifest["artifacts"][2]["file"]).read_text() == "<b>x</b>"

    def test_errors_exit_2_and_write_nothing(self, tmp_path):
        sketch = tree(tmp_path / "s", {"bin.dat": b"\x00\x01"})
        done = self.run("--sketch", str(sketch), "--out-dir", str(tmp_path / "out"))
        assert done.returncode == 2 and "binary" in done.stderr and not (tmp_path / "out").exists()

    def test_non_empty_out_dir_rejected(self, tmp_path):
        sketch = tree(tmp_path / "s", {"a.txt": "x\n"})
        (tmp_path / "out").mkdir()
        (tmp_path / "out" / "keep").write_text("k")
        done = self.run("--sketch", str(sketch), "--out-dir", str(tmp_path / "out"))
        assert done.returncode == 2 and "not empty" in done.stderr
