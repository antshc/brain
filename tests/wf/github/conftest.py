"""Shared fixtures: an in-memory `gh` fake with real-git passthrough, and the live-test gate."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse

import pytest

SKILL = Path(__file__).resolve().parents[3] / "plugins/wf/skills/github"
SCRIPT = SKILL / "scripts/github.py"
sys.path.insert(0, str(SCRIPT.parent))

from github_cli.cli import main
from github_cli.gh import Gh, run_cmd

LIVE_REPO = "antshc/brain"
LIVE_ENV = "BRAIN_GH_LIVE"
HEAD = "a" * 40
BASE = "b" * 40


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "integration: talks to the real antshc/brain repository through gh")
    config.addinivalue_line("markers", "live(area): live area selected through BRAIN_GH_LIVE")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    enabled = {part.strip() for part in os.environ.get(LIVE_ENV, "").lower().split(",") if part.strip()}
    for item in items:
        mark = item.get_closest_marker("live")
        if mark is None or "all" in enabled or mark.args[0] in enabled:
            continue
        item.add_marker(pytest.mark.skip(
            reason=f"live area {mark.args[0]!r} not selected; set {LIVE_ENV}={mark.args[0]} when the change risks it"))


@dataclass
class Result:
    code: int
    data: Any
    err: str


@pytest.fixture
def run(capsys: pytest.CaptureFixture[str]) -> Callable[..., Result]:
    def invoke(*argv: object, gh: Gh | Callable | None = None) -> Result:
        runner = gh if isinstance(gh, Gh) else Gh(gh) if gh else None
        code = main([str(arg) for arg in argv], gh=runner)
        out, err = capsys.readouterr()
        return Result(code, json.loads(out) if out.strip() else None, err)
    return invoke


@pytest.fixture
def body(tmp_path: Path) -> Callable[[str, str], str]:
    def write(text: str, name: str = "body.md") -> str:
        path = tmp_path / name
        path.write_bytes(text.encode("utf-8"))
        return str(path)
    return write


class FakeGitHub:
    """Stateful stand-in for `gh api` on one repository.

    Anything that is not a modelled REST route must be stubbed explicitly; git commands run for real
    unless stubbed. `remote_url` makes `git remote get-url` report a GitHub URL for a local repository.
    """

    def __init__(self, repo: str = "acme/work", login: str = "bot") -> None:
        self.repo, self.login = repo, login
        self.issues: dict[int, dict] = {}
        self.pulls: dict[int, dict] = {}
        self.comments: dict[int, dict] = {}
        self.review_comments: dict[int, dict] = {}
        self.labels: dict[str, dict] = {}
        self.branches: dict[str, str] = {}
        self.artifacts: list[dict] = []
        self.sub_issues: dict[int, list[int]] = {}
        self.blocked_by: dict[int, list[int]] = {}
        self.calls: list[list[str]] = []
        self.remote_url: str | None = None
        self.graphql_handler: Callable[[str, dict], dict] | None = None
        self._stubs: list[tuple[tuple[str, ...], Any]] = []
        self._rules: list[list[Any]] = []
        self._next = 100
        self._number = 0

    def __call__(self, argv: list[str]) -> tuple[int, str, str]:
        self.calls.append(list(argv))
        for seq, response in reversed(self._stubs):
            if any(argv[i:i + len(seq)] == list(seq) for i in range(len(argv))):
                return response(argv) if callable(response) else response
        if argv[0] == "git":
            if self.remote_url and "get-url" in argv:
                return 0, self.remote_url + "\n", ""
            return run_cmd(argv)
        assert argv[:2] == ["gh", "api"], f"unexpected call: {argv}"
        return self._api(argv[2:])

    def stub(self, seq: tuple[str, ...], response: tuple[int, str, str] | Callable[[list[str]], tuple]) -> None:
        self._stubs.append((seq, response))

    def fail(self, method: str, pattern: str, message: str = "boom") -> None:
        self._rules.append(["fail", method, re.compile(pattern), message])

    def lose(self, method: str, pattern: str, message: str = "lost response") -> None:
        """Apply the write, then report failure, like a response lost in transit."""
        self._rules.append(["lose", method, re.compile(pattern), message])

    def writes(self) -> list[str]:
        written = []
        for argv in self.calls:
            if argv[:2] == ["gh", "api"] and "--method" in argv:
                written.append(f"{argv[argv.index('--method') + 1]} {argv[-3] if '--input' in argv else argv[-1]}")
        return written

    def _id(self) -> int:
        self._next += 1
        return self._next

    def add_issue(self, title: str = "Title", body: str = "Body", labels: tuple[str, ...] = (), state: str = "open",
                  assignees: tuple[str, ...] = (), pull: bool = False, **extra: Any) -> int:
        self._number += 1
        number = self._number
        self.issues[number] = {
            "id": self._id(), "number": number, "title": title, "body": body, "state": state,
            "state_reason": "completed" if state == "closed" else None,
            "labels": [{"name": name} for name in labels], "assignees": [{"login": name} for name in assignees],
            "repository_url": f"https://api.github.com/repos/{self.repo}",
            "html_url": f"https://github.com/{self.repo}/issues/{number}", **extra,
        }
        if pull:
            self.issues[number]["pull_request"] = {}
        return number

    def add_pull(self, head: str = HEAD, base: str = BASE, head_ref: str = "feat/x", base_ref: str = "main",
                 title: str = "PR", body: str = "", draft: bool = True, state: str = "open") -> int:
        self._number += 1
        number = self._number
        self.pulls[number] = {
            "number": number, "state": state, "title": title, "body": body, "draft": draft,
            "html_url": f"https://github.com/{self.repo}/pull/{number}",
            "head": {"sha": head, "ref": head_ref, "repo": {"full_name": self.repo}},
            "base": {"sha": base, "ref": base_ref},
        }
        return number

    def add_comment(self, number: int, body: str, login: str | None = None) -> int:
        ident = self._id()
        self.comments[ident] = {"id": ident, "issue": number, "body": body, "user": {"login": login or self.login},
                                "html_url": f"https://github.com/{self.repo}/issues/{number}#issuecomment-{ident}"}
        return ident

    def _api(self, args: list[str]) -> tuple[int, str, str]:
        method, payload, paginate, endpoint, fields = "GET", None, False, "", {}
        it = iter(args)
        for arg in it:
            if arg == "--paginate":
                paginate = True
            elif arg == "--method":
                method = next(it)
            elif arg == "--input":
                payload = json.loads(Path(next(it)).read_text(encoding="utf-8"))
            elif arg in ("-H", "--jq"):
                next(it)
            elif arg in ("-f", "-F"):
                key, _, value = next(it).partition("=")
                fields[key] = value
            elif arg != "--slurp":
                endpoint = arg
        lost = None
        for rule in list(self._rules):
            if rule[1] == method and rule[2].search(endpoint):
                self._rules.remove(rule)
                if rule[0] == "fail":
                    return 1, "", rule[3]
                lost = rule[3]
        status, result = self._route(method, endpoint, payload, fields)
        if lost:
            return 1, "", lost
        if status:
            return 1, "", f"gh: {result} (HTTP {status})"
        if paginate:
            result = [result]
        return 0, json.dumps(result), ""

    def _route(self, method: str, endpoint: str, payload: dict | None, fields: dict) -> tuple[int, Any]:
        parsed = urlparse(endpoint)
        query = {key: values[0] for key, values in parse_qs(parsed.query).items()}
        path = parsed.path
        if path == "user":
            return 0, {"login": self.login}
        if path == "graphql":
            assert self.graphql_handler, "graphql not modelled"
            variables = payload["variables"] if payload else {k: v for k, v in fields.items() if k != "query"}
            return 0, self.graphql_handler(payload["query"] if payload else fields["query"], variables)
        match = re.fullmatch(rf"repos/{re.escape(self.repo)}/(.*)", path)
        if not match:
            return 404, "Not Found"
        rest = match.group(1)
        for pattern, handler in self._routes():
            found = re.fullmatch(pattern[1], rest)
            if found and pattern[0] == method:
                return handler(found, query, payload)
        return 404, "Not Found"

    def _routes(self) -> list[tuple[tuple[str, str], Callable]]:
        return [
            (("GET", r"issues"), self._list_issues), (("POST", r"issues"), self._create_issue),
            (("GET", r"issues/(\d+)"), lambda m, q, p: self._get(self.issues, int(m[1]))),
            (("GET", r"issues/(\d+)/comments"), lambda m, q, p: (0, [c for c in self.comments.values() if c["issue"] == int(m[1])])),
            (("POST", r"issues/(\d+)/comments"), lambda m, q, p: (0, self.comments[self.add_comment(int(m[1]), p["body"])])),
            (("GET", r"issues/comments/(\d+)"), lambda m, q, p: self._get(self.comments, int(m[1]))),
            (("PATCH", r"issues/comments/(\d+)"), self._edit_comment),
            (("POST", r"issues/(\d+)/assignees"), lambda m, q, p: self._assign(int(m[1]), p, add=True)),
            (("DELETE", r"issues/(\d+)/assignees"), lambda m, q, p: self._assign(int(m[1]), p, add=False)),
            (("GET", r"issues/(\d+)/sub_issues"), lambda m, q, p: (0, [self._by_id(i) for i in self.sub_issues.get(int(m[1]), [])])),
            (("POST", r"issues/(\d+)/sub_issues"), lambda m, q, p: (0, self.sub_issues.setdefault(int(m[1]), []).append(p["sub_issue_id"]) or {})),
            (("GET", r"issues/(\d+)/dependencies/blocked_by"), lambda m, q, p: (0, [self._by_id(i) for i in self.blocked_by.get(int(m[1]), [])])),
            (("GET", r"issues/(\d+)/artifacts"), self._list_artifacts),
            (("GET", r"labels"), lambda m, q, p: (0, list(self.labels.values()))),
            (("POST", r"labels"), self._create_label),
            (("GET", r"pulls"), self._list_pulls), (("POST", r"pulls"), self._create_pull),
            (("GET", r"pulls/(\d+)"), lambda m, q, p: self._get(self.pulls, int(m[1]))),
            (("GET", r"pulls/(\d+)/comments"), lambda m, q, p: (0, [c for c in self.review_comments.values() if c["pull"] == int(m[1])])),
            (("POST", r"pulls/(\d+)/comments"), self._create_review_comment),
            (("GET", r"pulls/comments/(\d+)"), lambda m, q, p: self._get(self.review_comments, int(m[1]))),
            (("GET", r"branches/(.+)"), self._get_branch),
        ]

    def _list_artifacts(self, m, query, payload):
        size, page = int(query.get("per_page", 30)), int(query.get("page", 1))
        return 0, self.artifacts[(page - 1) * size:page * size]

    def _get(self, table: dict, key: int) -> tuple[int, Any]:
        return (0, table[key]) if key in table else (404, "Not Found")

    def _by_id(self, ident: int) -> dict:
        return next(issue for issue in self.issues.values() if issue["id"] == ident)

    def _list_issues(self, m, query, payload):
        wanted = {name for name in query.get("labels", "").split(",") if name}
        return 0, [i for i in self.issues.values() if wanted <= {label["name"] for label in i["labels"]}]

    def _create_issue(self, m, query, payload):
        number = self.add_issue(payload["title"], payload["body"], tuple(payload.get("labels", [])))
        return 0, self.issues[number]

    def _edit_comment(self, m, query, payload):
        self.comments[int(m[1])]["body"] = payload["body"]
        return 0, self.comments[int(m[1])]

    def _assign(self, number: int, payload: dict, *, add: bool):
        names = {user["login"] for user in self.issues[number]["assignees"]}
        names = names | set(payload["assignees"]) if add else names - set(payload["assignees"])
        self.issues[number]["assignees"] = [{"login": name} for name in sorted(names)]
        return 0, self.issues[number]

    def _create_label(self, m, query, payload):
        if payload["name"] in self.labels:
            return 422, "Validation Failed"
        self.labels[payload["name"]] = {"name": payload["name"], "color": payload.get("color")}
        return 0, self.labels[payload["name"]]

    def _list_pulls(self, m, query, payload):
        head = query.get("head", "").split(":", 1)[-1]
        return 0, [p for p in self.pulls.values() if p["head"]["ref"] == head and p["base"]["ref"] == query.get("base")
                   and p["state"] == query.get("state", "open")]

    def _create_pull(self, m, query, payload):
        number = self.add_pull(self.branches[payload["head"]], BASE, payload["head"], payload["base"],
                               payload["title"], payload["body"], payload["draft"])
        return 0, self.pulls[number]

    def _create_review_comment(self, m, query, payload):
        ident = self._id()
        self.review_comments[ident] = {**payload, "id": ident, "pull": int(m[1])}
        return 0, self.review_comments[ident]

    def _get_branch(self, m, query, payload):
        from urllib.parse import unquote
        name = unquote(m[1])
        return (0, {"name": name, "commit": {"sha": self.branches[name]}}) if name in self.branches else (404, "Not Found")


@pytest.fixture
def fake() -> FakeGitHub:
    return FakeGitHub()


def git(path: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A real local checkout with one commit."""
    root = tmp_path / "checkout"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "test@example.invalid")
    git(root, "config", "user.name", "Test")
    git(root, "commit", "--allow-empty", "-qm", "initial")
    return root


