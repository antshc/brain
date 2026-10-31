#!/usr/bin/env python3
"""Run bookkeeping for the atl Confluence round-trip regression.

    init    create a run directory: the fixture page (unique title), its assets, `run.json`,
            and `checklist.md` listing every capability unchecked
    verify  evaluate every capability against the run's artifacts, tick verified items in
            `checklist.md`, write `results.json`; exit 1 unless every capability passed

Artifacts the agent saves into the run directory between the two:
`publish-1.json`, `fetched-1.md` (+ `.assets`), `publish-2.json`, `fetched-2.md`.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from capabilities import CAPABILITIES, Artifacts, Outcome, evaluate  # noqa: E402

REGRESSION_DIR = _SCRIPT_DIR.parent
FIXTURE = REGRESSION_DIR / "fixtures" / "round-trip-page.md"
FIXTURE_ASSETS = REGRESSION_DIR / "fixtures" / "assets"
DEFAULT_RUNS_DIR = REGRESSION_DIR / "runs"
_TITLE_RE = re.compile(r"\A# (.+)\n")
_MARKS = {"pass": "x", "fail": " ", "skipped": " ", "pending": " "}


def render_checklist(run: dict, outcomes: list[Outcome] | None) -> str:
    by_id = {outcome.capability.id: outcome for outcome in outcomes or []}
    if outcomes is None:
        summary = f"pending — 0/{len(CAPABILITIES)} verified"
    else:
        counts = {status: sum(o.status == status for o in outcomes) for status in ("pass", "fail", "skipped")}
        summary = f"{counts['pass']}/{len(CAPABILITIES)} verified, {counts['fail']} failed, {counts['skipped']} skipped"
    lines = [
        "# ATL round-trip regression checklist",
        "",
        f"- Run: `{run['runId']}`",
        f"- Space: `{run['space']}`",
        f"- Page: `{run.get('pageId') or 'not published yet'}` — {run['title']}",
        f"- Result: {summary}",
    ]
    area = None
    for capability in CAPABILITIES:
        if capability.area != area:
            area = capability.area
            lines += ["", f"## {area}", ""]
        outcome = by_id.get(capability.id)
        status = outcome.status if outcome else "pending"
        note = {"pass": "verified", "pending": "pending"}.get(status, f"{status.upper()}: {outcome.detail if outcome else ''}")
        lines.append(f"- [{_MARKS[status]}] **{capability.id}** {capability.title} — {note}")
    return "\n".join(lines) + "\n"


def init_run(space: str, runs_dir: Path, *, now: datetime | None = None) -> dict:
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M%S")
    run_dir = runs_dir / stamp
    run_dir.mkdir(parents=True)
    fixture = FIXTURE.read_text(encoding="utf-8")
    title = f"{_TITLE_RE.match(fixture).group(1)} {stamp}"
    (run_dir / "page.md").write_text(_TITLE_RE.sub(f"# {title}\n", fixture, count=1), encoding="utf-8")
    shutil.copytree(FIXTURE_ASSETS, run_dir / "assets")
    run = {"runId": stamp, "space": space, "title": title, "runDir": str(run_dir), "mdPath": str(run_dir / "page.md")}
    (run_dir / "run.json").write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    (run_dir / "checklist.md").write_text(render_checklist(run, None), encoding="utf-8")
    return run


def _read(path: Path, *, as_json: bool) -> dict | str | None:
    """`None` when the step left nothing usable: absent, empty (a failed step's truncated
    redirect), or unparsable JSON."""
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return None
    if not as_json:
        return text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def load_artifacts(run_dir: Path) -> tuple[dict, Artifacts]:
    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    artifacts = Artifacts(
        title=run["title"],
        run_dir=run_dir,
        publish_1=_read(run_dir / "publish-1.json", as_json=True),
        fetched_1=_read(run_dir / "fetched-1.md", as_json=False),
        publish_2=_read(run_dir / "publish-2.json", as_json=True),
        fetched_2=_read(run_dir / "fetched-2.md", as_json=False),
    )
    if artifacts.publish_1:
        run["pageId"] = artifacts.publish_1.get("pageId")
    return run, artifacts


def verify_run(run_dir: Path) -> list[Outcome]:
    run, artifacts = load_artifacts(run_dir)
    outcomes = evaluate(artifacts)
    (run_dir / "checklist.md").write_text(render_checklist(run, outcomes), encoding="utf-8")
    results = [
        {"id": o.capability.id, "area": o.capability.area, "title": o.capability.title, "status": o.status, "detail": o.detail}
        for o in outcomes
    ]
    (run_dir / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return outcomes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="action", required=True)
    init = sub.add_parser("init", help="Create a run directory and an all-unchecked checklist")
    init.add_argument("--space", required=True, help="Confluence test space key or id, supplied by the user")
    init.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR, help="Parent of run directories")
    verify = sub.add_parser("verify", help="Check the run's artifacts and tick the checklist")
    verify.add_argument("--run", type=Path, required=True, help="Run directory from `init`")
    args = parser.parse_args(argv)

    if args.action == "init":
        print(json.dumps(init_run(args.space, args.runs_dir)))
        return 0
    outcomes = verify_run(args.run)
    summary = {status: [o.capability.id for o in outcomes if o.status == status] for status in ("pass", "fail", "skipped")}
    print(json.dumps({"checklist": str(args.run / "checklist.md"), **summary}))
    return 0 if not summary["fail"] and not summary["skipped"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
