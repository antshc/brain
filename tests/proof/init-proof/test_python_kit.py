"""Proof Python kit behavior tests (init-proof scaffold --language python).

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.

Tests that run the scaffolded kit need `playwright` (and its Chromium for the end-to-end one) and skip without it.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[3] / "plugins" / "proof" / "skills" / "init-proof"
SCRIPT_PATH = SKILL_DIR / "scripts" / "scaffold.py"
PY_TEMPLATES = SKILL_DIR / "templates" / "python"

spec = importlib.util.spec_from_file_location("proof_scaffold_python", SCRIPT_PATH)
assert spec and spec.loader
scaffold_module = importlib.util.module_from_spec(spec)
sys.modules["proof_scaffold_python"] = scaffold_module
spec.loader.exec_module(scaffold_module)

MOLE = "python3 -m mole"
HAS_PLAYWRIGHT = importlib.util.find_spec("playwright") is not None


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return tmp_path


def run(repo: Path, surfaces: str = "both", name: str = "Demo shop") -> dict:
    return scaffold_module.scaffold(repo, scaffold_module.parse_surfaces(surfaces), name, install=False, language="python")


def text_files(repo: Path) -> list[Path]:
    return [p for root in (repo / "proof", repo / "mole", repo / ".github") for p in root.rglob("*") if p.is_file()]


class TestLanguageSelection:
    """Feature: Proof Language Selection"""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [("typescript", "typescript"), ("TS", "typescript"), ("python", "python"), (" Py ", "python")],
    )
    def test_language_choice_is_normalised(self, value: str, expected: str) -> None:
        assert scaffold_module.parse_language(value) == expected

    @pytest.mark.parametrize("value", ["", "ruby", "go"])
    def test_unknown_language_is_refused(self, value: str) -> None:
        with pytest.raises(scaffold_module.ScaffoldError, match="Use typescript or python"):
            scaffold_module.parse_language(value)

    def test_language_defaults_to_typescript_on_the_command_line(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        code = scaffold_module.main(["--repo", str(tmp_path), "--surfaces", "web", "--app-name", "x", "--no-install"])
        assert code == 2
        assert "not a pnpm repository" in json.loads(capsys.readouterr().err)["error"]

    def test_python_language_is_accepted_on_the_command_line(self, repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
        code = scaffold_module.main(["--repo", str(repo), "--language", "python", "--surfaces", "api", "--app-name", "x", "--no-install"])
        assert code == 0
        assert json.loads(capsys.readouterr().out)["language"] == "python"


class TestPythonKitGate:
    """Feature: Proof Python Kit Gate"""

    def test_any_folder_without_package_json_is_accepted(self, repo: Path) -> None:
        assert run(repo)["language"] == "python"
        assert not (repo / "package.json").exists()

    def test_old_python_is_refused_and_untouched(self, repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(scaffold_module.sys, "version_info", (3, 9, 0))
        with pytest.raises(scaffold_module.ScaffoldError, match="Python 3.10 or newer"):
            run(repo)
        assert not (repo / "proof").exists()


class TestPythonKitScaffoldOutput:
    """Feature: Proof Python Kit Scaffold Output"""

    def test_both_surfaces_create_the_kit_mole_adapters_and_skill(self, repo: Path) -> None:
        result = run(repo, "both")
        for path in (
            "mole/mole.py", "mole/__main__.py", "proof/kit/run.py", "proof/app.py", "proof/requirements.txt", "proof/test_features.py",
            "proof/features/__init__.py", "proof/features/surfaces/web.py", "proof/features/surfaces/api.py",
            ".github/skills/verify-mole/SKILL.md",
        ):
            assert path in result["created"]
        assert not list((repo / "proof").rglob("*.ts"))

    def test_web_only_has_no_api_adapter_or_api_config(self, repo: Path) -> None:
        run(repo, "web")
        assert not (repo / "proof/features/surfaces/api.py").exists()
        app = (repo / "proof/app.py").read_text()
        assert 'surfaces=["web"]' in app
        assert "ApiConfig" not in app and "WebConfig(" in app
        index = (repo / "proof/features/surfaces/__init__.py").read_text()
        assert "api_surface" not in index and "web_surface" in index

    def test_api_only_has_no_web_adapter_or_web_config(self, repo: Path) -> None:
        run(repo, "api")
        assert not (repo / "proof/features/surfaces/web.py").exists()
        app = (repo / "proof/app.py").read_text()
        assert 'surfaces=["api"]' in app
        assert "WebConfig" not in app and "ApiConfig(" in app
        skill = (repo / ".github/skills/verify-mole/SKILL.md").read_text()
        assert "screenshot" not in skill and "over HTTP" in skill

    @pytest.mark.parametrize("surfaces", ["web", "api", "both"])
    def test_no_marker_or_placeholder_is_left_in_any_file(self, repo: Path, surfaces: str) -> None:
        run(repo, surfaces)
        for path in text_files(repo):
            body = path.read_text()
            assert not re.search(r"<surface:|</surface:|<!-- /?surface|\{\{[A-Z_]+\}\}", body), f"marker left in {path.relative_to(repo)}"

    @pytest.mark.parametrize("surfaces", ["web", "api", "both"])
    def test_every_scaffolded_python_file_is_valid_python(self, repo: Path, surfaces: str) -> None:
        run(repo, surfaces)
        for path in [*(repo / "proof").rglob("*.py"), *(repo / "mole").rglob("*.py")]:
            ast.parse(path.read_text(), filename=str(path))

    def test_verify_mole_skill_and_maps_use_the_python_commands(self, repo: Path) -> None:
        run(repo, "both")
        for path in (repo / ".github/skills/verify-mole").rglob("*.md"):
            assert "pnpm" not in path.read_text(), f"pnpm left in {path.relative_to(repo)}"
        skill = (repo / ".github/skills/verify-mole/SKILL.md").read_text()
        assert f"`{MOLE} doctor`" in skill and "`proof/app.py`" in skill
        assert f"prove: {MOLE} prove --feature example" in (repo / ".github/skills/verify-mole/features/example.md").read_text()

    def test_kit_and_mole_are_copied_byte_for_byte(self, repo: Path) -> None:
        run(repo, "both")
        assert not (repo / "proof/engine").exists()
        for template, target in (("kit", "proof/kit"), ("mole", "mole")):
            sources = [p for p in (PY_TEMPLATES / template).iterdir() if p.is_file()]
            assert sources
            for source in sources:
                assert (repo / target / source.name).read_bytes() == source.read_bytes()

    def test_app_name_is_json_escaped_in_app_py_and_plain_in_the_skill(self, repo: Path) -> None:
        run(repo, "both", name='My "shop"')
        assert 'name="My \\"shop\\""' in (repo / "proof/app.py").read_text()
        assert "# Verify My \"shop\"" in (repo / ".github/skills/verify-mole/SKILL.md").read_text()

    def test_example_map_lists_exactly_the_chosen_surfaces(self, repo: Path) -> None:
        run(repo, "api")
        frontmatter = (repo / ".github/skills/verify-mole/features/example.md").read_text().split("---")[1]
        assert "surfaces:\n  - api" in frontmatter and "web" not in frontmatter

    def test_unresolved_todo_markers_remain_for_the_research_step(self, repo: Path) -> None:
        run(repo, "both")
        assert "TODO(proof)" in (repo / "proof/app.py").read_text()

    def test_typescript_scaffold_is_unchanged_by_the_python_templates(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text("{}")
        (tmp_path / "pnpm-lock.yaml").write_text("")
        result = scaffold_module.scaffold(tmp_path, ["web"], "x", install=False)
        assert result["language"] == "typescript"
        assert not list((tmp_path / "proof").rglob("*.py"))
        assert "pnpm mole doctor" in (tmp_path / ".github/skills/verify-mole/SKILL.md").read_text()


class TestPythonKitNoOverwrite:
    """Feature: Proof Python Kit No Overwrite"""

    def test_existing_files_are_kept_and_reported_as_skipped(self, repo: Path) -> None:
        (repo / "proof").mkdir()
        (repo / "proof/app.py").write_text("# mine\n")
        result = run(repo)
        assert "proof/app.py" in result["skipped"]
        assert (repo / "proof/app.py").read_text() == "# mine\n"

    def test_second_run_creates_nothing(self, repo: Path) -> None:
        run(repo)
        assert run(repo)["created"] == []


class TestPythonKitInstall:
    """Feature: Proof Python Kit Install"""

    def test_requirements_list_the_kit_dependencies(self, repo: Path) -> None:
        run(repo)
        packages = {re.split(r"[<>=]", line)[0] for line in (repo / "proof/requirements.txt").read_text().split()}
        assert packages == {"playwright", "pytest", "mypy"}

    def test_install_is_skipped_on_request_and_never_touches_package_json(self, repo: Path) -> None:
        result = run(repo)
        assert result["install"] == "skipped"
        assert result["scripts_added"] == [] and result["dev_dependencies_missing"] == []
        assert not (repo / "package.json").exists()

    def test_install_runs_pip_with_the_requirements_file(self, repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        calls: list[list[str]] = []

        class Done:
            returncode, stdout, stderr = 0, "", ""

        monkeypatch.setattr(scaffold_module.subprocess, "run", lambda command, **_: calls.append(command) or Done())
        result = scaffold_module.scaffold(repo, ["web"], "x", install=True, language="python")
        assert result["install"] == "installed"
        assert calls == [[sys.executable, "-m", "pip", "install", "-r", "proof/requirements.txt"]]

    def test_failed_install_is_reported_not_raised(self, repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        class Failed:
            returncode = 1
            stdout = ""
            stderr = "error: externally-managed-environment\n"

        monkeypatch.setattr(scaffold_module.subprocess, "run", lambda *_, **__: Failed())
        result = scaffold_module.scaffold(repo, ["web"], "x", install=True, language="python")
        assert "failed: error: externally-managed-environment" in result["install"]
        assert (repo / "proof/app.py").is_file()


class TestPythonKitGitignore:
    """Feature: Proof Python Kit Gitignore"""

    def test_runs_folder_and_bytecode_are_ignored(self, repo: Path) -> None:
        result = run(repo)
        assert result["gitignore"] == "created"
        assert (repo / ".gitignore").read_text().splitlines() == ["/proof/.runs/", "__pycache__/"]

    def test_existing_entries_are_respected_and_missing_ones_appended(self, repo: Path) -> None:
        (repo / ".gitignore").write_text("node_modules\n**/__pycache__\n")
        assert run(repo)["gitignore"] == "added"
        assert (repo / ".gitignore").read_text().splitlines() == ["node_modules", "**/__pycache__", "/proof/.runs/"]


@pytest.mark.skipif(not HAS_PLAYWRIGHT, reason="playwright is not installed")
class TestPythonKitEngine:
    """Feature: Proof Python Kit Engine"""

    def _scaffold(self, repo: Path, surfaces: str = "both") -> None:
        run(repo, surfaces)
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)

    def _python(self, repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], cwd=repo, capture_output=True, text=True, check=check)

    @pytest.mark.parametrize("surfaces", ["web", "api", "both"])
    def test_scaffolded_selftest_passes(self, repo: Path, surfaces: str) -> None:
        self._scaffold(repo, surfaces)
        result = self._python(repo, "-m", "pytest", "proof/test_features.py", "-q", "-p", "no:cacheprovider", check=False)
        assert result.returncode == 0, result.stdout + result.stderr

    def test_selftest_catches_a_map_that_drifted_from_the_registry(self, repo: Path) -> None:
        self._scaffold(repo)
        (repo / ".github/skills/verify-mole/features/orphan.md").write_text("---\nfeature: orphan\n---\n")
        result = self._python(repo, "-m", "pytest", "proof/test_features.py", "-q", "-p", "no:cacheprovider", check=False)
        assert result.returncode != 0 and "every_feature_has_a_map" in result.stdout

    def test_deep_equality_does_not_treat_true_as_one(self, repo: Path) -> None:
        self._scaffold(repo)
        code = (
            "from proof.kit import same;"
            "assert same({'a': [1, 2]}, {'a': [1, 2]}); assert same(1, 1.0);"
            "assert not same(True, 1); assert not same([1], [1, 2]); assert not same({'a': 1}, {'b': 1})"
        )
        self._python(repo, "-c", code)

    def test_help_lists_commands_with_the_python_invocation(self, repo: Path) -> None:
        self._scaffold(repo)
        out = self._python(repo, "-m", "mole", "help").stdout
        assert f"Usage: {MOLE} <command>" in out and "prove [--feature NAME]" in out

    def test_unknown_command_exits_2_with_a_next_step(self, repo: Path) -> None:
        self._scaffold(repo)
        result = self._python(repo, "-m", "mole", "bogus", check=False)
        assert result.returncode == 2
        assert json.loads(result.stderr)["next"] == f"See the commands: {MOLE} help"

    def test_commands_that_need_a_session_say_nothing_is_running(self, repo: Path) -> None:
        self._scaffold(repo)
        result = self._python(repo, "-m", "mole", "snapshot", check=False)
        assert result.returncode == 2
        assert json.loads(result.stderr)["error"] == "Nothing is running."


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _chromium_installed() -> bool:
    if not HAS_PLAYWRIGHT:
        return False
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        return Path(playwright.chromium.executable_path).exists()


SERVER = """\
import http.server, sys


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'{"ok": true}' if self.path == "/health" else b"<html><head><title>Demo</title></head><body><h1>Hello</h1></body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "application/json" if self.path == "/health" else "text/html")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