# Live helpers -------------------------------------------------------------------------------------

LIVE_GIT_ENV = {
    "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_COUNT": "1",
    "GIT_CONFIG_KEY_0": "credential.https://github.com.helper", "GIT_CONFIG_VALUE_0": "!gh auth git-credential",
}


@pytest.fixture(scope="session")
def live_ready() -> None:
    if shutil.which("gh") is None or subprocess.run(["gh", "auth", "status"], capture_output=True).returncode:
        pytest.skip("gh is missing or unauthenticated")
    permission = subprocess.run(["gh", "api", f"repos/{LIVE_REPO}", "--jq", ".permissions.push"],
                                capture_output=True, text=True)
    if permission.stdout.strip() != "true":
        pytest.skip(f"no push access to {LIVE_REPO}")


@pytest.fixture(scope="session")
def run_id() -> str:
    """Unique per xdist worker (each worker is its own session), so workers never share live resources."""
    return f"it-{uuid.uuid4().hex[:8]}"


def ident(run_id: str) -> str:
    """A name unique to one test, derived from the worker's run id."""
    return f"{run_id}-{uuid.uuid4().hex[:6]}"


@pytest.fixture(scope="session")
def cleanup() -> Any:
    """Teardown callbacks run in reverse; a failed cleanup is reported, never hidden."""
    actions: list[Callable[[], None]] = []
    yield actions.append
    leaked = []
    for action in reversed(actions):
        try:
            action()
        except (subprocess.SubprocessError, OSError) as exception:
            leaked.append(str(exception))
    assert not leaked, f"live cleanup failed, remove leftovers in {LIVE_REPO} by hand: {leaked}"


