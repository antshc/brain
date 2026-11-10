"""PR-specific checkout guards; generic Git branch and commit operations live in the git skill."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from .gh import Gh, UsageError


def checkout(gh: Gh, args: argparse.Namespace) -> str:
    root = Path(args.checkout)
    if not root.is_absolute():
        raise UsageError("checkout must be absolute")
    actual = Path(gh.git("-C", str(root), "rev-parse", "--show-toplevel").strip())
    if actual.resolve() != root.resolve():
        raise UsageError("checkout must name the repository root")
    return str(actual)


def sha(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
        raise UsageError("expected a full commit SHA")
    return value


def verify_remote(gh: Gh, root: str, remote: str, repository: str, *, push: bool = False) -> None:
    flags = ["--push", "--all"] if push else ["--all"]
    urls = gh.git("-C", root, "remote", "get-url", *flags, remote).splitlines()
    prefix = r"(?:https://github\.com/|ssh://git@github\.com/|git@github\.com:)"
    if len(urls) != 1 or not re.fullmatch(prefix + re.escape(repository) + r"(?:\.git)?/?", urls[0], re.I):
        raise UsageError(f"{remote} does not uniquely identify {repository}")
