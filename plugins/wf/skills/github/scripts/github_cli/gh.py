from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

REPO_PART = r"(?!\.{1,2}(?:[/#]|$))[A-Za-z0-9_.-]+"
REPO_PATTERN = rf"{REPO_PART}/{REPO_PART}"
Runner = Callable[[list[str]], tuple[int, str, str]]


class UsageError(Exception):
    exit_code = 2


class GhError(Exception):
    exit_code = 1


@dataclass(frozen=True)
class Ref:
    repo: str
    number: int

    def __str__(self) -> str:
        return f"{self.repo}#{self.number}"

    @property
    def key(self) -> str:
        digest = hashlib.sha256(str(self).lower().encode("ascii")).hexdigest()[:24]
        return f"t{self.number}-{digest}"


def parse_ref(text: str, default_repo: str | None = None, *, kind: str = "issues|pull") -> Ref:
    text = text.strip()
    match = re.fullmatch(rf"https://github\.com/({REPO_PATTERN})/(?:{kind})/([1-9]\d*)/?", text)
    match = match or re.fullmatch(rf"({REPO_PATTERN})#([1-9]\d*)", text)
    if match:
        return Ref(match.group(1), int(match.group(2)))
    bare = re.fullmatch(r"#?([1-9]\d*)", text)
    if bare and default_repo:
        return Ref(repository(default_repo), int(bare.group(1)))
    raise UsageError(f"cannot parse qualified GitHub reference: {text!r}")


def run_cmd(args: list[str]) -> tuple[int, str, str]:
    try:
        environment = {**os.environ, "GH_HOST": "github.com"} if args[0] == "gh" else None
        done = subprocess.run(args, check=False, capture_output=True, text=True, env=environment)
    except FileNotFoundError as exception:
        raise GhError(f"{args[0]} is not installed") from exception
    return done.returncode, done.stdout, done.stderr


class Gh:
    def __init__(self, runner: Runner = run_cmd) -> None:
        self._runner = runner

    def raw(self, *args: str) -> tuple[int, str, str]:
        return self._runner(["gh", *args])

    def text(self, *args: str) -> str:
        code, out, err = self.raw(*args)
        if code:
            raise GhError(f"gh {' '.join(args[:3])} failed ({code}): {(err or out).strip()}")
        return out

    def json(self, *args: str) -> Any:
        return json.loads(self.text(*args) or "null")

    def pages(self, endpoint: str) -> list[dict[str, Any]]:
        pages = self.json("api", "--paginate", "--slurp", endpoint)
        if not isinstance(pages, list) or any(not isinstance(page, list) for page in pages):
            raise GhError(f"incomplete paginated response: {endpoint}")
        return [item for page in pages for item in page]

    def git(self, *args: str) -> str:
        code, out, err = self._runner(["git", *args])
        if code:
            raise GhError(f"git {' '.join(args[:3])} failed ({code}): {(err or out).strip()}")
        return out


def repository(value: str) -> str:
    if not re.fullmatch(REPO_PATTERN, value):
        raise UsageError("expected a qualified owner/repository")
    return value


def read_body(path: str | Path) -> str:
    return Path(path).read_bytes().decode("utf-8")


def request(gh: Gh, endpoint: str, method: str, payload: dict[str, Any]) -> Any:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "payload.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return gh.json("api", "--method", method, endpoint, "--input", str(path))


def graphql(gh: Gh, query: str, **variables: Any) -> dict[str, Any]:
    result = request(gh, "graphql", "POST", {"query": query, "variables": variables})
    if not isinstance(result, dict) or result.get("errors") or not isinstance(result.get("data"), dict):
        raise GhError("GraphQL returned incomplete data or errors")
    return result["data"]
