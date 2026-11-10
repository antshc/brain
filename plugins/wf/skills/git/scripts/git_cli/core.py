from __future__ import annotations

import subprocess
from typing import Callable

Runner = Callable[[list[str]], tuple[int, str, str]]


class UsageError(Exception):
    exit_code = 2


class GitError(Exception):
    exit_code = 1


def run_cmd(args: list[str]) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(args, check=False, capture_output=True, text=True)
    except FileNotFoundError as exception:
        raise GitError(f"{args[0]} is not installed") from exception
    return completed.returncode, completed.stdout, completed.stderr


class Git:
    def __init__(self, runner: Runner = run_cmd) -> None:
        self._runner = runner

    def git(self, *args: str) -> str:
        code, stdout, stderr = self._runner(["git", *args])
        if code:
            raise GitError(f"git {' '.join(args[:3])} failed ({code}): {(stderr or stdout).strip()}")
        return stdout