@pytest.fixture(scope="session")
def live(live_ready: None, cleanup: Callable, run_id: str) -> Callable[..., Result]:
    def sweep() -> None:
        """Safety net: delete any issue titled with this worker's run id, even one created outside a helper."""
        rows = json.loads(gh_live("api", f"repos/{LIVE_REPO}/issues?state=all&per_page=100&sort=created&direction=desc"))
        for row in rows:
            if "pull_request" not in row and row["title"].startswith((f"[{run_id}]", run_id.upper())):
                quiet("issue", "delete", str(row["number"]), "-R", LIVE_REPO, "--yes")

    cleanup(sweep)

    def invoke(*argv: object, cwd: Path | None = None, code: int | None = 0) -> Result:
        done = subprocess.run([sys.executable, str(SCRIPT), *map(str, argv)], cwd=cwd, text=True, capture_output=True,
                              env={**os.environ, **LIVE_GIT_ENV})
        result = Result(done.returncode, json.loads(done.stdout) if done.stdout.strip().startswith(("{", "[")) else done.stdout, done.stderr)
        if code is not None:
            assert result.code == code, f"{argv} exited {result.code}: {done.stderr}\n{done.stdout}"
        return result
    return invoke


def gh_live(*args: str) -> str:
    done = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    return done.stdout


