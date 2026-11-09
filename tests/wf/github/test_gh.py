from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from github_cli import gh as gh_module
from github_cli.gh import Gh, GhError, Ref, UsageError, graphql, parse_ref, read_body, repository, request, run_cmd


@pytest.mark.parametrize("text, expected", [
    ("https://github.com/acme/work/issues/17", Ref("acme/work", 17)),
    ("https://github.com/acme/work/pull/17/", Ref("acme/work", 17)),
    ("  acme/work#17  ", Ref("acme/work", 17)),
    ("acme/my.repo-1#3", Ref("acme/my.repo-1", 3)),
])
def test_parse_ref_accepts_qualified_forms(text, expected):
    assert parse_ref(text) == expected


@pytest.mark.parametrize("text", [
    "17", "#17", "acme/work", "acme/work#0", "acme/work#017", "acme/work#-1", "acme/work#1x",
    "http://github.com/acme/work/issues/1", "https://other.com/acme/work/issues/1",
    "https://github.com/acme/work/commit/1", "../work#1", "acme/..#1", "a/b/c#1", "",
])
def test_parse_ref_rejects_unqualified_or_foreign_forms(text):
    with pytest.raises(UsageError, match="qualified GitHub reference"):
        parse_ref(text)


def test_parse_ref_resolves_bare_numbers_only_with_a_default_repository():
    assert parse_ref("#9", "acme/work") == Ref("acme/work", 9)
    assert parse_ref("9", "acme/work") == Ref("acme/work", 9)
    with pytest.raises(UsageError):
        parse_ref("9")


def test_parse_ref_kind_restricts_the_url_resource():
    assert parse_ref("https://github.com/acme/work/pull/1", kind="pull").number == 1
    with pytest.raises(UsageError):
        parse_ref("https://github.com/acme/work/issues/1", kind="pull")
    with pytest.raises(UsageError):
        parse_ref("https://github.com/acme/work/pull/1", kind="issues")


def test_ref_key_is_stable_case_insensitive_and_repository_specific():
    assert Ref("Acme/Work", 5).key == Ref("acme/work", 5).key
    assert Ref("acme/work", 5).key != Ref("acme/other", 5).key
    assert Ref("acme/work", 5).key.startswith("t5-")
    assert str(Ref("acme/work", 5)) == "acme/work#5"


@pytest.mark.parametrize("value", ["acme", "acme/", "/work", "a/b/c", "acme/..", "acme work/x", ""])
def test_repository_rejects_unqualified_names(value):
    with pytest.raises(UsageError):
        repository(value)


def test_repository_returns_valid_name_unchanged():
    assert repository("acme/work.v2") == "acme/work.v2"


def test_read_body_preserves_bytes_exactly(tmp_path):
    path = tmp_path / "b.md"
    path.write_bytes("a\r\nb `c` \u00e9\n\n".encode("utf-8"))
    assert read_body(path) == "a\r\nb `c` \u00e9\n\n"


def test_read_body_rejects_invalid_utf8(tmp_path):
    path = tmp_path / "b.md"
    path.write_bytes(b"\xff\xfe")
    with pytest.raises(UnicodeError):
        read_body(path)


def test_text_raises_with_exit_code_and_stderr():
    gh = Gh(lambda argv: (4, "", "denied\n"))
    with pytest.raises(GhError, match=r"failed \(4\): denied"):
        gh.text("api", "repos/a/b")


def test_text_falls_back_to_stdout_when_stderr_is_empty():
    with pytest.raises(GhError, match="from stdout"):
        Gh(lambda argv: (1, "from stdout", "")).text("x")


def test_json_treats_empty_output_as_null_and_rejects_garbage():
    assert Gh(lambda argv: (0, "", "")).json("x") is None
    with pytest.raises(json.JSONDecodeError):
        Gh(lambda argv: (0, "not json", "")).json("x")


def test_pages_flattens_slurped_pages_and_requests_the_endpoint_once():
    seen = []

    def runner(argv):
        seen.append(argv)
        return 0, json.dumps([[{"n": 1}], [{"n": 2}, {"n": 3}]]), ""

    assert Gh(runner).pages("repos/a/b/issues") == [{"n": 1}, {"n": 2}, {"n": 3}]
    assert seen == [["gh", "api", "--paginate", "--slurp", "repos/a/b/issues"]]


@pytest.mark.parametrize("payload", [{"a": 1}, [{"a": 1}], [[1], 2], None])
def test_pages_rejects_incomplete_paginated_responses(payload):
    with pytest.raises(GhError, match="incomplete paginated response"):
        Gh(lambda argv: (0, json.dumps(payload), "")).pages("e")


def test_git_wrapper_reports_failures():
    with pytest.raises(GhError, match=r"git -C /x rev-parse failed \(128\): fatal"):
        Gh(lambda argv: (128, "", "fatal")).git("-C", "/x", "rev-parse")


def test_run_cmd_reports_missing_binary():
    with pytest.raises(GhError, match="is not installed"):
        run_cmd(["definitely-not-a-binary-xyz"])


def test_run_cmd_pins_gh_host_and_leaves_git_environment_alone(monkeypatch):
    envs = []

    def fake_run(args, **kwargs):
        envs.append(kwargs["env"])
        return subprocess.CompletedProcess(args, 0, "out", "err")

    monkeypatch.setenv("GH_HOST", "ghe.example.com")
    monkeypatch.setattr(gh_module.subprocess, "run", fake_run)
    assert run_cmd(["gh", "x"]) == (0, "out", "err")
    run_cmd(["git", "x"])
    assert envs[0]["GH_HOST"] == "github.com" and envs[1] is None


def test_request_sends_json_through_an_input_file_and_removes_it():
    seen = {}

    def runner(argv):
        path = Path(argv[argv.index("--input") + 1])
        seen["payload"] = json.loads(path.read_text(encoding="utf-8"))
        seen["path"] = path
        seen["argv"] = argv
        return 0, json.dumps({"ok": True}), ""

    assert request(Gh(runner), "repos/a/b/issues", "POST", {"title": "t\u00e9 `x`"}) == {"ok": True}
    assert seen["argv"][:5] == ["gh", "api", "--method", "POST", "repos/a/b/issues"]
    assert seen["payload"] == {"title": "t\u00e9 `x`"}
    assert not seen["path"].exists()


def test_graphql_returns_data_and_rejects_errors_or_missing_data():
    ok = Gh(lambda argv: (0, json.dumps({"data": {"x": 1}}), ""))
    assert graphql(ok, "query { x }", id="1") == {"x": 1}
    for response in ({"data": {"x": 1}, "errors": [{"message": "no"}]}, {"data": None}, {}, [1]):
        with pytest.raises(GhError, match="incomplete data or errors"):
            graphql(Gh(lambda argv, r=response: (0, json.dumps(r), "")), "query { x }")
