#!/usr/bin/env python3
"""Package an accepted sketch with stable paths, bytes and inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path

SKIPPED_DIRS = {".git", "__pycache__", "node_modules", "bin", "obj", "dist", "build", ".venv"}
SKIPPED_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}


def package(source: Path, out: Path) -> dict[str, object]:
    source, out = source.resolve(), out.resolve()
    if not source.is_dir():
        raise ValueError("source must be an accepted sketch package directory")
    if out.is_relative_to(source):
        raise ValueError("output must be outside the source package")
    for required in ("rationale.md", "module-map.md"):
        if not (source / required).is_file():
            raise ValueError(f"missing package member: {required}")
    if not (source / "sketch").is_dir():
        raise ValueError("sketch must be a directory")
    files: list[tuple[str, bytes]] = []
    for directory, dirs, names in os.walk(source, followlinks=False):
        root = Path(directory)
        dirs[:] = sorted(name for name in dirs if name not in SKIPPED_DIRS)
        if any((root / name).is_symlink() for name in dirs + names):
            raise ValueError("package must not contain symbolic links")
        for name in sorted(names):
            if name in SKIPPED_FILES or ":" in name:
                continue
            path = root / name
            files.append((path.relative_to(source).as_posix(), path.read_bytes()))
    files.sort()
    if not any(name.startswith("sketch/") for name, _ in files):
        raise ValueError("sketch must contain source files")
    out.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=out.parent, suffix=".zip")
    os.close(descriptor)
    temp_path = Path(temporary)
    try:
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_STORED) as archive:
            for name, data in files:
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
        digest = hashlib.sha256(temp_path.read_bytes()).hexdigest()
        temp_path.replace(out)
    finally:
        temp_path.unlink(missing_ok=True)
    return {
        "file": str(out), "sha256": digest,
        "files": [{"path": name, "sha256": hashlib.sha256(data).hexdigest()} for name, data in files],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = package(args.source, args.out)
    except (ValueError, OSError, zipfile.BadZipFile) as exception:
        print(f"package_sketch: {exception}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
