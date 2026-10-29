from __future__ import annotations

import json
from pathlib import Path

import pytest

import spec_gh
from spec_gh import Gh, GhError, UsageError


class FakeRunner:
    """Maps a substring of the joined command line to (code, stdout, stderr); records every call."""

    def __init__(self, responses: dict[str, tuple[int, str, str] | str]) -> None:
        self.responses = responses
        self.calls: list[str] = []

    def __call__(self, args: list[str]) -> tuple[int, str, str]:
        line = " ".join(args)
        self.calls.append(line)
        for needle, response in self.responses.items():
            if needle in line:
                return response if isinstance(response, tuple) else (0, response, "")
        raise AssertionError(f"unexpected command: {line}")


def issue(number: int, title: str, *, labels=(), state="open", reason=None, repo="acme/shop", body="") -> dict:
    return {
        "number": number, "title": title, "state": state, "state_reason": reason, "body": body,
        "labels": [{"name": name} for name in labels], "repository_url": f"https://api.github.com/repos/{repo}",
        "html_url": f"https://github.com/{repo}/issues/{number}",
    }


def ticket(ref: str, *, blockers=(), hitl=False, state="open", reason=None) -> dict:
    return {
        "ref": ref, "title": ref, "state": state, "state_reason": reason, "labels": [], "hitl": hitl,
        "blocked_by": [{"ref": b, "state": "open", "state_reason": None} for b in blockers],
    }


class TestParseRef:
    @pytest.mark.parametrize("text", ["acme/shop#12", "https://github.com/acme/shop/issues/12"])
    def test_parses_ref_and_url(self, text):
        assert str(spec_gh.parse_ref(text)) == "acme/shop#12"

    def test_bare_number_needs_default_repo(self):
        assert str(spec_gh.parse_ref("#7", "acme/shop")) == "acme/shop#7"
        with pytest.raises(UsageError):
            spec_gh.parse_ref("#7")


class TestInitiativeId:
    def test_prefix_before_first_colon(self):
        assert spec_gh.initiative_id_of("PAY-12: Refunds: phase 1") == "PAY-12"

    @pytest.mark.parametrize("title", ["No colon", ": empty", "../x: bad", ".hidden: bad", "a/b: bad"])
    def test_unsafe_or_missing_prefix_rejected(self, title):
        with pytest.raises(UsageError):
            spec_gh.initiative_id_of(title)


class TestFrontier:
    def graph(self, *tickets):
        return {"tickets": list(tickets)}

    def test_ready_blocked_deferred_and_done(self):
        graph = self.graph(
            ticket("a#1"), ticket("a#2", blockers=["a#1"]), ticket("a#3", hitl=True), ticket("a#4", blockers=["a#3"]),
            ticket("a#5", state="closed", reason="completed"),
        )
        result = spec_gh.analyse(graph, set())
        assert result["ready"] == ["a#1"]
        assert result["blocked"] == [{"ref": "a#2", "unmet": ["a#1"]}]
        assert {d["ref"]: d["reason"] for d in result["deferred"]} == {"a#3": "hitl", "a#4": "blocked by a#3"}
        assert result["done"] == ["a#5"]

    def test_done_set_unblocks_dependants(self):
        result = spec_gh.analyse(self.graph(ticket("a#1"), ticket("a#2", blockers=["a#1"])), {"a#1"})
        assert result["ready"] == ["a#2"]

    def test_cycle_reported(self):
        result = spec_gh.analyse(self.graph(ticket("a#1", blockers=["a#2"]), ticket("a#2", blockers=["a#1"])), set())
        assert result["cycles"] and result["ready"] == []

    def test_cancelled_blocker_needs_resolution(self):
        t = ticket("a#1")
        t["blocked_by"] = [{"ref": "x/y#9", "state": "closed", "state_reason": "not_planned"}]
        result = spec_gh.analyse(self.graph(t), set())
        assert result["needs_resolution"] == [{"ref": "a#1", "blocker": "x/y#9", "state_reason": "not_planned"}]
        assert result["ready"] == []


