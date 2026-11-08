"""Marker routing and safe reconciliation of Address review threads."""
import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

SPEC = importlib.util.spec_from_file_location(
    "address_discussion_state", Path(__file__).parents[1] / "scripts/pr_discussion_state.py"
)
state = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(state)


def comment(body, ident="c1", author="shared", review="COMMENTED"):
    return {"id": ident, "author": {"login": author}, "body": body,
            "createdAt": ident, "updatedAt": ident, "diffHunk": "@@ source",
            "pullRequestReview": {"state": review}}


def marked(role, text="Concern", context=""):
    return f"{text}\n\n<!-- agent:{role}\n{context}\n-->"


def thread(*comments, truncated=False, resolved=False):
    return {"id": "t1", "isResolved": resolved, "isOutdated": False,
            "path": "Cache.cs", "line": 42, "startLine": None, "diffSide": "RIGHT",
            "comments": {"nodes": list(comments), "totalCount": len(comments),
                         "pageInfo": {"hasNextPage": truncated}}}


@pytest.mark.parametrize("role", ["comment", "reply"])
@pytest.mark.parametrize("context", ["", "Evidence: ReadAsync.\nTest passed."])
def test_complete_terminal_blocks(role, context):
    body = marked(role, context=context)
    assert state.terminal_marker(body) == role
    assert state.visible_body(body) == "Concern"


@pytest.mark.parametrize("body", [
    "<!-- agent:comment -->", "<!-- agent:other\n-->",
    "<!-- agent:comment\nmissing close", "<!-- agent:comment\n-->\nAfter",
    "prefix <!-- agent:comment\n-->", "> <!-- agent:comment\n> -->",
    "    <!-- agent:comment\n    -->", "```markdown\n<!-- agent:comment\n-->\n```",
    "```markdown\n<!-- agent:comment\n-->", "~~~\n<!-- agent:comment\n-->",
    "<!-- outer\n<!-- agent:comment\n-->", "`example\n<!-- agent:comment\n-->",
    "<!-- agent:comment \n-->", "<!-- agent:comment\nfirst -->\n-->",
    "<!-- brain:code-review:v1 -->",
])
def test_examples_and_malformed_markers_do_not_route(body):
    assert state.terminal_marker(body) is None
    assert state.visible_body(body) == body


def test_closed_code_fence_does_not_hide_real_terminal_marker():
    body = "```\nexample\n```\n\n" + marked("comment")
    assert state.terminal_marker(body) == "comment"


def test_shared_login_does_not_determine_origin_or_answers():
    finding = state.classify(thread(comment(marked("comment"))))
    human = state.classify(thread(comment("Human concern")))
    assert (finding["origin"], finding["state"]) == ("agent", "pending")
    assert (human["origin"], human["state"]) == ("human/unknown", "pending")
    assert finding["mode"] == human["mode"] == "first-pass"


def test_agent_reply_in_human_thread_keeps_manual_closure():
    result = state.classify(thread(comment("Human concern"), comment(marked("reply"), "c2")))
    assert result["origin"] == "human/unknown"
    assert result["state"] == "answered"


def test_agent_thread_with_reply_always_remains_available_for_reconciliation():
    result = state.classify(thread(comment(marked("comment")), comment(marked("reply", "Fixed"), "c2")))
    assert result["state"] == "reconcile"
    assert result["origin"] == "agent"
    assert result["newComments"] == []
    assert result["lastReply"]["id"] == "c2"
    assert result["comments"][0]["body"] == marked("comment")
    assert result["comments"][0]["visibleBody"] == "Concern"


@pytest.mark.parametrize("opening", ["Human concern", marked("comment")])
def test_same_login_clarification_after_reply_is_follow_up(opening):
    result = state.classify(thread(comment(opening), comment(marked("reply", "Which scope?"), "c2"),
                                   comment("Whole job", "c3")))
    assert result["state"] == "pending"
    assert result["mode"] == "follow-up"
    assert [c["id"] for c in result["newComments"]] == ["c3"]


def test_reply_marker_cannot_claim_ownership_as_opening_comment():
    result = state.classify(thread(comment(marked("reply"))))
    assert result["origin"] == "human/unknown"
    assert result["state"] == "pending"


def test_draft_comment_neither_answers_nor_reopens_thread():
    assert state.classify(thread(comment(marked("comment"), review="PENDING"))) is None
    result = state.classify(thread(comment("Human concern"), comment(marked("reply"), "c2"),
                                   comment("Draft", "c3", review="PENDING")))
    assert result["state"] == "answered"
    assert result["commentCount"] == 3


def test_no_author_dependent_fix_bypass():
    result = state.classify(thread(comment("Human concern"), comment(marked("reply", "fix!: note"), "c2")))
    assert result["state"] == "answered"


