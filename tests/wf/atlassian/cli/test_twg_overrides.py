from __future__ import annotations

from pathlib import Path

import pytest

from atl_cli.twg.overrides import Context, OverrideError, plan


def _context(tmp_path: Path, resolved: dict | None = None, calls: list | None = None) -> Context:
    def resolve(args: list[str]) -> dict:
        if calls is not None:
            calls.append(args)
        return resolved or {}

    return Context(workdir=tmp_path, resolve=resolve)


@pytest.mark.parametrize(
    "args",
    [
        ["jira", "workitem", "query", "--jql", "x"],
        ["confluence", "content", "get", "12", "--format", "html"],
        ["confluence", "content", "get", "12", "--detail", "summary"],
        ["confluence", "content", "get", "12", "-o", "json", "--output-file", "p.json"],
        ["confluence", "content", "update", "12", "--edits-file", "e.json", "--snapshot-token", "t"],
        ["confluence", "content", "create", "--content-type", "folder", "--space-id", "1", "--title", "F"],
        ["jira", "workitem", "get", "ABC-1", "--comments", "-o", "json"],
        ["jira", "workitem", "get", "ABC-1", "--fields", "summary"],
        ["jira", "workitem", "update", "--id", "ABC-1", "--description", "<p>x</p>", "--description-format", "html"],
        ["jira", "workitem", "update", "--id", "ABC-1", "--status", "Done"],
    ],
)
def test_non_markdown_commands_pass_through(tmp_path, args):
    assert plan(args, _context(tmp_path)) is None


def test_page_url_reads_markdown_through_fetch_page(tmp_path):
    delegate = plan(
        ["confluence", "content", "get", "https://org.atlassian.net/wiki/spaces/S/pages/42/T", "--output-file", "p.md", "--comments", "skip"],
        _context(tmp_path),
    )

    assert delegate.command == "fetch-page"
    assert delegate.argv == ["--page-id", "42", "--md-path", "p.md", "--site", "https://org.atlassian.net", "--comments", "skip"]


def test_tiny_link_resolves_through_twg_before_fetching(tmp_path):
    calls: list = []

    delegate = plan(
        ["confluence", "content", "get", "https://org.atlassian.net/wiki/x/AbC", "--format", "md", "--output-file", "p.md"],
        _context(tmp_path, {"data": {"id": "77"}}, calls),
    )

    assert calls == [["confluence", "content", "get", "https://org.atlassian.net/wiki/x/AbC", "--detail", "summary"]]
    assert delegate.argv[:2] == ["--page-id", "77"]


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["confluence", "content", "get", "12"], "--output-file"),
        (["confluence", "content", "get", "12", "--section", "Intro", "--output-file", "p.md"], "--section"),
        (["confluence", "content", "get", "1", "2", "--output-file", "p.md"], "exactly one"),
        (["confluence", "content", "update", "12", "--body", "x", "--minor-edit"], "--minor-edit"),
        (["confluence", "content", "create", "--content-type", "page", "--space-id", "KEY", "--title", "T", "--body", "x"], "numeric"),
        (["jira", "workitem", "get", "ari:cloud:jira:1", "--output-file", "w.md"], "not a work-item key"),
        (["jira", "workitem", "create", "--description", "x", "--summary", "S"], "--space, --type"),
    ],
)
def test_markdown_commands_reject_what_they_cannot_honour(tmp_path, args, message):
    with pytest.raises(OverrideError, match=message):
        plan(args, _context(tmp_path))


def test_inline_page_body_publishes_from_a_temp_markdown_file(tmp_path):
    delegate = plan(
        ["confluence", "content", "create", "--space-id", "9", "--parent-id", "5", "--content-type", "page", "--title", "T", "--body", "# T\n", "--ack-body-formats", "-y"],
        _context(tmp_path),
    )

    assert delegate.command == "publish-page" and delegate.publishes
    assert delegate.argv == ["run", "--md-path", str(tmp_path / "body.md"), "--space-id", "9", "--parent-id", "5", "--title", "T"]
    assert (tmp_path / "body.md").read_text() == "# T\n"


def test_page_update_ignores_twg_write_guards(tmp_path):
    delegate = plan(
        ["confluence", "content", "update", "12", "--body-file", "p.md", "--snapshot-token", "t", "--ack-body-formats", "--yes", "--parent-id", "5"],
        _context(tmp_path),
    )

    assert delegate.argv == ["run", "--md-path", "p.md", "--page-id", "12", "--parent-id", "5"]


def test_workitem_browse_url_reads_markdown_through_fetch_work(tmp_path):
    delegate = plan(
        ["jira", "workitem", "get", "https://org.atlassian.net/browse/ABC-7", "--output-file", "w.md", "--attachments", "all"],
        _context(tmp_path),
    )

    assert delegate.command == "fetch-work"
    assert delegate.argv == ["--issue-key", "ABC-7", "--md-path", "w.md", "--site", "https://org.atlassian.net", "--attachments", "all"]


def test_workitem_create_maps_twg_flags_and_keeps_the_rest_for_twg(tmp_path):
    delegate = plan(
        [
            "jira", "workitem", "create", "--space", "ABC", "--type", "Story", "--summary", "S",
            "--description-file", "d.md", "--parent", "ABC-1", "--fields-json", '{"customfield_1": 3}',
            "--assignee", "me", "--labels", "x", "-y",
        ],
        _context(tmp_path),
    )

    assert delegate.argv == [
        "create", "--project", "ABC", "--issue-type", "Story", "--summary", "S", "--markdown", "d.md",
        "--parent", "ABC-1", "--fields-json", str(tmp_path / "fields.json"),
    ]
    assert (tmp_path / "fields.json").read_text() == '{"customfield_1": 3}'
    assert delegate.follow_up == ["--assignee", "me", "--labels", "x"]
