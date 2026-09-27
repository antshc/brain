#!/usr/bin/env python3
"""Run every repository test directory in an isolated pytest process."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_roots(repo: Path) -> list[Path]:
    paths = subprocess.check_output(["git", "ls-files"], cwd=repo, text=True).splitlines()
    roots: set[Path] = set()
    for name in paths:
        path = Path(name)
        if any(part in {"_backup", "_in-progress"} for part in path.parts):
            continue
        if path.suffix != ".py" or not (path.name.startswith("test_") or path.name.endswith("_test.py")):
            continue
        roots.add(Path("tools/tests") if path.parts[:2] == ("tools", "tests") else path.parent)
    return sorted(roots)


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    failures = []
    for folder in test_roots(repo):
        print(f"\nTesting {folder}", flush=True)
        result = subprocess.run([sys.executable, "-m", "pytest", str(folder)], cwd=repo, check=False)
        if result.returncode:
            failures.append(str(folder))
    if failures:
        print(f"Failed: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
