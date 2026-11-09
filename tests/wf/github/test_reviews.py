from __future__ import annotations

import json

import pytest

from conftest import HEAD, FakeGitHub
from github_cli import reviews

REPO = "acme/work"


def message(role: str, text: str = "Finding") -> str:
    return f"{text}\n\n<!-- agent:{role}\n\n-->"


def node(ident: str, body: str, login: str = "bot") -> dict:
    return {"id": ident, "author": {"login": login}, "body": body, "createdAt": ident, "updatedAt": ident,
            "diffHunk": "@@", "pullRequestReview": {"state": "COMMENTED"}}


class Threads:
    """GraphQL backend holding review threads of one pull request."""

    def __init__(self) -> None:
        self.threads: list[dict] = []
        self.apply_mutations = True
        self.truncated = False

    def add(self, *comments: dict, resolved: bool = False, ident: str = "T1") -> dict:
        thread = {"id": ident, "isResolved": resolved, "isOutdated": False, "path": "a.py", "line": 3, "startLine": None,
                  "diffSide": "RIGHT", "comments": {"nodes": list(comments), "totalCount": len(comments),
                                                    "pageInfo": {"hasNextPage": False}}}
        self.threads.append(thread)
        return thread

    def snapshot(self, thread: dict) -> list[dict]:
        return reviews.flatten_comments(thread)

    def __call__(self, query: str, variables: dict) -> dict:
        if "reviewThreads" in query:
            nodes = self.threads
            if self.truncated:
                nodes = [{**t, "comments": {**t["comments"], "totalCount": 99}} for t in nodes]
            return {"data": {"repository": {"pullRequest": {"reviewThreads": {
                "pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": nodes}}}}}
        thread = next(t for t in self.threads if t["id"] == variables["id"])
        if "addPullRequestReviewThreadReply" in query:
            comment = node(f"R{len(thread['comments']['nodes'])}", variables["body"])
            if self.apply_mutations:
                thread["comments"]["nodes"].append(comment)
                thread["comments"]["totalCount"] += 1
            return {"data": {"addPullRequestReviewThreadReply": {"comment": {"id": comment["id"], "body": comment["body"]}}}}
        if self.apply_mutations:
            thread["isResolved"] = True
        return {"data": {"resolveReviewThread": {"thread": {"id": thread["id"], "isResolved": True}}}}


@pytest.fixture
def pull(fake: FakeGitHub) -> str:
    return f"{REPO}#{fake.add_pull()}"


@pytest.fixture
def threads(fake: FakeGitHub, pull: str) -> Threads:
    backend = Threads()
    fake.graphql_handler = backend
    return backend


def inline(run, fake, pull, body, *, line=4, head=HEAD, extra=()):
    return run("review", "inline", pull, "--expected", head, "--path", "src.py", "--line", line,
               "--body-file", body(message("comment")), *extra, gh=fake)


def test_inline_posts_a_right_side_comment_on_the_reviewed_commit(run, fake, pull, body):
    result = inline(run, fake, pull, body)
    assert result.code == 0
    stored = next(iter(fake.review_comments.values()))
    assert (stored["commit_id"], stored["path"], stored["line"], stored["side"]) == (HEAD, "src.py", 4, "RIGHT")


def test_inline_is_idempotent_and_distinguishes_lines(run, fake, pull, body):
    first = inline(run, fake, pull, body)
    assert inline(run, fake, pull, body).data["id"] == first.data["id"]
    inline(run, fake, pull, body, line=5)
    assert len(fake.review_comments) == 2


@pytest.mark.parametrize("head, base, state", [("c" * 40, None, "open"), (HEAD, "c" * 40, "open"), (HEAD, None, "closed")])
def test_inline_never_writes_when_the_pull_request_changed(run, fake, body, head, base, state):
    number = fake.add_pull(state=state)
    extra = ("--base", base) if base else ()
    result = inline(run, fake, f"{REPO}#{number}", body, head=head, extra=extra)
    assert result.code == 2 and fake.writes() == []