@pytest.fixture(scope="session")
def track_issue(cleanup: Callable) -> Callable[[int], None]:
    """Schedule deletion (or closing, when deletion is not permitted) of an issue a test created through the CLI."""
    def track(number: int) -> None:
        def remove() -> None:
            deleted = subprocess.run(["gh", "issue", "delete", str(number), "-R", LIVE_REPO, "--yes"], capture_output=True)
            if deleted.returncode and b"deleted" not in deleted.stderr:
                gh_live("issue", "close", str(number), "-R", LIVE_REPO, "--reason", "not planned")
        cleanup(remove)
    return track


@pytest.fixture(scope="session")
def live_issue(live: Callable, track_issue: Callable, run_id: str, tmp_path_factory: pytest.TempPathFactory) -> Callable[..., dict]:
    """Create a throwaway issue in the live repo; it is deleted (or closed) at session end."""
    def create(title: str, text: str = "Live test body.\n", labels: tuple[str, ...] = ()) -> dict:
        path = tmp_path_factory.mktemp("issue") / "body.md"
        path.write_text(text, encoding="utf-8")
        flags = [part for label in labels for part in ("--label", label)]
        issue = live("issue", "create", "--repo", LIVE_REPO, "--title", f"[{run_id}] {title}", "--body-file", path, *flags).data
        track_issue(issue["number"])
        return issue
    return create


