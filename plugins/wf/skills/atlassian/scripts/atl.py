#!/usr/bin/env python3
"""ATL command-line entry point; runs from any working directory.

    python3 <atlassian-skill-dir>/scripts/atl.py <command> [options]

Commands: fetch-work, publish-work, fetch-page, publish-page, map-markdown. See `--help`.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _configured_python(args: list[str]) -> Path | None:
    config_path: Path | None = None
    if "--config" in args:
        index = args.index("--config")
        if index + 1 < len(args):
            config_path = Path(args[index + 1])
    elif any(value.startswith("--config=") for value in args):
        config_path = Path(next(value.split("=", 1)[1] for value in args if value.startswith("--config=")))
    if config_path is None or not config_path.is_file():
        return None
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    candidate = Path(str(config.get("pythonPath", "")).strip()) if isinstance(config, dict) else None
    return candidate if candidate and candidate.is_absolute() and candidate.is_file() else None


def _local_runtime() -> Path | None:
    for parent in (Path.cwd(), *Path.cwd().parents):
        candidate = parent / ".venv" / "bin" / "python"
        if not candidate.is_file():
            continue
        try:
            probe = subprocess.run(
                [
                    str(candidate),
                    "-c",
                    "import atlassian, pymarkdown.api, requests",
                ],
                capture_output=True,
                check=False,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if probe.returncode == 0:
            return candidate
    return None


_arguments = sys.argv[1:]
_python = _configured_python(_arguments) or _local_runtime()
# Compare unresolved paths: venv interpreters symlink to a shared base, so resolving would hide a different environment.
if _python is not None and not os.environ.get("ATL_PYTHON_REEXEC") and os.path.abspath(sys.executable) != os.path.abspath(_python):
    os.execve(
        str(_python),
        [str(_python), str(Path(__file__).resolve()), *_arguments],
        {**os.environ, "ATL_PYTHON_REEXEC": "1"},
    )

sys.path.insert(0, str(Path(__file__).resolve().parent))

from atl_cli.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