def test_inline_refuses_to_guess_between_duplicate_findings(run, fake, pull, body):
    number = int(pull.split("#")[1])
    for ident in (1, 2):
        fake.review_comments[ident] = {"id": ident, "pull": number, "commit_id": HEAD, "path": "src.py", "line": 4,
                                       "side": "RIGHT", "body": message("comment")}
    assert inline(run, fake, pull, body).code == 2


def test_inline_rejects_a_post_that_cannot_be_read_back(run, fake, pull, body):
    original = fake._route

    def tampering(method, endpoint, payload, fields):
        status, result = original(method, endpoint, payload, fields)
        if method == "GET" and "pulls/comments/" in endpoint:
            result = {**result, "path": "elsewhere.py"}
        return status, result

    fake._route = tampering
    result = inline(run, fake, pull, body)
    assert result.code == 1 and "could not be verified" in result.err


def reply(run, fake, pull, thread, snapshot, body, text=None, head=HEAD, action="reply"):
    path = body(json.dumps(snapshot), "snapshot.json")
    args = ["review", action, pull, "--expected", head, "--thread", thread["id"], "--snapshot", path]
    if action == "reply":
        args += ["--body-file", body(text if text is not None else message("reply", "Done"), "reply.md")]
    return run(*args, gh=fake)


def test_reply_appends_to_an_unchanged_thread_and_verifies(run, fake, pull, threads, body):
    thread = threads.add(node("C1", message("comment")))
    result = reply(run, fake, pull, thread, threads.snapshot(thread), body)
    assert result.code == 0 and result.data["body"].endswith("-->") and len(thread["comments"]["nodes"]) == 2


def test_reply_is_idempotent_after_it_was_already_posted(run, fake, pull, threads, body):
    thread = threads.add(node("C1", message("comment")))
    before = threads.snapshot(thread)
    reply(run, fake, pull, thread, before, body)
    again = reply(run, fake, pull, thread, before, body)
    assert again.code == 0 and len(thread["comments"]["nodes"]) == 2


def test_reply_requires_the_terminal_reply_marker(run, fake, pull, threads, body):
    thread = threads.add(node("C1", message("comment")))
    result = reply(run, fake, pull, thread, threads.snapshot(thread), body, text="no marker")
    assert result.code == 2 and "agent:reply" in result.err and len(thread["comments"]["nodes"]) == 1


def test_reply_refuses_a_thread_that_changed_since_the_snapshot(run, fake, pull, threads, body):
    thread = threads.add(node("C1", message("comment")))
    stale = threads.snapshot(thread)
    thread["comments"]["nodes"].append(node("C2", "late human comment", "human"))
    thread["comments"]["totalCount"] = 2
    result = reply(run, fake, pull, thread, stale, body)
    assert result.code == 2 and "changed" in result.err and len(thread["comments"]["nodes"]) == 2


def test_reply_refuses_resolved_unknown_or_truncated_threads(run, fake, pull, threads, body):
    done = threads.add(node("C1", message("comment")), resolved=True)
    assert reply(run, fake, pull, done, threads.snapshot(done), body).code == 2
    ghost = {"id": "NOPE", "comments": {"nodes": []}}
    result = reply(run, fake, pull, ghost, [], body)
    assert result.code == 2 and "absent" in result.err
    live = threads.add(node("C9", message("comment")), ident="T2")
    threads.truncated = True
    assert reply(run, fake, pull, live, threads.snapshot(live), body).code == 1


def test_reply_does_not_claim_success_when_the_reply_is_missing_afterwards(run, fake, pull, threads, body):
    thread = threads.add(node("C1", message("comment")))
    threads.apply_mutations = False
    result = reply(run, fake, pull, thread, threads.snapshot(thread), body)
    assert result.code == 1 and "could not be verified" in result.err


