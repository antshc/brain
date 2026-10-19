from __future__ import annotations

import hashlib
import os
import signal
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from http.client import HTTPException
from pathlib import Path
from typing import IO, Any

from ..app import APP

# proof/engine/runtime.py -> the repository root, wherever mole is started from.
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_URL = APP.url


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, errors="replace", check=True)
    return result.stdout


# Proof files are not part of the build, so editing them must not stale the running app. Bytecode is never source.
def _pathspec() -> list[str]:
    return [
        "--",
        *(APP.source_paths or ["."]),
        ":(exclude)proof",
        ":(exclude).github",
        ":(exclude,glob)**/__pycache__/**",
        ":(exclude,glob)**/*.pyc",
    ]


# An app rarely serves its revision, so derive one from the source: HEAD plus a hash of uncommitted changes under APP.source_paths.
def source_revision() -> str | None:
    try:
        head = git("rev-parse", "--short", "HEAD").strip()
        diff = git("diff", "HEAD", *_pathspec())
        untracked = sorted(line for line in git("ls-files", "--others", "--exclude-standard", *_pathspec()).split("\n") if line)
        digest = hashlib.sha256(diff.encode())
        for file in untracked:
            digest.update(file.encode())
            try:
                digest.update((ROOT / file).read_bytes())
            except OSError:
                pass
        return f"{head}+{digest.hexdigest()[:8]}" if diff or untracked else head
    except (subprocess.CalledProcessError, OSError):
        return None


def changed_files() -> list[str]:
    """Files changed since HEAD, relative to ROOT, plus untracked ones."""

    def lines(*args: str) -> list[str]:
        return [line for line in git(*args).split("\n") if line]

    return list(dict.fromkeys([*lines("diff", "--name-only", "--relative", "HEAD"), *lines("ls-files", "--others", "--exclude-standard")]))


# PROOF_API_URL wins, then APP.api.discover. A repo with no web surface is its own API.
def discover_api() -> str | None:
    if os.environ.get("PROOF_API_URL"):
        return os.environ["PROOF_API_URL"]
    if APP.api and APP.api.discover:
        try:
            found = APP.api.discover()
        except (OSError, ValueError, RuntimeError):
            found = None
        if found:
            return found
    return None if "web" in APP.surfaces else APP.url


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


_NO_REDIRECT = urllib.request.build_opener(_NoRedirect)
_NETWORK_ERRORS = (OSError, HTTPException, ValueError)


def reachable(url: str, timeout_s: float = 2.0) -> bool:
    try:
        with _NO_REDIRECT.open(url, timeout=timeout_s) as response:
            return bool(response.status < 500)
    except urllib.error.HTTPError as exception:  # A redirect or an error status still means something answered.
        return exception.code < 500
    except _NETWORK_ERRORS:
        return False


def api_answers(base_url: str) -> bool:
    try:
        return bool(APP.api.probe(base_url)) if APP.api and APP.api.probe else reachable(base_url)
    except (OSError, ValueError, RuntimeError):
        return False


@dataclass(frozen=True)
class HttpResponse:
    status: int
    body: str


def fetch(url: str, timeout_s: float = 10.0) -> HttpResponse:
    """GET `url`, following redirects. Raises OSError (URLError, timeouts, resets) when nothing answers."""
    try:
        with urllib.request.urlopen(url, timeout=timeout_s) as response:
            return HttpResponse(response.status, response.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as exception:
        return HttpResponse(exception.code, exception.read().decode("utf-8", errors="replace"))
    except HTTPException as exception:
        raise OSError(str(exception)) from exception


class StartedApp:
    def __init__(self, url: str, child: subprocess.Popen[bytes], log: Path, log_file: IO[bytes]) -> None:
        self.url = url
        self.child = child
        self.pid = child.pid
        self.log = log
        self._log_file = log_file

    def close(self) -> None:
        if self.child.poll() is None:
            try:
                os.killpg(self.pid, signal.SIGINT)
            except ProcessLookupError:
                pass
            try:
                self.child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(self.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                self.child.wait()
        self._log_file.close()


def _tail(file: Path) -> str:
    try:
        lines = [line for line in file.read_text(errors="replace").strip().split("\n") if line]
    except OSError:
        lines = []
    return " ".join(lines[:3])[:300] or "no output"


# Runs APP.start and waits until the app answers (and APP.start.ready agrees).
def start_app(*, log: Path, url: str | None = None, timeout_s: float | None = None) -> StartedApp:
    start = APP.start
    if start is None:
        raise RuntimeError("proof/app.py has no `start`, so mole cannot run the app. Start it yourself, or fill in APP.start.")
    target = url or DEFAULT_URL
    extra = (start.prerequisites() if start.prerequisites else None) or {}
    log_file = log.open("wb")
    try:
        child = subprocess.Popen(
            [start.command, *start.args],
            cwd=ROOT / start.cwd if start.cwd else ROOT,
            env={**os.environ, **extra, **start.env},
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    except OSError as exception:
        log_file.close()
        raise RuntimeError(f"Can't run `{start.command}`: {exception}. Fix APP.start in proof/app.py.") from exception
    started = StartedApp(target, child, log, log_file)

    deadline = time.monotonic() + (timeout_s or start.timeout_s)
    while time.monotonic() < deadline:
        code = child.poll()
        if code is not None:
            started.close()
            raise RuntimeError(f"The app exited with code {code} before it answered: {_tail(log)} (log: {log})")
        if reachable(target) and _ready(target):
            return started
        time.sleep(1)
    started.close()
    raise RuntimeError(f"{APP.name} did not answer at {target} in time. See {log}")


def _ready(url: str) -> bool:
    ready = APP.start.ready if APP.start else None
    if ready is None:
        return True
    try:
        return bool(ready(url))
    except (OSError, ValueError, RuntimeError):
        return False