http.server.HTTPServer(("127.0.0.1", int(sys.argv[1])), Handler).serve_forever()
"""


@pytest.mark.skipif(not _chromium_installed(), reason="playwright Chromium is not installed")
class TestPythonKitEndToEnd:
    """Feature: Proof Python Kit End To End"""

    @pytest.fixture
    def app_repo(self, repo: Path) -> Path:
        (repo / "src").mkdir()
        (repo / "src/server.py").write_text(SERVER)
        run(repo, "both", name="Demo")
        port = _free_port()
        app = repo / "proof/app.py"
        text = app.read_text().replace("http://localhost:3000", f"http://127.0.0.1:{port}")
        text = text.replace('args=["-m", "your_app"]', f'args=["src/server.py", "{port}"]')
        app.write_text(text)
        for command in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"], ["add", "-A"], ["commit", "-qm", "init"]):
            subprocess.run(["git", *command], cwd=repo, check=True)
        return repo

    def _mole(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-m", "mole", *args], cwd=repo, capture_output=True, text=True, timeout=120)

    def test_up_start_doctor_prove_stale_and_down(self, app_repo: Path) -> None:
        up = subprocess.Popen(
            [sys.executable, "-m", "mole", "up", "--start", "--headless"],
            cwd=app_repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        session = app_repo / "proof/.runs/mole/session.json"
        try:
            deadline = time.monotonic() + 90
            while not session.exists() and time.monotonic() < deadline:
                assert up.poll() is None, up.stderr.read() if up.stderr else "up exited"
                time.sleep(0.5)
            assert session.exists()

            doctor = self._mole(app_repo, "doctor")
            assert doctor.returncode == 0, doctor.stdout
            assert json.loads(doctor.stdout)["ok"] is True

            proved = self._mole(app_repo, "prove")
            receipt = json.loads(proved.stdout)
            assert proved.returncode == 0 and receipt["verdict"] == "PASS"
            assert receipt["surfaces"] == ["web", "api"] and receipt["pageErrors"] == []
            assert Path(receipt["screenshot"]).is_file()
            assert [check["pass"] for check in receipt["checks"]] == [True, True]

            only_api = json.loads(self._mole(app_repo, "prove", "--surface", "api").stdout)
            assert only_api["surfaces"] == ["api"] and "screenshot" not in only_api
            assert any("web surface did not run" in line for line in only_api["next"])

            assert json.loads(self._mole(app_repo, "snapshot").stdout)["heading"] == "Hello"
            assert json.loads(self._mole(app_repo, "api", "get", "/health").stdout)["body"] == {"ok": True}

            (app_repo / "src/server.py").write_text(SERVER + "# changed\n")
            stale = self._mole(app_repo, "prove")
            assert stale.returncode == 2 and "A proof would describe code that is not running" in stale.stderr
            assert "STALE" in self._mole(app_repo, "doctor").stdout

            down = self._mole(app_repo, "down")
            assert json.loads(down.stdout)["ok"] is True
            assert not session.exists()
        finally:
            if up.poll() is None:
                up.terminate()
            up.communicate(timeout=60)

    def test_a_failing_check_is_a_fail_receipt_with_its_hint(self, app_repo: Path) -> None:
        feature = app_repo / "proof/features/example.py"
        feature.write_text(feature.read_text().replace("status.ok, True,", "status.ok, False,"))
        up = subprocess.Popen(
            [sys.executable, "-m", "mole", "up", "--start", "--headless"],
            cwd=app_repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        session = app_repo / "proof/.runs/mole/session.json"
        try:
            deadline = time.monotonic() + 90
            while not session.exists() and time.monotonic() < deadline:
                time.sleep(0.5)
            proved = self._mole(app_repo, "prove", "--surface", "api")
            receipt = json.loads(proved.stdout)
            assert proved.returncode == 1 and receipt["verdict"] == "FAIL"
            assert "did not answer well" in receipt["next"][0]
        finally:
            self._mole(app_repo, "down")
            up.communicate(timeout=60)
