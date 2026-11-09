from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[3] / "plugins/wf/skills/github"
SCRIPT = SKILL / "scripts/github.py"
sys.path.insert(0, str(SCRIPT.parent))

from github_cli.cli import main
from github_cli.gh import Gh

HEAD = "a" * 40
BASE = "b" * 40
REF = "acme/work#17"


def test_local_entry_point_creates_branch_and_commits_exact_paths(tmp_path):
    checkout = tmp_path / "source"
    checkout.mkdir()

    def git(*args):
        return subprocess.check_output(["git", "-C", str(checkout), *args], text=True).strip()

    def cli(*args, code=0):
        result = subprocess.run([sys.executable, str(SCRIPT), *args, "--checkout", str(checkout)],
                                cwd=tmp_path, text=True, capture_output=True)
        assert result.returncode == code, result.stderr
        return json.loads(result.stdout) if code == 0 else result.stderr

    git("init", "-q")
    git("config", "user.email", "test@example.invalid")
    git("config", "user.name", "Test")
    git("commit", "--allow-empty", "-qm", "initial")
    base = git("rev-parse", "HEAD")
    assert cli("branch", "create", "--name", "feat/slice", "--start", base)["head"] == base
    git("switch", "feat/slice")
    message = tmp_path / "message"
    message.write_text("ccode(PAY-12 acme/work#17): ship slice\n\nContext\n")
    (checkout / "selected.txt").write_text("selected")
    (checkout / "other.txt").write_text("unrelated")
    commit = ("commit", "create", "--expected", base, "--message-file", str(message), "selected.txt")
    result = cli(*commit)
    assert git("show", "--format=", "--name-only", result["head"]) == "selected.txt"
    assert git("status", "--porcelain") == "?? other.txt"
    history = cli("commit", "history", "--base", base, "--tip", result["head"], "--ccode")["commits"]
    assert [(item["sha"], item["body"]) for item in history] == [(result["head"], "Context\n")]
    assert "HEAD changed" in cli(*commit, code=2)


def test_issue_reconciles_a_lost_create_without_a_duplicate(tmp_path, capsys):
    body = tmp_path / "issue.md"
    body.write_text("Exact body with quotes, `code` and a final newline.\n")
    issues = []

    def runner(argv):
        if "--paginate" in argv:
            return 0, json.dumps([issues]), ""
        assert argv[2:5] == ["--method", "POST", "repos/acme/work/issues"]
        payload = json.loads(Path(argv[-1]).read_text())
        issues.append({**payload, "number": 17, "html_url": "https://github.com/acme/work/issues/17"})
        return 1, "", "lost response"

    args = ["issue", "create", "--repo", "acme/work", "--title", "Slice", "--body-file", str(body),
            "--label", "spec"]
    assert main(args, gh=Gh(runner)) == 1
    assert "lost response" in capsys.readouterr().err
    assert main(args, gh=Gh(runner)) == 0
    assert json.loads(capsys.readouterr().out)["created"] is False
    assert len(issues) == 1 and issues[0]["body"] == body.read_text()


def test_changed_review_head_blocks_inline_mutation(tmp_path, capsys):
    body = tmp_path / "finding.md"
    body.write_text("Approved body\n")

    def runner(argv):
        assert argv == ["gh", "api", "repos/acme/work/pulls/17"]
        return 0, json.dumps({"state": "open", "head": {"sha": BASE}}), ""

    args = ["review", "inline", REF, "--expected", HEAD, "--path", "src.py", "--line", "4",
            "--body-file", str(body)]
    assert main(args, gh=Gh(runner)) == 2
    assert "changed" in capsys.readouterr().err


@pytest.mark.parametrize("target", ["https://github.com/acme/work/issues/17", "https://other/acme/work/pull/17"])
def test_review_write_rejects_wrong_resource_url(target, capsys):
    def runner(argv):
        pytest.fail(f"unexpected GitHub call: {argv}")

    args = ["review", "inline", target, "--expected", HEAD, "--path", "src.py", "--line", "4",
            "--body-file", "unused.md"]
    assert main(args, gh=Gh(runner)) == 2
    assert "qualified GitHub reference" in capsys.readouterr().err


def test_one_discoverable_skill_routes_to_bundled_tactics():
    router = (SKILL / "SKILL.md").read_text()
    assert router.startswith("---\nname: github\n")
    assert "disable-model-invocation" not in router
    assert list(SKILL.rglob("SKILL.md")) == [SKILL / "SKILL.md"]
    assert not (SKILL.parent / "git-conventions/SKILL.md").exists()
    assert not (SKILL.parent / "worktrees/SKILL.md").exists()
    for path in (SKILL / "tactics").glob("*.md"):
        assert f"](tactics/{path.name})" in router
