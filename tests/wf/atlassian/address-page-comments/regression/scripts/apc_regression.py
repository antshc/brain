#!/usr/bin/env python3
"""Live regression for the atlassian skill's Address page comments tactic.

    run     create a test page in a user-supplied space, seed review comments, then follow the
            skill's gate, edit, and reply steps with the real twg and `comment_state.py`,
            saving every artifact in a fresh run directory; finishes with verify
    verify  evaluate every case against a run directory's artifacts, write `checklist.md` and
            `results.json`; exit 1 unless every case passed

Every comment shares one Atlassian account, so seeded reviewer comments are relabelled to a
stand-in account id before `comment_state.py` classifies them.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parents[5]
STATE_SCRIPTS = REPO_ROOT / "plugins" / "wf" / "skills" / "atlassian" / "scripts"
for _path in (_SCRIPT_DIR, STATE_SCRIPTS):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import comment_state  # noqa: E402
from cases import APPENDED_TEXT, CASES, EDIT_NEW, EDIT_OLD, REVIEWER_ID, evaluate, load_artifacts, node_html  # noqa: E402

DEFAULT_RUNS_DIR = _SCRIPT_DIR.parent / "runs"
FIXTURE_DIR = _SCRIPT_DIR.parent / "fixtures"
ATL_PY = REPO_ROOT / "plugins" / "wf" / "skills" / "atlassian" / "scripts" / "atl.py"
SEEDS = {
    "edit": ("inline", "retry limit", "Should be five attempts, not three."),
    "delete": ("inline", "Legacy export", "Legacy export is gone; remove this line."),
    "question": ("inline", "rotate daily", "Why daily and not hourly?"),
    "footer": ("footer", None, "Please name an owner for this page."),
}
REPLIES = {
    "edit": "Changed to five attempts.",
    "question": "Daily rotation keeps each file under the upload size limit.",
    "footer": "Added an owner line at the end of the page.",
}
_LOCAL_ID = re.compile(r'data-local-id="([^"]+)"')


class StepError(Exception):
    pass


class Twg:
    def __init__(self, command: str, run_dir: Path) -> None:
        self.command = shlex.split(command)
        self.run_dir = run_dir

    def __call__(self, name: str, *args: str) -> dict:
        out = self.run_dir / f"{name}.json"
        body_to_file = "--output-file" in args
        sink = ["-o", "json"] if body_to_file else ["-o", "json", "--output-file", str(out)]
        result = subprocess.run([*self.command, *args, *sink], capture_output=True, text=True, check=False)
        if body_to_file and not result.returncode:
            out.write_text(result.stdout, encoding="utf-8")
        if result.returncode or not out.is_file():
            raise StepError(f"{name}: twg exit {result.returncode}: {(result.stderr or result.stdout)[-1500:]}")
        envelope = json.loads(out.read_text(encoding="utf-8"))
        data = envelope.get("data")
        if envelope.get("ok") is False or (isinstance(data, dict) and data.get("ok") is False):
            raise StepError(f"{name}: {json.dumps(envelope.get('error') or envelope.get('data'))[:1500]}")
        return envelope


def _comment(envelope: dict) -> dict:
    data = envelope.get("data") or {}
    return data.get("comment") or data


def _list_comments(twg: Twg, page_id: str, name: str) -> list[Path]:
    paths, cursor, number = [], None, 0
    while True:
        number += 1
        args = ["confluence", "content", "comments", "list", "--id", page_id, "--resolution-status", "open",
                "--include-replies", "true", "--body-format", "md", "--limit", "250"]
        envelope = twg(f"{name}-{number}", *args, *(["--cursor", cursor] if cursor else []))
        paths.append(twg.run_dir / f"{name}-{number}.json")
        cursor = (envelope.get("data") or {}).get("nextCursor")
        if not cursor:
            return paths


def _relabel(paths: list[Path], seeded: set[str]) -> list[Path]:
    relabelled = []
    for path in paths:
        envelope = json.loads(path.read_text(encoding="utf-8"))
        for comment in envelope["data"]["comments"]:
            if comment["id"] in seeded:
                comment["authorAccountId"] = REVIEWER_ID
        target = path.with_name(f"relabelled-{path.name}")
        target.write_text(json.dumps(envelope), encoding="utf-8")
        relabelled.append(target)
    return relabelled


def _draft(twg: Twg, page_id: str, name: str) -> tuple[str, str]:
    envelope = twg(f"envelope-{name}", "confluence", "content", "get", page_id, "--draft", "--detail", "full",
                   "--format", "html", "--body-only", "--output-file", str(twg.run_dir / f"{name}.html"))
    return (twg.run_dir / f"{name}.html").read_text(encoding="utf-8"), envelope["data"].get("snapshotToken") or ""


def _gate(twg: Twg, page_id: str, name: str, html: str, seed: dict, account_id: str, site: str) -> dict:
    pages = _relabel(_list_comments(twg, page_id, f"comments-{name}"), {s["id"] for s in seed.values()})
    report = comment_state.build_report(comment_state.load_comment_pages(pages), html, account_id, site)
    (twg.run_dir / f"{name}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def _local_id(node: str) -> str:
    match = _LOCAL_ID.search(node)
    if not match:
        raise StepError(f"no data-local-id on node: {node[:200]}")
    return match.group(1)


def build_edits(html: str, seed: dict) -> list[dict]:
    edit_node = node_html(html, seed["edit"]["marker"])
    delete_node = node_html(html, seed["delete"]["marker"])
    if not edit_node or not delete_node:
        raise StepError("annotated target node not found in draft body")
    return [
        {"name": "replaceNode", "localId": _local_id(edit_node), "value": edit_node.replace(EDIT_OLD, EDIT_NEW)},
        {"name": "deleteNode", "localId": _local_id(delete_node)},
        {"name": "appendNodeToEnd", "value": f"<p>{APPENDED_TEXT}</p>"},
    ]


def _post(twg: Twg, name: str, args: list[str], body: str) -> dict:
    body_file = twg.run_dir / f"reply-{name}.md"
    body_file.write_text(body, encoding="utf-8")
    posted = _comment(twg(f"posted-{name}", *args, "--body-file", str(body_file), "--body-format", "md"))
    read = _comment(twg(f"readback-{name}", "confluence", "content", "comments", "get", "--comment-id", str(posted["id"]), "--body-format", "md"))
    return {"id": posted["id"], "sent": body, "readBack": ((read.get("body") or {}).get("value") or "")}


def _publish(twg: Twg, space: str, title: str, config: Path) -> str:
    space_id = space
    if not space.isdigit():
        space_id = str(twg("space", "confluence", "space", "list", "--keys", space)["data"][0]["id"])
    result = subprocess.run(
        [sys.executable, str(ATL_PY), "publish-page", "run", "--md-path", str(twg.run_dir / "page.md"), "--space-id", space_id,
         "--title", title, "--config", str(config)],
        cwd=twg.run_dir, capture_output=True, text=True, check=False)
    (twg.run_dir / "publish.json").write_text(result.stdout, encoding="utf-8")
    if result.returncode:
        raise StepError(f"publish-page exit {result.returncode}: {result.stderr[-1500:]}")
    return str(json.loads(result.stdout)["pageId"])


def run_scenario(space: str, twg_command: str, account_id: str, site: str, config: Path, runs_dir: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir = runs_dir / stamp
    run_dir.mkdir(parents=True)
    twg = Twg(twg_command, run_dir)
    run = {"runId": stamp, "space": space, "title": f"APC Comments Regression {stamp}", "runDir": str(run_dir)}
    step = "publish"
    try:
        shutil.copy(FIXTURE_DIR / "page.md", run_dir / "page.md")
        shutil.copytree(FIXTURE_DIR / "assets", run_dir / "assets")
        page_id = _publish(twg, space, run["title"], config)
        run["pageId"] = page_id
        (run_dir / "run.json").write_text(json.dumps(run, indent=2), encoding="utf-8")

        step = "seed"
        seed = {}
        for name, (kind, selection, text) in SEEDS.items():
            args = ["confluence", "content", "comments", "create", "--id", page_id, "--comment-type", kind, "--body", text]
            comment = _comment(twg(f"seed-{name}", *args, *(["--text-selection", selection] if selection else [])))
            seed[name] = {"id": str(comment["id"]), "marker": comment.get("inlineMarkerRef")}
        (run_dir / "seed.json").write_text(json.dumps(seed, indent=2), encoding="utf-8")

        step = "gate-1"
        twg("attachments-before", "confluence", "content", "attachments", "list", "--id", page_id, "--limit", "100")
        before, token = _draft(twg, page_id, "before")
        _gate(twg, page_id, "gate-1", before, seed, account_id, site)

        step = "edit"
        edits = build_edits(before, seed)
        (run_dir / "edits.json").write_text(json.dumps(edits, indent=2), encoding="utf-8")
        twg("update", "confluence", "content", "update", page_id, "--snapshot-token", token, "--edits-file", str(run_dir / "edits.json"),
            "--ack-body-formats", "--version-message", "Address review comments (regression)", "-y")
        after, _ = _draft(twg, page_id, "after")

        step = "gate-2"
        gate_2 = _gate(twg, page_id, "gate-2", after, seed, account_id, site)

        step = "reply"
        replies = {}
        for name, text in REPLIES.items():
            replies[name] = _post(twg, name, ["confluence", "content", "comments", "reply", "--comment-id", seed[name]["id"]], text)
        orphan = next(t for t in gate_2["threads"] if t["id"] == seed["delete"]["id"])
        page_body = ("These comments lost their highlighted text, so the answers are here:\n\n"
                     "| Removed text | Comment | Answer |\n| --- | --- | --- |\n"
                     f"| {orphan['selection']} | [Reviewer: remove the legacy export line]({orphan['url']}) | Removed the line. |\n")
        replies["page"] = _post(twg, "page", ["confluence", "content", "comments", "create", "--id", page_id, "--comment-type", "footer"], page_body)
        (run_dir / "replies.json").write_text(json.dumps(replies, indent=2), encoding="utf-8")

        step = "gate-3"
        final, _ = _draft(twg, page_id, "final")
        _gate(twg, page_id, "gate-3", final, seed, account_id, site)
        twg("attachments-after", "confluence", "content", "attachments", "list", "--id", page_id, "--limit", "100")
        final_pages = _list_comments(twg, page_id, "final-list")
        (run_dir / "final-comments.json").write_text(final_pages[0].read_text(encoding="utf-8"), encoding="utf-8")
    except (StepError, KeyError, StopIteration, json.JSONDecodeError) as exception:
        (run_dir / f"{step}.err").write_text(f"{exception!r}\n", encoding="utf-8")
        print(f"step {step} failed: {exception}", file=sys.stderr)
    (run_dir / "run.json").write_text(json.dumps(run, indent=2), encoding="utf-8")
    return run_dir


def render_checklist(run: dict, outcomes: list) -> str:
    counts = {status: sum(o.status == status for o in outcomes) for status in ("pass", "fail", "skipped")}
    lines = [
        "# address-page-comments regression checklist",
        "",
        f"- Run: `{run.get('runId')}`",
        f"- Space: `{run.get('space')}`",
        f"- Page: `{run.get('pageId') or 'not created'}` — {run.get('title')}",
        f"- Result: {counts['pass']}/{len(CASES)} verified, {counts['fail']} failed, {counts['skipped']} skipped",
        "",
    ]
    for outcome in outcomes:
        note = "verified" if outcome.status == "pass" else f"{outcome.status.upper()}: {outcome.detail}"
        lines.append(f"- [{'x' if outcome.status == 'pass' else ' '}] **{outcome.case.id}** {outcome.case.title} — {note}")
    return "\n".join(lines) + "\n"


def verify_run(run_dir: Path) -> list:
    artifacts = load_artifacts(run_dir)
    outcomes = evaluate(artifacts)
    run = artifacts.get("run") or {}
    (run_dir / "checklist.md").write_text(render_checklist(run, outcomes), encoding="utf-8")
    results = [{"id": o.case.id, "title": o.case.title, "status": o.status, "detail": o.detail} for o in outcomes]
    (run_dir / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return outcomes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="action", required=True)
    run = sub.add_parser("run", help="Run the live scenario, then verify")
    run.add_argument("--space", required=True, help="Confluence test space key or id, supplied by the user")
    run.add_argument("--twg", required=True, help="Preflight's credentialed twg command, quoted")
    run.add_argument("--account-id", required=True, help="Preflight accountId")
    run.add_argument("--site", required=True, help="https://<host>")
    run.add_argument("--config", type=Path, required=True, help="Preflight configPath, passed to publish-page")
    run.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR)
    verify = sub.add_parser("verify", help="Evaluate a run directory")
    verify.add_argument("--run", type=Path, required=True)
    args = parser.parse_args(argv)

    run_dir = args.run if args.action == "verify" else run_scenario(args.space, args.twg, args.account_id, args.site, args.config, args.runs_dir)
    outcomes = verify_run(run_dir)
    summary = {status: [o.case.id for o in outcomes if o.status == status] for status in ("pass", "fail", "skipped")}
    print(json.dumps({"runDir": str(run_dir), "checklist": str(run_dir / "checklist.md"), **summary}))
    return 0 if not summary["fail"] and not summary["skipped"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
