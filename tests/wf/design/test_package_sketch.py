from __future__ import annotations

import json
import os
import zipfile
from pathlib import Path

import pytest

from package_sketch import main, package


def sketch(tmp_path: Path) -> Path:
    source = tmp_path / "accepted"
    (source / "sketch/orders").mkdir(parents=True)
    (source / "rationale.md").write_text("# Shape\nConsumer usage and alternatives.\n")
    (source / "module-map.md").write_text("orders/Order.cs -> src/Order.cs\n")
    (source / "sketch/orders/Order.cs").write_text("public record Order(int Id);\n")
    return source


def test_package_is_stable_across_mtimes_modes_and_output_names(tmp_path):
    source = sketch(tmp_path)
    first = package(source, tmp_path / "first.zip")
    for file in source.rglob("*"):
        os.utime(file, (1_700_000_000, 1_700_000_000))
        if file.is_file():
            file.chmod(0o755)
    second = package(source, tmp_path / "second.zip")
    assert first["sha256"] == second["sha256"]
    with zipfile.ZipFile(first["file"]) as archive:
        assert archive.namelist() == ["module-map.md", "rationale.md", "sketch/orders/Order.cs"]
        assert archive.read("sketch/orders/Order.cs") == (source / "sketch/orders/Order.cs").read_bytes()
    assert [entry["path"] for entry in first["files"]] == archive.namelist()
    (source / "sketch/orders/Order.cs").write_text("public record Order(string Id);\n")
    assert package(source, tmp_path / "second.zip")["sha256"] != first["sha256"]


def test_package_excludes_build_products_and_preserves_empty_source_files(tmp_path):
    source = sketch(tmp_path)
    (source / "sketch/empty.cs").touch()
    for folder in ("bin", "obj", "node_modules", ".git"):
        (source / folder).mkdir()
        (source / folder / "generated").write_bytes(b"generated")
    result = package(source, tmp_path / "sketch.zip")
    assert {entry["path"] for entry in result["files"]} == {
        "rationale.md", "module-map.md", "sketch/orders/Order.cs", "sketch/empty.cs",
    }


@pytest.mark.parametrize("missing", ["rationale.md", "module-map.md", "sketch/orders/Order.cs"])
def test_invalid_package_does_not_overwrite_previous_archive(tmp_path, missing):
    source = sketch(tmp_path)
    archive = tmp_path / "package.zip"
    archive.write_bytes(b"previous")
    (source / missing).unlink()
    with pytest.raises(ValueError):
        package(source, archive)
    assert archive.read_bytes() == b"previous"


def test_package_rejects_self_inclusion_and_symlinks(tmp_path):
    source = sketch(tmp_path)
    with pytest.raises(ValueError, match="outside"):
        package(source, source / "package.zip")
    (source / "sketch/escape.cs").symlink_to(tmp_path / "outside.cs")
    with pytest.raises(ValueError, match="symbolic"):
        package(source, tmp_path / "package.zip")
    assert not (tmp_path / "package.zip").exists()


def test_cli_returns_inventory_or_clear_failure(tmp_path, capsys):
    source = sketch(tmp_path)
    assert main(["--source", str(source), "--out", str(tmp_path / "package.zip")]) == 0
    assert json.loads(capsys.readouterr().out)["files"]
    assert main(["--source", str(tmp_path / "absent"), "--out", str(tmp_path / "package.zip")]) == 2
    assert "source must" in capsys.readouterr().err