def eventually(check: Callable[[], Any], *, timeout: float = 30.0, interval: float = 2.0) -> Any:
    """Poll for GitHub's eventually consistent reads (label-filtered issue lists lag a few seconds)."""
    deadline = time.monotonic() + timeout
    while True:
        value = check()
        if value:
            return value
        assert time.monotonic() < deadline, "GitHub did not reflect the write in time"
        time.sleep(interval)


def quiet(*args: str) -> None:
    """Idempotent cleanup call: an already-removed resource is fine, any other failure is raised."""
    done = subprocess.run(["gh", *args], capture_output=True, text=True)
    gone = ("Not Found", "Reference does not exist", "Could not resolve", "not found")
    if done.returncode and not any(marker in done.stderr for marker in gone):
        raise subprocess.SubprocessError(f"gh {' '.join(args)} failed: {done.stderr.strip()}")


@pytest.fixture(scope="session")
def fresh_clone(live_ready: None, tmp_path_factory: pytest.TempPathFactory) -> Callable[[str], Path]:
    """Clone of the live repository with a committer identity and the gh credential helper."""
    def clone(name: str) -> Path:
        root = tmp_path_factory.mktemp(name) / "brain"
        subprocess.run(["git", "clone", "-q", f"https://github.com/{LIVE_REPO}.git", str(root)],
                       check=True, env={**os.environ, **LIVE_GIT_ENV})
        git(root, "config", "user.email", "live-test@example.invalid")
        git(root, "config", "user.name", "Live Test")
        return root
    return clone
