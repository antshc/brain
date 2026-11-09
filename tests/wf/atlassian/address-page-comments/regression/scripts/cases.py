"""Case catalogue for the address-page-comments live regression: one check per behavior the
skill relies on, evaluated offline against the artifacts a run leaves in its run directory."""
from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

REVIEWER_ID = "regression-reviewer"
THREADS = ("edit", "delete", "question", "footer")
EDIT_OLD, EDIT_NEW = "three attempts", "five attempts"
DELETED_TEXT = "Legacy export runs nightly."
APPENDED_TEXT = "Owner: Platform team."


@dataclass(frozen=True)
class Case:
    id: str
    title: str
    needs: tuple[str, ...]
    check: Callable[[dict], str | None] = field(repr=False)


@dataclass(frozen=True)
class Outcome:
    case: Case
    status: str  # "pass" | "fail" | "skipped"
    detail: str


def load_artifacts(run_dir: Path) -> dict:
    artifacts: dict = {}
    for path in run_dir.iterdir():
        if path.suffix == ".json" and path.stat().st_size:
            try:
                artifacts[path.stem] = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
        elif path.suffix == ".html" and path.stat().st_size:
            artifacts[path.stem] = path.read_text(encoding="utf-8")
    return artifacts


def node_html(html: str, marker: str) -> str | None:
    """The innermost `<p>`/`<li>`/heading element holding the annotation `marker`."""
    for match in re.finditer(r"<(p|li|h[1-6])\b[^>]*>.*?</\1>", html, re.DOTALL):
        if f'data-annotation-id="{marker}"' in match.group(0):
            return match.group(0)
    return None


def _thread(gate: dict, seed: dict, name: str) -> dict | None:
    return next((t for t in gate.get("threads", []) if t["id"] == seed[name]["id"]), None)


def _gate_1(a: dict) -> str | None:
    gate, seed = a["gate-1"], a["seed"]
    if gate.get("action") != "proceed" or gate["counts"]["pending"] != len(THREADS):
        return f"expected proceed with {len(THREADS)} pending, got {gate.get('action')} {gate.get('counts')}"
    expected = {"edit": "anchored", "delete": "anchored", "question": "anchored", "footer": "page"}
    for name, anchor in expected.items():
        thread = _thread(gate, seed, name)
        if not thread or thread["anchor"] != anchor or thread["replyTarget"] != "thread":
            return f"{name}: expected {anchor}/thread, got {thread and (thread['anchor'], thread['replyTarget'])}"
    return None


def _update_ok(a: dict) -> str | None:
    data = a["update"].get("data") or {}
    data = data.get("content") or data
    return None if a["update"].get("ok", True) is not False and data.get("id") else f"update failed: {a['update'].get('error')}"


def _replaced(a: dict) -> str | None:
    node = node_html(a["after"], a["seed"]["edit"]["marker"])
    if node is None:
        return "edited node lost its annotation"
    return None if EDIT_NEW in node and EDIT_OLD not in node else f"edited node text wrong: {node!r}"


def _untouched(a: dict) -> str | None:
    marker = a["seed"]["question"]["marker"]
    before, after = node_html(a["before"], marker), node_html(a["after"], marker)
    return None if before and before == after else f"untouched node changed: {before!r} -> {after!r}"


def _deleted(a: dict) -> str | None:
    if f'data-annotation-id="{a["seed"]["delete"]["marker"]}"' in a["after"]:
        return "deleted node's annotation still present"
    return None if DELETED_TEXT not in a["after"] else "deleted text still present"


def _appended(a: dict) -> str | None:
    return None if APPENDED_TEXT in a["after"] else "appended paragraph missing"


def _gate_2(a: dict) -> str | None:
    gate, seed = a["gate-2"], a["seed"]
    delete = _thread(gate, seed, "delete")
    if not delete or (delete["anchor"], delete["replyTarget"]) != ("orphaned", "page"):
        return f"delete thread not orphaned: {delete and (delete['anchor'], delete['replyTarget'])}"
    for name in ("edit", "question"):
        thread = _thread(gate, seed, name)
        if not thread or thread["anchor"] != "anchored":
            return f"{name} thread lost its anchor"
    return None if gate["counts"]["pending"] == len(THREADS) else f"pending {gate['counts']['pending']}"


def _thread_replies(a: dict) -> str | None:
    for name in ("edit", "question", "footer"):
        reply = a["replies"].get(name) or {}
        if not reply.get("id") or reply.get("sent", "").strip() not in (reply.get("readBack") or ""):
            return f"{name}: reply missing or read-back mismatch"
    return None


def _page_answer(a: dict) -> str | None:
    answer = a["replies"].get("page") or {}
    link = f"focusedCommentId={a['seed']['delete']['id']}"
    if not answer.get("id"):
        return "page answer not posted"
    return None if link in (answer.get("readBack") or "") else f"page answer lacks {link}"


