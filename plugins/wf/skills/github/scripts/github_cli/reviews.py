#!/usr/bin/env python3
"""Read-only marker-based PR discussion gate.

Published opening agent:comment blocks own agent threads. Later agent:reply blocks
separate new reply work from unresolved agent-thread reconciliation; no login or
metadata prose determines completion. Human/unknown threads require manual closure.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Callable

from .gh import Gh, GhError, Ref, UsageError, graphql, parse_ref, read_body, request
from .pulls import require_snapshot

PR_URL_RE = re.compile(r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<number>[1-9]\d*)/?$")
PR_SHORT_RE = re.compile(r"^(?P<owner>[^/\s]+)/(?P<repo>[^/#\s]+)#(?P<number>\d+)$")
MARKER_OPENERS = {"<!-- agent:comment": "comment", "<!-- agent:reply": "reply"}
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")

THREADS_QUERY = """
query($owner: String!, $repo: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 50, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          startLine
          originalLine
          originalStartLine
          diffSide
          comments(first: 100) {
            totalCount
            pageInfo { hasNextPage }
            nodes { id author { login } body createdAt updatedAt diffHunk pullRequestReview { state } }
          }
        }
      }
    }
  }
}
"""



def run_gh(args: list[str]) -> str:
    return Gh().text(*args)


def parse_pr_ref(raw: str) -> tuple[str, str, int]:
    match = PR_URL_RE.match(raw.strip()) or PR_SHORT_RE.match(raw.strip())
    if not match:
        raise ValueError(
            f"cannot parse {raw!r} — expected https://github.com/owner/repo/pull/N or owner/repo#N"
        )
    ref = parse_ref(raw, kind="pull")
    owner, repo = ref.repo.split("/")
    return owner, repo, ref.number


def pr_metadata(owner: str, repo: str, number: int) -> dict[str, Any]:
    out = run_gh([
        "pr", "view", str(number),
        "--repo", f"{owner}/{repo}",
        "--json", "headRefName,baseRefName,headRefOid,state,isDraft,url",
    ])
    return json.loads(out)


def fetch_threads(
    owner: str, repo: str, number: int, *, read: Callable[..., str] | None = None
) -> list[dict[str, Any]]:
    threads: list[dict[str, Any]] = []
    cursor: str | None = None
    seen_cursors: set[str] = set()
    while True:
        args = [
            "api", "graphql",
            "-f", f"query={THREADS_QUERY}",
            "-f", f"owner={owner}",
            "-f", f"repo={repo}",
            "-F", f"number={number}",
        ]
        if cursor:
            args += ["-f", f"cursor={cursor}"]
        page = json.loads(read(*args) if read else run_gh(args))
        if page.get("errors"):
            raise GhError(f"GraphQL errors: {json.dumps(page['errors'])}")
        connection = page["data"]["repository"]["pullRequest"]["reviewThreads"]
        threads.extend(connection["nodes"])
        if not connection["pageInfo"]["hasNextPage"]:
            return threads
        cursor = connection["pageInfo"]["endCursor"]
        if not cursor or cursor in seen_cursors:
            raise GhError("Incomplete thread pagination: missing or repeated cursor")
        seen_cursors.add(cursor)


def resolve_anchor(thread: dict[str, Any]) -> dict[str, Any]:
    """Where the thread points in source, falling back to the pre-outdating position."""
    if thread.get("line") is not None:
        return {
            "path": thread["path"],
            "startLine": thread.get("startLine"),
            "line": thread["line"],
            "side": thread.get("diffSide"),
            "basis": "current",
        }
    if thread.get("originalLine") is not None:
        return {
            "path": thread["path"],
            "startLine": thread.get("originalStartLine"),
            "line": thread["originalLine"],
            "side": thread.get("diffSide"),
            "basis": "original",
        }
    return {"path": thread["path"], "startLine": None, "line": None, "side": thread.get("diffSide"), "basis": "unknown"}


def is_pending_review_comment(comment: dict[str, Any]) -> bool:
    """True for a comment still attached to an unsubmitted (draft) review."""
    review = comment.get("pullRequestReview")
    return bool(review) and review.get("state") == "PENDING"


def flatten_comments(thread: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": comment["id"],
            "author": (comment.get("author") or {}).get("login"),
            "body": comment.get("body", ""),
            "createdAt": comment.get("createdAt"),
            "updatedAt": comment.get("updatedAt"),
            "visibleBody": visible_body(comment.get("body", "")),
        }
        for comment in thread["comments"]["nodes"]
        if not is_pending_review_comment(comment)
    ]


def terminal_block(body: str) -> tuple[str, int] | None:
    """Recognize a complete terminal block outside Markdown examples and HTML comments."""
    lines = body.splitlines(keepends=True)
    nonempty = [i for i, line in enumerate(lines) if line.strip()]
    if not nonempty or lines[nonempty[-1]].rstrip("\r\n") != "-->":
        return None
    last = nonempty[-1]
    candidates = [i for i in range(last) if lines[i].rstrip("\r\n") in MARKER_OPENERS]
    if not candidates:
        return None
    opening = candidates[-1]
    # An early closing delimiter or nested block is not one complete terminal block.
    prose = "".join(lines[opening + 1:last])
    if "-->" in prose or "<!--" in prose:
        return None
    fence: str | None = None
    fence_length = 0
    in_comment = False
    code_ticks = 0
    for line in lines[:opening]:
        text = line.rstrip("\r\n")
        if fence is not None:
            if re.fullmatch(r" {0,3}" + re.escape(fence) + "{" + str(fence_length) + r",}\s*", text):
                fence = None
            continue
        match = FENCE_RE.match(text)
        if not in_comment and not code_ticks and match:
            run, rest = match.groups()
            if run[0] != "`" or "`" not in rest:
                fence, fence_length = run[0], len(run)
                continue
        # Quoted and indented examples cannot open a top-level HTML comment/code span.
        if text.startswith((">", "    ", "\t")):
            continue
        for token in re.finditer(r"<!--|-->|`+", text):
            value = token.group()
            if in_comment:
                if value == "-->":
                    in_comment = False
            elif code_ticks:
                if value == "`" * code_ticks:
                    code_ticks = 0
            elif value == "<!--":
                in_comment = True
            elif value.startswith("`"):
                code_ticks = len(value)
    if fence is not None or in_comment or code_ticks:
        return None
    return MARKER_OPENERS[lines[opening].rstrip("\r\n")], sum(map(len, lines[:opening]))


def terminal_marker(body: str) -> str | None:
    block = terminal_block(body)
    return block[0] if block else None


def visible_body(body: str) -> str:
    block = terminal_block(body)
    return body[:block[1]].rstrip() if block else body


def classify(thread: dict[str, Any]) -> dict[str, Any] | None:
    comments = flatten_comments(thread)
    if not comments:
        return None
    connection = thread["comments"]
    truncated = connection["pageInfo"]["hasNextPage"] or connection["totalCount"] > len(connection["nodes"])
    origin = "agent" if terminal_marker(comments[0]["body"]) == "comment" else "human/unknown"
    replies = [i for i, comment in enumerate(comments[1:], 1)
               if terminal_marker(comment["body"]) == "reply"]
    last_reply = replies[-1] if replies else None
    new_comments = comments[last_reply + 1:] if last_reply is not None else comments
    record: dict[str, Any] = {
        "id": thread["id"],
        "anchor": resolve_anchor(thread),
        "isOutdated": thread["isOutdated"],
        "commentCount": thread["comments"]["totalCount"],
        "truncated": truncated,
        "lastAuthor": comments[-1]["author"],
        "lastCommentAt": comments[-1]["createdAt"],
        "origin": origin,
        "state": "pending" if new_comments or truncated else ("reconcile" if origin == "agent" else "answered"),
        "mode": "follow-up" if replies else "first-pass",
        "diffHunk": next((c.get("diffHunk") for c in thread["comments"]["nodes"]
                          if not is_pending_review_comment(c) and c.get("diffHunk")), None),
        "comments": comments,
        "newComments": new_comments,
    }
    if last_reply is not None:
        record["lastReply"] = comments[last_reply]
    return record


def build_state(pr_ref: str) -> tuple[dict[str, Any], int]:
    owner, repo, number = parse_pr_ref(pr_ref)
    meta = pr_metadata(owner, repo, number)

    state: dict[str, Any] = {
        "pr": {"owner": owner, "repo": repo, "number": number, "url": meta.get("url")},
        "prState": meta.get("state"),
        "isDraft": meta.get("isDraft"),
        "headRef": meta.get("headRefName"),
        "headOid": meta.get("headRefOid"),
        "baseRef": meta.get("baseRefName"),
    }

    if meta.get("state") != "OPEN":
        state["action"] = "stop"
        state["reason"] = f"PR state is {meta.get('state')}, not OPEN"
        state["counts"] = {}
        state["threads"] = []
        return state, 1

    raw_threads = fetch_threads(owner, repo, number)
    resolved = [t for t in raw_threads if t["isResolved"]]
    incomplete = [t for t in raw_threads if not t["isResolved"] and (
        t["comments"]["pageInfo"]["hasNextPage"]
        or t["comments"]["totalCount"] > len(t["comments"]["nodes"])
    )]
    if incomplete:
        state.update(action="stop", reason="Truncated review comments; full context required",
                     counts={"total": len(raw_threads), "resolved": len(resolved)}, threads=[])
        return state, 1
    classified = (classify(t) for t in raw_threads if not t["isResolved"])
    live = [record for record in classified if record is not None]

    answered = [t for t in live if t["state"] == "answered"]
    first_pass = [t for t in live if t["state"] == "pending" and t["mode"] == "first-pass"]
    follow_up = [t for t in live if t["state"] == "pending" and t["mode"] == "follow-up"]
    reconcile = [t for t in live if t["state"] == "reconcile"]

    state["counts"] = {
        "total": len(raw_threads),
        "resolved": len(resolved),
        "answered": len(answered),
        "pendingFirstPass": len(first_pass),
        "pendingFollowUp": len(follow_up),
        "reconcile": len(reconcile),
    }
    state["action"] = "skip" if not (first_pass or follow_up or reconcile) else "proceed"
    state["threads"] = first_pass + follow_up + reconcile
    state["answeredThreads"] = [
        {"id": t["id"], "path": t["anchor"]["path"], "lastAuthor": t["lastAuthor"]} for t in answered
    ]
    return state, 0


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("pr", help="PR URL (https://github.com/owner/repo/pull/N) or owner/repo#N")
    parser.add_argument("--json-out", help="also write the JSON state to this path")
    parser.add_argument("--pretty", action="store_true", help="indent the JSON")
    parser.set_defaults(entry=discussion)


def discussion(args: argparse.Namespace) -> int:

    try:
        state, exit_code = build_state(args.pr)
    except (GhError, UsageError, ValueError, KeyError) as exception:
        print(json.dumps({"action": "stop", "reason": str(exception)}))
        return 1

    payload = json.dumps(state, indent=2 if args.pretty else None)
    print(payload)
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")
    return exit_code


def post_inline(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref, kind="pull")
    body = read_body(args.body_file)
    path = f"repos/{ref.repo}/pulls/{ref.number}/comments"
    require_snapshot(gh, ref, args.expected, args.base)
    matches = [
        row for row in gh.pages(f"{path}?per_page=100")
        if row.get("commit_id") == args.expected and row["path"] == args.path
        and row.get("line") == args.line and row.get("side") == "RIGHT" and row["body"] == body
    ]
    if len(matches) > 1:
        raise UsageError("multiple matching findings; reconcile before writing")
    if matches:
        return matches[0]
    require_snapshot(gh, ref, args.expected, args.base)
    posted = request(gh, path, "POST", {
        "body": body, "commit_id": args.expected, "path": args.path, "line": args.line, "side": "RIGHT",
    })
    observed = gh.json("api", f"repos/{ref.repo}/pulls/comments/{posted['id']}")
    if observed.get("body") != body or observed.get("path") != args.path or observed.get("commit_id") != args.expected:
        raise GhError(f"inline comment {posted['id']} could not be verified")
    return observed


def thread_state(gh: Gh, ref: Ref, thread_id: str) -> dict[str, Any]:
    owner, repo = ref.repo.split("/")
    threads = fetch_threads(owner, repo, ref.number, read=gh.text)
    target = next((item for item in threads if item["id"] == thread_id), None)
    if target is None:
        raise UsageError("thread is absent from the qualified PR")
    comments = target["comments"]
    if comments["pageInfo"]["hasNextPage"] or comments["totalCount"] > len(comments["nodes"]):
        raise GhError("truncated thread comments; full context required")
    return target


def change_thread(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref, kind="pull")
    expected = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    require_snapshot(gh, ref, args.expected)
    thread = thread_state(gh, ref, args.thread)
    comments = flatten_comments(thread)
    if args.action == "reply":
        body = read_body(args.body_file)
        if terminal_marker(body) != "reply":
            raise UsageError("review reply must carry the terminal agent:reply marker")
        if comments and comments[:-1] == expected and comments[-1]["body"] == body:
            return comments[-1]
        if thread["isResolved"] or comments != expected:
            raise UsageError("review thread changed; reassess before replying")
        require_snapshot(gh, ref, args.expected)
        result = graphql(gh, """
            mutation($id: ID!, $body: String!) {
              addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $id, body: $body}) {
                comment { id body updatedAt }
              }
            }
        """, id=args.thread, body=body)
        reply = result.get("addPullRequestReviewThreadReply", {}).get("comment")
        observed = flatten_comments(thread_state(gh, ref, args.thread))
        if not reply or observed[:-1] != expected or not observed or observed[-1]["id"] != reply["id"] or observed[-1]["body"] != body:
            raise GhError("review reply could not be verified; reconcile before retrying")
        return observed[-1]
    if comments != expected:
        raise UsageError("review thread changed; reassess before resolving")
    if thread["isResolved"]:
        return {"id": args.thread, "isResolved": True}
    if not comments or terminal_marker(comments[0]["body"]) != "comment" or terminal_marker(comments[-1]["body"]) != "reply":
        raise UsageError("only an answered agent-owned thread can be resolved")
    require_snapshot(gh, ref, args.expected)
    result = graphql(gh, """
        mutation($id: ID!) {
          resolveReviewThread(input: {threadId: $id}) { thread { id isResolved } }
        }
    """, id=args.thread)
    resolved = result.get("resolveReviewThread", {}).get("thread")
    observed = thread_state(gh, ref, args.thread)
    if not resolved or resolved.get("id") != args.thread or not resolved.get("isResolved") or not observed["isResolved"]:
        raise GhError("review thread resolution could not be verified")
    return resolved
