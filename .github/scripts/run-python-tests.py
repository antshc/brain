#!/usr/bin/env python3
"""Run every repository test directory in an isolated pytest process.

`--unit-only` skips integration tests: `tools/tests/integration/` and `*_integration.py` files.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


INTEGRATION_GLOB = "*_integration.py"


def test_roots(repo: Path, unit_only: bool = False) -> list[Path]:
    paths = subprocess.check_output(["git", "ls-files"], cwd=repo, text=True).splitlines()
    roots: set[Path] = set()
    for name in paths:
        path = Path(name)
        if any(part in {"_backup", "_in-progress"} for part in path.parts):
            continue
        if path.suffix != ".py" or not (path.name.startswith("test_") or path.name.endswith("_test.py")):
            continue
        if unit_only and path.match(INTEGRATION_GLOB):
            continue
        if path.parts[:2] == ("tools", "tests"):
            if unit_only:
                if path.parts[2:3] == ("unit",):
                    roots.add(Path("tools/tests/unit"))
                continue
            roots.add(Path("tools/tests"))
        elif path.parts[0] == "tests":
            # Per-skill folders run isolated; a file directly under tests/<plugin>/ runs alone.
            roots.add(Path(*path.parts[:3]))
        else:
            roots.add(path.parent)
    return sorted(roots)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit-only", action="store_true", help="skip integration tests")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    extra = [f"--ignore-glob={INTEGRATION_GLOB}"] if args.unit_only else []
    failures = []
    for folder in test_roots(repo, args.unit_only):
        print(f"\nTesting {folder}", flush=True)
        result = subprocess.run([sys.executable, "-m", "pytest", str(folder), *extra], cwd=repo, check=False)
        if result.returncode:
            failures.append(str(folder))
    if failures:
        print(f"Failed: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