def build(raw, **meta_overrides):
    meta = {"state": "OPEN", "isDraft": False, "headRefName": "feat/test", "baseRefName": "main",
            "headRefOid": "sha1", "url": "https://github.com/a/b/pull/1", **meta_overrides}
    with patch.object(state, "pr_metadata", return_value=meta), patch.object(state, "fetch_threads", return_value=raw):
        return state.build_state("a/b#1")


def test_gate_keeps_reconciliation_separate_from_new_replies():
    raw = thread(comment(marked("comment")), comment(marked("reply", "Need decision"), "c2"))
    first, code = build([raw])
    second, _ = build([raw])
    assert code == 0 and first == second
    assert first["action"] == "proceed"
    assert first["counts"]["reconcile"] == 1
    assert first["counts"]["pendingFirstPass"] == first["counts"]["pendingFollowUp"] == 0
    assert first["headOid"] == "sha1"
    assert "actingLogin" not in first


def test_resolved_and_draft_only_threads_are_excluded():
    result, code = build([thread(comment(marked("comment")), resolved=True),
                          thread(comment(marked("comment"), review="PENDING"))])
    assert code == 0 and result["action"] == "skip" and result["threads"] == []


def test_truncation_prevents_any_work_or_closure_even_after_reply():
    result, code = build([thread(comment(marked("comment")), comment(marked("reply"), "c2"), truncated=True)])
    assert code == 1 and result["action"] == "stop"
    assert "truncat" in result["reason"].lower()
    assert result["threads"] == []


def test_truncated_draft_page_cannot_hide_later_published_work():
    result, code = build([thread(comment("Draft", review="PENDING"), truncated=True)])
    assert code == 1 and result["action"] == "stop"


def test_comment_count_mismatch_stops_even_without_next_page_flag():
    raw = thread(comment(marked("comment")))
    raw["comments"]["totalCount"] = 101
    result, code = build([raw])
    assert code == 1 and result["action"] == "stop"


def test_grouped_issue_members_keep_independent_origins():
    agent = thread(comment(marked("comment")), comment(marked("reply"), "c2"))
    human = thread(comment("Same concern"), comment(marked("reply"), "c4"))
    human["id"] = "t2"
    result, _ = build([agent, human])
    assert [t["id"] for t in result["threads"]] == ["t1"]
    assert result["threads"][0]["origin"] == "agent"
    assert [t["id"] for t in result["answeredThreads"]] == ["t2"]


def test_no_prose_status_parser_is_used():
    for prose in ("Fixed and tested.", "Which option?", "Resolution failed."):
        result = state.classify(thread(comment(marked("comment")), comment(marked("reply", prose), "c2")))
        assert result["state"] == "reconcile"


def test_human_answered_gate_skips_and_legacy_is_never_auto_owned():
    result, _ = build([thread(comment("<!-- brain:code-review:v1 -->"), comment(marked("reply"), "c2"))])
    assert result["action"] == "skip"
    assert result["counts"]["answered"] == 1


def test_closed_pr_stops_before_thread_fetch():
    result, code = build([], state="CLOSED")
    assert code == 1 and result["action"] == "stop"


def test_deleted_authors_are_safe_and_irrelevant():
    c = comment(marked("comment")); c["author"] = None
    assert state.classify(thread(c))["origin"] == "agent"


def test_outdated_anchor_is_preserved():
    raw = thread(comment(marked("comment")))
    raw.update(line=None, originalLine=12, originalStartLine=10, isOutdated=True)
    result = state.classify(raw)
    assert result["anchor"]["line"] == 12 and result["anchor"]["basis"] == "original"


def page(nodes, more=False, cursor=None):
    return {"data": {"repository": {"pullRequest": {"reviewThreads": {
        "nodes": nodes, "pageInfo": {"hasNextPage": more, "endCursor": cursor}}}}}}


def test_all_thread_pages_are_fetched():
    import json
    with patch.object(state, "run_gh", side_effect=[json.dumps(page([{"id":"1"}], True, "next")),
                                                  json.dumps(page([{"id":"2"}]))]) as gh:
        assert [t["id"] for t in state.fetch_threads("a", "b", 1)] == ["1", "2"]
        assert "cursor=next" in gh.call_args_list[1].args[0]


def test_missing_pagination_cursor_stops_instead_of_repeating_page():
    import json
    with patch.object(state, "run_gh", return_value=json.dumps(page([], True))):
        with pytest.raises(state.GhError): state.fetch_threads("a", "b", 1)


def test_repeated_pagination_cursor_stops():
    import json
    with patch.object(state, "run_gh", return_value=json.dumps(page([], True, "same"))):
        with pytest.raises(state.GhError): state.fetch_threads("a", "b", 1)


def test_graphql_errors_are_not_partial_success():
    with patch.object(state, "run_gh", return_value='{"errors":[{"message":"denied"}]}'):
        with pytest.raises(state.GhError): state.fetch_threads("a", "b", 1)