class TestPreflight:
    def args(self, tmp_path, **extra):
        values = {"spec": "acme/specs#1", "harness_root": str(tmp_path), "source_repository": None, "base_branch": None}
        return spec_gh.build_parser().parse_args(["preflight", "--spec", values["spec"], "--harness-root", values["harness_root"]]), extra

    def runner(self, tmp_path, labels):
        (tmp_path / "workspace" / "shop" / ".git").mkdir(parents=True)
        return FakeRunner({
            "gh --version": "gh 2", "gh auth status": "ok",
            "api repos/acme/specs/issues/1": json.dumps(issue(1, "PAY-12: Refunds", labels=labels, repo="acme/specs")),
            "gh repo view acme/shop": json.dumps({"nameWithOwner": "acme/shop", "defaultBranchRef": {"name": "main"}}),
            "branches/release%2F1": "{}",
            "remote get-url origin": "git@github.com:acme/shop.git",
        })

    def test_resolves_routing_checkout_and_run_dir(self, tmp_path):
        runner = self.runner(tmp_path, ["spec", "repo:target:acme/shop", "repo:base:release/1"])
        args, _ = self.args(tmp_path)
        result = spec_gh.cmd_preflight(Gh(runner), args)
        assert result["source_repository"] == "acme/shop" and result["base_branch"] == "release/1"
        assert result["initiative_id"] == "PAY-12"
        assert result["integration_branch"] == "feat/PAY-12"
        assert result["run_dir"].endswith("workspace/shop.runs/1")
        assert result["source_root"].endswith("workspace/shop")

    def single_repo_runner(self, tmp_path, ignored):
        (tmp_path / ".git").mkdir(parents=True)
        return FakeRunner({
            "gh --version": "gh 2", "gh auth status": "ok",
            "api repos/acme/specs/issues/1": json.dumps(
                issue(1, "PAY-12: Refunds", labels=["repo:target:acme/shop", "repo:base:main"], repo="acme/specs")),
            "gh repo view acme/shop": json.dumps({"nameWithOwner": "acme/shop", "defaultBranchRef": {"name": "main"}}),
            "branches/main": "{}",
            "remote get-url origin": "https://github.com/acme/shop.git",
            "check-ignore": (0 if ignored else 1, "", ""),
        })

    def test_single_repo_layout_uses_harness_as_source_root(self, tmp_path):
        args, _ = self.args(tmp_path)
        result = spec_gh.cmd_preflight(Gh(self.single_repo_runner(tmp_path, ignored=True)), args)
        assert result["source_root"] == str(tmp_path)
        assert result["run_dir"] == str(tmp_path / "workspace" / "shop.runs" / "1")
        assert result["evidence_root"] == str(tmp_path / "workspace" / "shop.evidence")

    def test_single_repo_layout_falls_back_outside_checkout_when_not_ignored(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        args, _ = self.args(repo)
        result = spec_gh.cmd_preflight(Gh(self.single_repo_runner(repo, ignored=False)), args)
        assert result["run_dir"] == str(tmp_path / "shop.runs" / "1")
        assert result["evidence_root"] == str(tmp_path / "shop.evidence")

    def test_single_repo_layout_rejects_mismatched_origin(self, tmp_path):
        runner = self.single_repo_runner(tmp_path, ignored=True)
        runner.responses["remote get-url origin"] = "git@github.com:other/repo.git"
        args, _ = self.args(tmp_path)
        with pytest.raises(UsageError, match="not a primary checkout"):
            spec_gh.cmd_preflight(Gh(runner), args)

    def test_conflicting_routing_labels_stop(self, tmp_path):
        runner = self.runner(tmp_path, ["repo:target:a/b", "repo:target:c/d", "repo:base:main"])
        args, _ = self.args(tmp_path)
        with pytest.raises(UsageError, match="exactly one"):
            spec_gh.cmd_preflight(Gh(runner), args)

    def test_run_dir_never_reuses_existing(self, tmp_path):
        runner = self.runner(tmp_path, ["repo:target:acme/shop", "repo:base:release/1"])
        (tmp_path / "workspace" / "shop.runs" / "1").mkdir(parents=True)
        args, _ = self.args(tmp_path)
        assert spec_gh.cmd_preflight(Gh(runner), args)["run_dir"].endswith("shop.runs/1-2")


class TestGraphRead:
    def test_saves_files_and_reports_routing_conflict(self, tmp_path):
        spec = issue(1, "PAY-12: X", labels=["repo:target:acme/shop", "repo:base:main"], repo="acme/specs")
        child = issue(5, "slice", labels=["repo:target:other/repo"], repo="acme/specs")
        blocker = issue(4, "dep", state="closed", reason="completed", repo="acme/specs")
        runner = FakeRunner({
            "issues/1/artifacts": "[]",
            "issues/1/comments": "[[]]", "issues/1/sub_issues": json.dumps([[child]]),
            "issues/5/comments": "[[]]", "issues/5/dependencies/blocked_by": json.dumps([[blocker]]),
            "api repos/acme/specs/issues/1": json.dumps(spec),
        })
        args = spec_gh.build_parser().parse_args(["graph", "read", "--spec", "acme/specs#1", "--out", str(tmp_path / "run")])
        graph = spec_gh.cmd_graph_read(Gh(runner), args)
        assert (tmp_path / "run" / "spec.json").exists()
        assert (tmp_path / "run" / "tickets" / "acme_specs_5.json").exists()
        assert graph["frontier"]["ready"] == ["acme/specs#5"]
        assert "conflicts" in graph["problems"][0]


def artifact(number: int, name: str, body: str, kind: str = "generic") -> dict:
    return {
        "id": 900 + number, "number": number, "type": kind, "name": name, "body": body,
        "html_url": f"https://github.com/acme/specs/issues/1/artifacts/{number}", "updated_at": "2026-10-01T00:00:00Z",
    }


class TestSpecArtifacts:
    def read(self, tmp_path, artifact_responses: dict[str, tuple[int, str, str] | str]):
        spec = issue(1, "PAY-12: X", labels=["repo:target:acme/shop", "repo:base:main"], repo="acme/specs")
        runner = FakeRunner({
            **artifact_responses,
            "issues/1/comments": "[[]]", "issues/1/sub_issues": "[[]]",
            "api repos/acme/specs/issues/1": json.dumps(spec),
        })
        args = spec_gh.build_parser().parse_args(["graph", "read", "--spec", "acme/specs#1", "--out", str(tmp_path / "run")])
        return spec_gh.cmd_graph_read(Gh(runner), args), runner

    def test_artifacts_saved_and_listed_in_spec_and_graph(self, tmp_path):
        items = [artifact(1, "Sketch index", "# index", "plan"), artifact(2, "src/A b.txt", "body two"),
                 artifact(3, "view.html", "<p>x</p>", "embedded_html")]
        graph, runner = self.read(tmp_path, {"issues/1/artifacts?per_page=100&page=1": json.dumps(items)})
        records = graph["spec"]["artifacts"]
        assert [Path(r["file"]).name for r in records] == ["001-sketch-index.md", "002-src-a-b-txt.md", "003-view-html.html"]
        assert Path(records[1]["file"]).read_text() == "body two"
        assert records[0] | {"file": None} == {
            "number": 1, "name": "Sketch index", "type": "plan", "file": None,
            "url": "https://github.com/acme/specs/issues/1/artifacts/1", "updated_at": "2026-10-01T00:00:00Z",
        }
        saved = json.loads((tmp_path / "run" / "spec.json").read_text())
        assert saved["artifacts"] == records and saved["artifacts_note"] is None
        assert json.loads((tmp_path / "run" / "artifacts" / "index.json").read_text()) == records
        assert any("X-GitHub-Api-Version" in call for call in runner.calls)

    def test_pages_until_short_page(self, tmp_path):
        first = [artifact(n, f"file {n}", str(n)) for n in range(1, 101)]
        graph, runner = self.read(tmp_path, {
            "artifacts?per_page=100&page=1": json.dumps(first),
            "artifacts?per_page=100&page=2": json.dumps([artifact(101, "last", "101")]),
        })
        assert len(graph["spec"]["artifacts"]) == 101
        assert sum("/artifacts?" in call for call in runner.calls) == 2

    def test_unavailable_endpoint_is_empty_with_note(self, tmp_path):
        graph, _ = self.read(tmp_path, {"issues/1/artifacts": (1, "", "gh: Not Found (HTTP 404)")})
        assert graph["spec"]["artifacts"] == []
        assert "unavailable" in graph["spec"]["artifacts_note"]

    def test_other_artifact_errors_fail(self, tmp_path):
        with pytest.raises(GhError):
            self.read(tmp_path, {"issues/1/artifacts": (1, "", "gh: Server Error (HTTP 500)")})

    def test_rerun_drops_stale_artifact_files(self, tmp_path):
        stale = tmp_path / "run" / "artifacts" / "009-old.md"
        stale.parent.mkdir(parents=True)
        stale.write_text("old")
        self.read(tmp_path, {"issues/1/artifacts": "[]"})
        assert not stale.exists()


class TestIssueOps:
    def test_close_refuses_hitl(self):
        runner = FakeRunner({"api repos/acme/shop/issues/3": json.dumps(issue(3, "t", labels=["hitl"]))})
        args = spec_gh.build_parser().parse_args(["issue", "close", "acme/shop#3", "--commit", "abc", "--branch", "b"])
        with pytest.raises(UsageError, match="hitl"):
            spec_gh.cmd_issue_close(Gh(runner), args)
        assert not any("issue close" in call for call in runner.calls)

    def test_close_verifies_state(self):
        runner = FakeRunner({
            "issue close": "", "api repos/acme/shop/issues/3": json.dumps(issue(3, "t", state="open")),
        })
        args = spec_gh.build_parser().parse_args(["issue", "close", "acme/shop#3", "--comment", "done"])
        with pytest.raises(GhError, match="not closed"):
            spec_gh.cmd_issue_close(Gh(runner), args)

    def test_close_default_comment(self):
        closed = json.dumps(issue(3, "t", state="closed", reason="completed"))
        runner = FakeRunner({"issue close": "", "api repos/acme/shop/issues/3": closed})
        args = spec_gh.build_parser().parse_args(
            ["issue", "close", "acme/shop#3", "--commit", "abc", "--branch", "feat", "--pr", "http://pr"])
        spec_gh.cmd_issue_close(Gh(runner), args)
        assert "--comment Implemented in abc on feat (http://pr)." in next(c for c in runner.calls if "issue close" in c)

    def test_comment_reads_back(self, tmp_path):
        body = tmp_path / "c.md"
        body.write_text("hello\n")
        runner = FakeRunner({
            "issue comment": "https://github.com/acme/shop/issues/3#issuecomment-99",
            "issues/comments/99": json.dumps({"body": "hello"}),
        })
        args = spec_gh.build_parser().parse_args(["issue", "comment", "acme/shop#3", "--body-file", str(body)])
        result = spec_gh.cmd_issue_comment(Gh(runner), args)
        assert result["id"] == 99 and result["problems"] == []

    def test_block_is_idempotent(self):
        runner = FakeRunner({"dependencies/blocked_by": json.dumps([[issue(4, "dep")]])})
        args = spec_gh.build_parser().parse_args(["issue", "block", "acme/shop#5", "--by", "acme/shop#4"])
        result = spec_gh.cmd_issue_block(Gh(runner), args)
        assert result["added"] == [] and not any("POST" in call for call in runner.calls)


class TestTicketCreate:
    def test_reuses_linked_child(self, tmp_path):
        body = tmp_path / "b.md"
        body.write_text("x")
        spec = issue(1, "PAY-12: X", labels=["repo:target:acme/shop"])
        runner = FakeRunner({
            "label list": json.dumps([{"name": "repo:target:acme/shop"}]),
            "issues/1/sub_issues": json.dumps([[issue(8, "slice one")]]),
            "api repos/acme/shop/issues/1": json.dumps(spec),
        })
        args = spec_gh.build_parser().parse_args(
            ["ticket", "create", "--spec", "acme/shop#1", "--title", "slice one", "--body-file", str(body)])
        assert spec_gh.cmd_ticket_create(Gh(runner), args) == {"ref": "acme/shop#8", "created": False, "linked": True}
        assert not any("issue create" in call for call in runner.calls)


class TestPrBody:
    def test_rationale_must_be_bullets(self):
        with pytest.raises(UsageError, match="rationale"):
            spec_gh.build_body("PAY-12", "Added a check\n", [], [], "", "")
        with pytest.raises(UsageError):
            spec_gh.build_body("PAY-12", "", [], [], "", "")

    def test_initiative_id_first_line_and_links(self):
        body = spec_gh.build_body("PAY-12", "- Prevent duplicate charges.\n", ["acme/shop#3"], ["acme/specs#1"], "", "")
        assert body.splitlines()[0] == "PAY-12"
        assert "Closes acme/shop#3" in body and "Refs acme/specs#1" in body

    def test_user_text_drops_legacy_markers_and_managed_block(self):
        old = (
            "[#12]\nInitiative: PAY-12\nInitiative source: http://x\nPAY-12\n"
            f"{spec_gh.BLOCK_BEGIN}\n- old\n{spec_gh.BLOCK_END}\nMy own note\n"
        )
        assert spec_gh.user_text(old, "PAY-12") == "My own note"

    def test_block_refs_only_read_managed_block(self):
        body = f"Closes a/b#1\n{spec_gh.BLOCK_BEGIN}\nCloses a/b#2\nRefs a/b#3\n{spec_gh.BLOCK_END}"
        assert spec_gh.block_refs(body, "Closes") == ["a/b#2"]
        assert spec_gh.block_refs(body, "Refs") == ["a/b#3"]


class TestPrPublish:
    def args(self, tmp_path, *extra):
        rationale = tmp_path / "why.md"
        rationale.write_text("- Prevent duplicate charges.\n")
        return spec_gh.build_parser().parse_args([
            "pr", "publish", "--source-repository", "acme/shop", "--base", "main", "--head", "feat",
            "--title", "PAY-12: Refunds", "--initiative-id", "PAY-12", "--rationale-file", str(rationale), *extra])

    def view(self, body, draft=True):
        return json.dumps({
            "url": "https://github.com/acme/shop/pull/9", "title": "PAY-12: Refunds", "body": body, "headRefOid": "abc",
            "isDraft": draft, "baseRefName": "main", "headRefName": "feat", "state": "OPEN",
        })

    def test_creates_draft_and_verifies(self, tmp_path):
        body = "PAY-12\n\nCloses acme/shop#3\n"
        runner = FakeRunner({
            "api repos/acme/shop/issues/3": json.dumps(issue(3, "t", state="closed", reason="completed")),
            "pr list": "[]", "pr create": "https://github.com/acme/shop/pull/9",
            "pr view": self.view(body), "pr checks": (1, "", "no checks reported on the 'feat' branch"),
        })
        result = spec_gh.cmd_pr_publish(Gh(runner), self.args(tmp_path, "--closes", "acme/shop#3"))
        assert "--draft" in next(c for c in runner.calls if "pr create" in c)
        assert result["created"] and result["problems"] == [] and result["checks"]["status"] == "absent"

    def test_update_preserves_user_text_and_accumulates_closes(self, tmp_path):
        old = f"PAY-12\n\n{spec_gh.BLOCK_BEGIN}\n- old\nCloses acme/shop#2\n{spec_gh.BLOCK_END}\n\nMy note\n"
        existing = [{"number": 9, "url": "u", "isDraft": True, "baseRefName": "main", "headRefName": "feat", "body": old}]
        written: list[str] = []

        def runner(args):
            line = " ".join(args)
            if "pr edit" in line:
                written.append(Path(args[args.index("--body-file") + 1]).read_text())
                return 0, "", ""
            return FakeRunner({
                "api repos/acme/shop/issues/3": json.dumps(issue(3, "t")),
                "pr list": json.dumps(existing), "pr view": self.view("PAY-12\n\nCloses acme/shop#2\nCloses acme/shop#3\n"),
                "pr checks": json.dumps([{"name": "ci", "bucket": "pending"}]),
            })(args)

        result = spec_gh.cmd_pr_publish(Gh(runner), self.args(tmp_path, "--closes", "acme/shop#3"))
        assert "Closes acme/shop#2" in written[0] and "Closes acme/shop#3" in written[0] and "My note" in written[0]
        assert written[0].startswith("PAY-12\n")
        assert result["checks"]["status"] == "pending" and not result["created"]

    def test_read_reports_problems(self):
        runner = FakeRunner({
            "pr view": self.view("[#1]\nPAY-12\n", draft=False), "pr checks": json.dumps([{"name": "ci", "bucket": "fail"}]),
        })
        result = spec_gh.read_pr(Gh(runner), "acme/shop", 9, "PAY-12", ["acme/shop#3"])
        assert len(result["problems"]) == 3 and result["checks"]["failed"] == ["ci"]


class TestMain:
    def test_exit_codes(self, capsys):
        runner = FakeRunner({"api repos/acme/shop/issues/3": json.dumps(issue(3, "t", labels=["hitl"]))})
        code = spec_gh.main(["issue", "close", "acme/shop#3", "--comment", "x"], gh=Gh(runner))
        assert code == 2 and "hitl" in capsys.readouterr().err
        failing = FakeRunner({"api": (1, "", "HTTP 404")})
        assert spec_gh.main(["issue", "close", "acme/shop#3", "--comment", "x"], gh=Gh(failing)) == 1


class TestWrites:
    def test_spec_create_ensures_labels_and_reads_back(self, tmp_path):
        body = tmp_path / "plan.md"
        body.write_text("# Plan\n")
        created = issue(7, "PAY-12: Refunds plan", labels=["spec", "repo:target:acme/shop", "repo:base:main"], repo="acme/specs")
        runner = FakeRunner({
            "gh repo view acme/shop": json.dumps({"nameWithOwner": "acme/shop", "defaultBranchRef": {"name": "main"}}),
            "branches/main": "{}", "label list": "[]", "label create": "",
            "issue create": "https://github.com/acme/specs/issues/7", "api repos/acme/specs/issues/7": json.dumps(created),
        })
        args = spec_gh.build_parser().parse_args([
            "spec", "create", "--source-repository", "acme/shop", "--base-branch", "main", "--initiative-id", "PAY-12",
            "--summary", "Refunds  plan", "--body-file", str(body), "--source-note", "plan.md", "--tracker-repository", "acme/specs"])
        result = spec_gh.cmd_spec_create(Gh(runner), args)
        assert result == {"spec": "acme/specs#7", "url": "https://github.com/acme/specs/issues/7", "problems": []}
        assert sum("label create" in call for call in runner.calls) == 3

    def test_ticket_create_new_links_and_verifies(self, tmp_path):
        body = tmp_path / "b.md"
        body.write_text("x")
        spec = issue(1, "PAY-12: X", labels=["repo:target:acme/shop"])
        child = {**issue(8, "slice", repo="acme/shop"), "id": 80}
        listed = [json.dumps([[]]), json.dumps([[child]])]

        class Runner(FakeRunner):
            def __call__(self, args):
                line = " ".join(args)
                if "issues/1/sub_issues" in line and "POST" not in line:
                    self.calls.append(line)
                    return 0, listed.pop(0), ""
                return super().__call__(args)

        runner = Runner({
            "label list": json.dumps([{"name": "repo:target:acme/shop"}]), "issue list": "[]",
            "issue create": "https://github.com/acme/shop/issues/8", "POST": "{}",
            "api repos/acme/shop/issues/1": json.dumps(spec), "api repos/acme/shop/issues/8": "80",
        })
        args = spec_gh.build_parser().parse_args(["ticket", "create", "--spec", "acme/shop#1", "--title", "slice", "--body-file", str(body)])
        assert spec_gh.cmd_ticket_create(Gh(runner), args) == {"ref": "acme/shop#8", "created": True, "linked": True}
        assert any("sub_issue_id=80" in call for call in runner.calls)

    def test_ticket_create_stops_on_ambiguous_matches(self, tmp_path):
        spec = issue(1, "PAY-12: X", labels=["repo:target:acme/shop"])
        runner = FakeRunner({
            "label list": json.dumps([{"name": "repo:target:acme/shop"}]),
            "issues/1/sub_issues": json.dumps([[issue(2, "dup"), issue(3, "dup")]]),
            "api repos/acme/shop/issues/1": json.dumps(spec),
        })
        args = spec_gh.build_parser().parse_args(["ticket", "create", "--spec", "acme/shop#1", "--title", "dup", "--body-file", "-"])
        with pytest.raises(UsageError, match="already titled"):
            spec_gh.cmd_ticket_create(Gh(runner), args)

    def test_block_posts_missing_edge_and_verifies(self):
        gets = [json.dumps([[]]), json.dumps([[issue(4, "dep")]])]

        class Runner(FakeRunner):
            def __call__(self, args):
                line = " ".join(args)
                if "dependencies/blocked_by" in line and "POST" not in line:
                    self.calls.append(line)
                    return 0, gets.pop(0), ""
                return super().__call__(args)

        runner = Runner({"api repos/acme/shop/issues/4": "44", "POST": "{}"})
        args = spec_gh.build_parser().parse_args(["issue", "block", "acme/shop#5", "--by", "acme/shop#4"])
        assert spec_gh.cmd_issue_block(Gh(runner), args)["added"] == ["acme/shop#4"]

    def test_block_fails_when_edge_missing_after_link(self):
        runner = FakeRunner({"dependencies/blocked_by": json.dumps([[]]), "api repos/acme/shop/issues/4": "44"})
        args = spec_gh.build_parser().parse_args(["issue", "block", "acme/shop#5", "--by", "acme/shop#4"])
        with pytest.raises(GhError, match="missing after link"):
            spec_gh.cmd_issue_block(Gh(runner), args)

    def test_edit_body_reports_mismatch(self, tmp_path):
        body = tmp_path / "b.md"
        body.write_text("new")
        runner = FakeRunner({"issue edit": "", "api repos/acme/shop/issues/3": json.dumps(issue(3, "t", body="old"))})
        args = spec_gh.build_parser().parse_args(["issue", "edit-body", "acme/shop#3", "--body-file", str(body)])
        assert spec_gh.cmd_issue_edit_body(Gh(runner), args)["problems"] == ["body differs after edit"]


class TestChecks:
    @pytest.mark.parametrize("rows, status", [
        ([{"name": "a", "bucket": "pass"}], "passed"),
        ([{"name": "a", "bucket": "pass"}, {"name": "b", "bucket": "pending"}], "pending"),
        ([{"name": "a", "bucket": "cancel"}, {"name": "b", "bucket": "pending"}], "failed"),
        ([{"name": "a", "bucket": "skipping"}], "passed"),
    ])
    def test_status_precedence(self, rows, status):
        runner = FakeRunner({"pr checks": (8, json.dumps(rows), "")})
        assert spec_gh.pr_checks(Gh(runner), "acme/shop", 9)["status"] == status

    def test_unexpected_failure_is_an_error(self):
        with pytest.raises(GhError):
            spec_gh.pr_checks(Gh(FakeRunner({"pr checks": (1, "", "HTTP 500")})), "acme/shop", 9)


def test_graph_frontier_command_reads_saved_graph(tmp_path, capsys):
    path = tmp_path / "graph.json"
    path.write_text(json.dumps({"tickets": [ticket("a/b#1"), ticket("a/b#2", blockers=["a/b#1"])]}))
    assert spec_gh.main(["graph", "frontier", "--graph", str(path), "--done", "a/b#1"], gh=Gh(FakeRunner({}))) == 0
    assert json.loads(capsys.readouterr().out)["ready"] == ["a/b#2"]
    assert spec_gh.main(["graph", "frontier", "--graph", str(tmp_path / "missing.json")], gh=Gh(FakeRunner({}))) == 2


@pytest.mark.parametrize("argv", [
    ["graph", "frontier", "--graph", "g.json", "--done", "a/b#1", "a/b#2"],
    ["graph", "frontier", "--graph", "g.json", "--done", "a/b#1", "--done", "a/b#2"],
])
def test_multi_value_flags_accept_space_separated_and_repeated(argv):
    assert spec_gh.build_parser().parse_args(argv).done == ["a/b#1", "a/b#2"]


def test_pr_and_block_flags_accept_space_separated_refs():
    parser = spec_gh.build_parser()
    publish = parser.parse_args(["pr", "publish", "--source-repository", "a/b", "--base", "main", "--head", "h", "--title", "t",
                                 "--initiative-id", "I", "--rationale-file", "r", "--closes", "a/b#1", "a/b#2", "--refs", "a/b#3"])
    assert (publish.closes, publish.refs) == (["a/b#1", "a/b#2"], ["a/b#3"])
    assert parser.parse_args(["pr", "read", "--source-repository", "a/b", "--expect-closes", "a/b#1", "a/b#2"]).expect_closes == ["a/b#1", "a/b#2"]
    assert parser.parse_args(["issue", "block", "a/b#3", "--by", "a/b#1", "a/b#2"]).by == ["a/b#1", "a/b#2"]


class TestInstructionsUseRealCommands:
    ROOT = Path(__file__).resolve().parents[3] / "plugins" / "wf" / "skills" / "implement-spec"

    def commands(self) -> list[tuple[str, ...]]:
        import re

        found = []
        for path in self.ROOT.rglob("*.md"):
            for match in re.finditer(r"(?:`GH_TOOL|\{\{ghTool\}\}) ((?:preflight|spec|graph|ticket|issue|pr)\b(?: (?:create|read|frontier|block|edit-body|comment|close|publish|diff-split)\b)?)", path.read_text()):
                found.append(tuple(match.group(1).split()))
        return found

    def test_every_documented_command_parses(self):
        commands = self.commands()
        assert len(commands) >= 10
        parser = spec_gh.build_parser()
        groups = {action.dest: action for action in parser._subparsers._group_actions}
        for command in commands:
            assert command[0] in groups["group"].choices, command
            nested = groups["group"].choices[command[0]]._subparsers
            if nested:
                assert len(command) == 2 and command[1] in nested._group_actions[0].choices, command

    def test_no_dangling_references_to_removed_files(self):
        text = "\n".join(path.read_text() for path in self.ROOT.rglob("*.md"))
        for removed in ("github_setup", "github_graph", "github_publication", "github_finalize"):
            assert removed not in text


DIFF = (
    "diff --git a/src/a.py b/src/a.py\nindex 1..2 100644\n--- a/src/a.py\n+++ b/src/a.py\n@@ -1 +1 @@\n-x\n+y\n"
    "diff --git a/old name.txt b/new dir/new name.txt\nsimilarity index 90%\nrename from old name.txt\nrename to new dir/new name.txt\n"
    "diff --git a/src_a.py b/src_a.py\n--- a/src_a.py\n+++ b/src_a.py\n@@ -1 +1 @@\n-1\n+2\n"
)


class TestDiffSplit:
    def test_splits_per_file_using_b_side_path(self):
        files = spec_gh.split_diff(DIFF)
        assert [path for path, _ in files] == ["src/a.py", "new dir/new name.txt", "src_a.py"]
        assert files[0][1].startswith("diff --git a/src/a.py") and "+y" in files[0][1] and "rename" not in files[0][1]

    def test_ignores_text_before_first_header(self):
        assert spec_gh.split_diff("noise\n") == []

    def test_writes_files_manifest_and_dedupes_sanitized_names(self):
        result = spec_gh.cmd_pr_diff_split(Gh(FakeRunner({"pr diff": DIFF})), spec_gh.build_parser().parse_args(
            ["pr", "diff-split", "--pr", "https://github.com/acme/shop/pull/9"]))
        out = Path(result["diff_dir"])
        rows = [line.split("\t") for line in (out / "_manifest.tsv").read_text().splitlines()]
        assert result["files"] == 3 and rows[0] == ["src/a.py", "src_a.py"] and rows[2] == ["src_a.py", "src_a.py_"]
        assert (out / "src_a.py").read_text().count("+y") == 1 and (out / "src_a.py_").read_text().count("+2") == 1

    def test_empty_diff_is_an_error(self):
        args = spec_gh.build_parser().parse_args(["pr", "diff-split", "--pr", "9", "--source-repository", "acme/shop"])
        with pytest.raises(GhError, match="never run the subagent"):
            spec_gh.cmd_pr_diff_split(Gh(FakeRunner({"pr diff": ""})), args)