def _gate_3(a: dict) -> str | None:
    gate = a["gate-3"]
    if gate.get("action") != "skip":
        return f"rerun gate not skip: {gate.get('action')} {gate.get('counts')}"
    return None if gate["counts"]["answered"] == len(THREADS) else f"answered {gate['counts']['answered']}"


def _still_open(a: dict) -> str | None:
    open_ids = {c["id"] for c in a["final-comments"]["data"]["comments"]}
    missing = [name for name in THREADS if a["seed"][name]["id"] not in open_ids]
    return f"resolved or missing: {missing}" if missing else None


RICH_TOKENS = {
    "draw.io diagram": '/static/drawio"',
    "toc macro": 'data-extension-key="toc"',
    "image": 'data-type="media-single"',
    "file attachment": 'data-type="media-group"',
    "panel": 'data-type="panel-',
    "status lozenge": 'data-type="status"',
    "table": "<table",
    "expand": "<details",
    "code block": "<pre",
    "wide breakout": 'data-breakout="wide"',
    "bullet list": "<ul",
    "ordered list": "<ol",
    "blockquote": "<blockquote",
    "rule": "<hr",
}
ATTACHMENTS = ("regression-image.png", "regression-notes.txt", "regression-flow.drawio", "regression-sequence.drawio")


def _rich_present(a: dict) -> str | None:
    missing = [label for label, token in RICH_TOKENS.items() if token not in a["before"]]
    return f"fixture constructs missing before edit: {missing}" if missing else None


def _without(html: str, *nodes: str | None) -> list[str]:
    for node in nodes:
        if node:
            html = html.replace(node, "")
    return [line for line in html.splitlines() if line.strip()]


def untouched_lines(a: dict) -> tuple[list[str], list[str]]:
    """Body lines outside the three intended edits, before and after edits and replies."""
    seed, before, final = a["seed"], a["before"], a["final"]
    appended = re.search(r"<p\b[^>]*>" + re.escape(APPENDED_TEXT) + r"</p>", final)
    return (
        _without(before, node_html(before, seed["edit"]["marker"]), node_html(before, seed["delete"]["marker"])),
        _without(final, node_html(final, seed["edit"]["marker"]), appended and appended.group(0)),
    )


def _rich_preserved(a: dict) -> str | None:
    before, final = untouched_lines(a)
    if before == final:
        return None
    changed = next((b, f) for b, f in zip(before + [""], final + [""]) if b != f)
    return f"untouched content changed: {changed[0][:120]!r} -> {changed[1][:120]!r}"


def _attachment_set(envelope: dict) -> set[tuple[str, str, int]]:
    return {(x["id"], x["title"], x["version"]["number"]) for x in envelope["data"]["results"]}


def _attachments_kept(a: dict) -> str | None:
    before, after = _attachment_set(a["attachments-before"]), _attachment_set(a["attachments-after"])
    titles = {title for _, title, _ in before}
    missing = [name for name in ATTACHMENTS if name not in titles]
    if missing:
        return f"fixture attachments missing: {missing}"
    return None if before == after else f"attachments changed: {sorted(before ^ after)}"


CASES: tuple[Case, ...] = (
    Case("G1", "First gate lists every seeded thread with its anchor", ("gate-1", "seed"), _gate_1),
    Case("E1", "Targeted edit update succeeds", ("update",), _update_ok),
    Case("E2", "replaceNode changes text and keeps the annotation", ("after", "seed"), _replaced),
    Case("E3", "Untouched node is byte-identical after the edit", ("before", "after", "seed"), _untouched),
    Case("E4", "deleteNode removes the node and its annotation", ("after", "seed"), _deleted),
    Case("E5", "appendNodeToEnd adds the requested paragraph", ("after",), _appended),
    Case("G2", "Removed highlight makes its thread orphaned with page reply target", ("gate-2", "seed"), _gate_2),
    Case("R1", "Thread replies post and read back", ("replies",), _thread_replies),
    Case("R2", "Orphaned thread answered in a page comment linking it", ("replies", "seed"), _page_answer),
    Case("G3", "Rerun gate detects every answer and skips", ("gate-3",), _gate_3),
    Case("R3", "No seeded comment resolved", ("final-comments", "seed"), _still_open),
    Case("P1", "Page carries diagrams, media, tables, lists, panels, and other ADF-only constructs", ("before",), _rich_present),
    Case("P2", "Everything outside the edited nodes is byte-identical after edits and replies", ("before", "final", "seed"), _rich_preserved),
    Case("P3", "Attachments (image, file, draw.io) unchanged after edits and replies", ("attachments-before", "attachments-after"), _attachments_kept),
)


def evaluate(artifacts: dict) -> list[Outcome]:
    outcomes = []
    for case in CASES:
        missing = [name for name in case.needs if name not in artifacts]
        if missing:
            outcomes.append(Outcome(case, "skipped", f"missing artifact: {missing[0]}"))
            continue
        try:
            detail = case.check(artifacts)
        except (KeyError, TypeError) as exception:
            detail = f"malformed artifact: {exception!r}"
        outcomes.append(Outcome(case, "fail" if detail else "pass", detail or ""))
    return outcomes