def test_reply_refuses_a_moved_pull_request_head(run, fake, pull, threads, body):
    thread = threads.add(node("C1", message("comment")))
    assert reply(run, fake, pull, thread, threads.snapshot(thread), body, head="c" * 40).code == 2
    assert fake.writes() == []


def test_resolve_closes_an_answered_agent_thread(run, fake, pull, threads, body):
    thread = threads.add(node("C1", message("comment")), node("C2", message("reply")))
    result = reply(run, fake, pull, thread, threads.snapshot(thread), body, action="resolve")
    assert result.data == {"id": "T1", "isResolved": True} and thread["isResolved"]


def test_resolve_leaves_human_or_unanswered_threads_to_a_person(run, fake, pull, threads, body):
    human = threads.add(node("H1", "please fix", "human"), node("H2", message("reply")), ident="T2")
    unanswered = threads.add(node("C1", message("comment")), ident="T3")
    for thread in (human, unanswered):
        result = reply(run, fake, pull, thread, threads.snapshot(thread), body, action="resolve")
        assert result.code == 2 and "answered agent-owned" in result.err and not thread["isResolved"]


def test_resolve_refuses_a_changed_thread_and_accepts_an_already_resolved_one(run, fake, pull, threads, body):
    thread = threads.add(node("C1", message("comment")), node("C2", message("reply")))
    stale = threads.snapshot(thread)
    thread["comments"]["nodes"].append(node("C3", "human follow-up", "human"))
    thread["comments"]["totalCount"] = 3
    assert reply(run, fake, pull, thread, stale, body, action="resolve").code == 2
    resolved = threads.add(node("D1", "x"), resolved=True, ident="T2")
    result = reply(run, fake, pull, resolved, threads.snapshot(resolved), body, action="resolve")
    assert result.data == {"id": "T2", "isResolved": True}


def test_resolve_does_not_claim_success_when_the_thread_stays_open(run, fake, pull, threads, body):
    thread = threads.add(node("C1", message("comment")), node("C2", message("reply")))
    threads.apply_mutations = False
    result = reply(run, fake, pull, thread, threads.snapshot(thread), body, action="resolve")
    assert result.code == 1 and "could not be verified" in result.err


@pytest.fixture
def pr_view(monkeypatch):
    """Route reviews.run_gh, which builds its own Gh, to canned responses."""
    state = {"meta": {"headRefName": "f", "baseRefName": "main", "headRefOid": HEAD, "state": "OPEN", "isDraft": True,
                      "url": "https://github.com/acme/work/pull/1"},
             "threads": {"data": {"repository": {"pullRequest": {"reviewThreads": {
                 "pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": []}}}}}}

    def run_gh(args):
        return json.dumps(state["meta"] if args[0] == "pr" else state["threads"])

    monkeypatch.setattr(reviews, "run_gh", run_gh)
    return state


def test_discussion_entry_prints_state_and_writes_the_json_file(run, capsys, pr_view, tmp_path):
    out = tmp_path / "state.json"
    result = run("review", "discussion", f"{REPO}#1", "--json-out", out)
    assert result.code == 0 and result.data["action"] == "skip"
    assert json.loads(out.read_text()) == result.data


def test_discussion_entry_stops_on_a_closed_pull_request_with_exit_1(run, pr_view):
    pr_view["meta"]["state"] = "CLOSED"
    result = run("review", "discussion", "https://github.com/acme/work/pull/1")
    assert result.code == 1 and result.data["action"] == "stop"


@pytest.mark.parametrize("ref", ["acme/work", "https://github.com/acme/work/issues/1", "#1"])
def test_discussion_entry_stops_on_unparseable_references(run, pr_view, ref):
    result = run("review", "discussion", ref)
    assert result.code == 1 and result.data["action"] == "stop" and "cannot parse" in result.data["reason"]
