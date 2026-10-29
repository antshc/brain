#!/usr/bin/env python3
"""GitHub operations for the implement-spec skill: one command per intent, JSON on stdout.

Self-contained: stdlib only, shells out to `gh` and `git`. Errors go to stderr.
Exit codes: 0 ok, 1 GitHub/tool failure, 2 invalid input or unresolved routing,
3 completed but read-back verification reported `problems`.

    preflight   --spec REF [--harness-root P] [--source-repository R --base-branch B]
    spec create --source-repository R --base-branch B --initiative-id I --summary S --body-file F --source-note N
    graph read  --spec REF --out RUN_DIR      (also saves spec issue artifacts under RUN_DIR/artifacts, indexed by name in index.json)
    graph frontier --graph FILE [--done REF ...]
    ticket create --spec REF --title T --body-file F
    issue block REF --by REF [--by REF ...]
    issue edit-body REF --body-file F
    issue comment REF --body-file F
    issue close REF (--commit SHA --branch B [--pr URL] | --comment TEXT)
    pr publish  --source-repository R --base B --head H --title T --initiative-id I
                --rationale-file F [--closes REF ...] [--refs REF ...] [--evidence-file F]
    pr read     --source-repository R (--number N | --head H) [--initiative-id I] [--expect-closes REF ...]
    pr diff-split --pr URL_OR_NUMBER [--source-repository R]

REF is `OWNER/REPO#NUMBER` or an issue URL.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote

REPO_PATTERN = r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"
BLOCK_BEGIN = "<!-- implement-spec:begin -->"
BLOCK_END = "<!-- implement-spec:end -->"
TARGET_PREFIX = "repo:target:"
BASE_PREFIX = "repo:base:"
ARTIFACTS_API_VERSION = "2026-03-10"
ARTIFACTS_PAGE_SIZE = 100
ARTIFACTS_INDEX = "index.json"
Runner = Callable[[list[str]], tuple[int, str, str]]


class UsageError(Exception):
    exit_code = 2


class GhError(Exception):
    exit_code = 1


@dataclass(frozen=True)
class Ref:
    repo: str
    number: int

    def __str__(self) -> str:
        return f"{self.repo}#{self.number}"

    @property
    def file_stem(self) -> str:
        owner, name = self.repo.split("/")
        return f"{owner}_{name}_{self.number}"


def parse_ref(text: str, default_repo: str | None = None) -> Ref:
    text = text.strip()
    match = re.fullmatch(rf"https://github\.com/({REPO_PATTERN})/(?:issues|pull)/(\d+)/?", text)
    match = match or re.fullmatch(rf"({REPO_PATTERN})#(\d+)", text)
    if match:
        return Ref(match.group(1), int(match.group(2)))
    bare = re.fullmatch(r"#?(\d+)", text)
    if bare and default_repo:
        return Ref(default_repo, int(bare.group(1)))
    raise UsageError(f"cannot parse issue reference: {text!r}")


def run_cmd(args: list[str]) -> tuple[int, str, str]:
    try:
        done = subprocess.run(args, check=False, capture_output=True, text=True)
    except FileNotFoundError as exception:
        raise GhError(f"{args[0]} is not installed") from exception
    return done.returncode, done.stdout, done.stderr


class Gh:
    def __init__(self, runner: Runner = run_cmd) -> None:
        self._runner = runner

    def raw(self, *args: str) -> tuple[int, str, str]:
        return self._runner(["gh", *args])

    def text(self, *args: str) -> str:
        code, out, err = self.raw(*args)
        if code:
            raise GhError(f"gh {' '.join(args[:3])} failed ({code}): {(err or out).strip()}")
        return out

    def json(self, *args: str) -> Any:
        return json.loads(self.text(*args) or "null")

    def pages(self, endpoint: str) -> list[dict[str, Any]]:
        return [item for page in self.json("api", "--paginate", "--slurp", endpoint) for item in page]

    def git(self, *args: str) -> str:
        code, out, err = self._runner(["git", *args])
        if code:
            raise GhError(f"git {' '.join(args[:3])} failed ({code}): {(err or out).strip()}")
        return out


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def read_issue(gh: Gh, ref: Ref) -> dict[str, Any]:
    return gh.json("api", f"repos/{ref.repo}/issues/{ref.number}")


def read_comments(gh: Gh, ref: Ref) -> list[dict[str, Any]]:
    return gh.pages(f"repos/{ref.repo}/issues/{ref.number}/comments")


def read_artifacts(gh: Gh, ref: Ref) -> tuple[list[dict[str, Any]], str | None]:
    """Issue artifacts (public preview). The endpoint returns a bare array without Link headers, so pages are looped manually."""
    artifacts: list[dict[str, Any]] = []
    page = 1
    while True:
        try:
            batch = gh.json(
                "api", "-H", f"X-GitHub-Api-Version: {ARTIFACTS_API_VERSION}",
                f"repos/{ref.repo}/issues/{ref.number}/artifacts?per_page={ARTIFACTS_PAGE_SIZE}&page={page}",
            )
        except GhError as exception:
            if page == 1 and re.search(r"HTTP (404|410)", str(exception)):
                return [], f"issue artifacts unavailable for {ref}: {exception}"
            raise
        artifacts.extend(batch or [])
        if len(batch or []) < ARTIFACTS_PAGE_SIZE:
            return artifacts, None
        page += 1


def save_artifacts(artifacts: list[dict[str, Any]], directory: Path) -> list[dict[str, Any]]:
    if directory.exists():
        shutil.rmtree(directory)
    records: list[dict[str, Any]] = []
    for artifact in artifacts:
        slug = re.sub(r"[^a-z0-9]+", "-", artifact["name"].lower()).strip("-") or "artifact"
        suffix = ".html" if artifact["type"] == "embedded_html" else ".md"
        path = directory / f"{artifact['number']:03d}-{slug}{suffix}"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(artifact.get("body") or "", encoding="utf-8")
        records.append({
            "number": artifact["number"], "name": artifact["name"], "type": artifact["type"],
            "url": artifact.get("html_url"), "updated_at": artifact.get("updated_at"), "file": str(path),
        })
    directory.mkdir(parents=True, exist_ok=True)
    (directory / ARTIFACTS_INDEX).write_text(json.dumps(records, indent=2), encoding="utf-8")
    return records


def labels_of(issue: dict[str, Any]) -> list[str]:
    return [label["name"] if isinstance(label, dict) else label for label in issue.get("labels", [])]


def ref_of_api(issue: dict[str, Any]) -> Ref:
    match = re.search(rf"/repos/({REPO_PATTERN})$", issue["repository_url"])
    if not match:
        raise GhError(f"issue has no resolvable repository: {issue.get('html_url')}")
    return Ref(match.group(1), issue["number"])


def single_label(labels: list[str], prefix: str) -> str:
    values = [label[len(prefix):] for label in labels if label.startswith(prefix)]
    if len(values) != 1 or not values[0]:
        raise UsageError(f"expected exactly one `{prefix}*` label, found {values or 'none'}; resolve routing explicitly")
    return values[0]


def validate_initiative_id(value: str) -> str:
    value = value.strip()
    if not value or "/" in value or "\\" in value or ".." in value or value.startswith("."):
        raise UsageError(f"initiative id {value!r} is empty or not a safe single path component")
    return value


def initiative_id_of(title: str) -> str:
    prefix, separator, _ = title.partition(":")
    if not separator:
        raise UsageError(f"title {title!r} has no `<INITIATIVE_ID>:` prefix")
    return validate_initiative_id(prefix)


def ensure_label(gh: Gh, repo: str, name: str, *, color: str | None = None, description: str | None = None) -> bool:
    found = gh.json("label", "list", "--repo", repo, "--search", name, "--limit", "100", "--json", "name")
    if any(label["name"] == name for label in found):
        return False
    extra = (["--color", color] if color else []) + (["--description", description] if description else [])
    gh.text("label", "create", name, "--repo", repo, *extra)
    return True


def verify_source(gh: Gh, source_repo: str, base_branch: str) -> dict[str, Any]:
    info = gh.json("repo", "view", source_repo, "--json", "nameWithOwner,defaultBranchRef")
    gh.text("api", f"repos/{source_repo}/branches/{quote(base_branch, safe='')}")
    return {"source_repository": info["nameWithOwner"], "default_branch": (info.get("defaultBranchRef") or {}).get("name")}


def origin_matches(gh: Gh, root: Path, source_repo: str) -> bool:
    origin = gh.git("-C", str(root), "remote", "get-url", "origin").strip()
    return bool(re.search(rf"[:/]{re.escape(source_repo)}(\.git)?/?$", origin, re.IGNORECASE))


def is_ignored(gh: Gh, root: Path, path: Path) -> bool:
    try:
        gh.git("-C", str(root), "check-ignore", "-q", str(path))
    except GhError:
        return False
    return True


def resolve_checkout(gh: Gh, harness_root: Path, source_repo: str, spec_number: int) -> dict[str, str]:
    name = source_repo.split("/")[1]
    workspace = harness_root / "workspace"
    split_root = workspace / name
    if (split_root / ".git").is_dir():
        source_root, base_dir = split_root, workspace
    elif (harness_root / ".git").is_dir() and origin_matches(gh, harness_root, source_repo):
        # Single-repo layout: the harness checkout is the source repository's primary checkout.
        source_root = harness_root
        base_dir = workspace if is_ignored(gh, harness_root, workspace / f"{name}.runs") else harness_root.parent
    elif not workspace.is_dir():
        raise UsageError(f"{workspace} not found and {harness_root} is not a primary checkout of {source_repo}")
    else:
        raise UsageError(f"{split_root} is not a primary checkout")
    if not origin_matches(gh, source_root, source_repo):
        raise UsageError(f"origin of {source_root} does not match {source_repo}")
    runs = base_dir / f"{name}.runs"
    candidate, suffix = runs / str(spec_number), 1
    while candidate.exists():
        suffix += 1
        candidate = runs / f"{spec_number}-{suffix}"
    return {
        "harness_root": str(harness_root),
        "source_root": str(source_root),
        "run_dir": str(candidate),
        "evidence_root": str(base_dir / f"{name}.evidence"),
    }


def cmd_preflight(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    gh.text("--version")
    gh.text("auth", "status")
    harness_root = Path(args.harness_root or gh.git("rev-parse", "--show-toplevel").strip())
    default_repo = None
    if "/" not in args.spec:
        default_repo = gh.text("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner").strip()
    ref = parse_ref(args.spec, default_repo)
    issue = read_issue(gh, ref)
    labels = labels_of(issue)
    source = args.source_repository or single_label(labels, TARGET_PREFIX)
    base = args.base_branch or single_label(labels, BASE_PREFIX)
    verified = verify_source(gh, source, base)
    initiative_id = initiative_id_of(issue["title"])
    return {
        "spec": str(ref),
        "tracker_repository": ref.repo,
        "title": issue["title"],
        "state": issue["state"],
        "base_branch": base,
        "initiative_id": initiative_id,
        "integration_branch": f"feat/{initiative_id}",
        **verified,
        **resolve_checkout(gh, harness_root, verified["source_repository"], ref.number),
    }


def cmd_spec_create(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    initiative = validate_initiative_id(args.initiative_id)
    source = verify_source(gh, args.source_repository, args.base_branch)["source_repository"]
    tracker = args.tracker_repository or gh.text("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner").strip()
    target_label, base_label = f"{TARGET_PREFIX}{source}", f"{BASE_PREFIX}{args.base_branch}"
    for label in ("spec", target_label, base_label):
        ensure_label(gh, tracker, label)
    body = Path(args.body_file).read_text(encoding="utf-8").rstrip() + f"\n\nSource: {args.source_note}\n"
    title = f"{initiative}: {' '.join(args.summary.split())}"
    with tempfile.TemporaryDirectory() as tmp:
        body_file = Path(tmp) / "spec.md"
        body_file.write_text(body, encoding="utf-8")
        url = gh.text("issue", "create", "--repo", tracker, "--title", title, "--body-file", str(body_file),
                      "--label", ",".join(["spec", target_label, base_label])).strip().splitlines()[-1]
    ref = parse_ref(url)
    issue = read_issue(gh, ref)
    labels = labels_of(issue)
    problems = []
    if issue["title"] != title:
        problems.append("title mismatch")
    if "spec" not in labels or single_label(labels, TARGET_PREFIX) != source or single_label(labels, BASE_PREFIX) != args.base_branch:
        problems.append("labels mismatch")
    return {"spec": str(ref), "url": url, "problems": problems}


def blocker_record(blocker: dict[str, Any]) -> dict[str, Any]:
    return {"ref": str(ref_of_api(blocker)), "state": blocker["state"], "state_reason": blocker.get("state_reason")}


def cmd_graph_read(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    out = Path(args.out)
    spec_ref = parse_ref(args.spec)
    spec = read_issue(gh, spec_ref)
    spec_labels = labels_of(spec)
    raw_artifacts, artifacts_note = read_artifacts(gh, spec_ref)
    artifacts = save_artifacts(raw_artifacts, out / "artifacts")
    write_json(out / "spec.json", {
        "ref": str(spec_ref), "issue": spec, "comments": read_comments(gh, spec_ref),
        "artifacts": artifacts, "artifacts_note": artifacts_note,
    })
    routing = {prefix: next((label for label in spec_labels if label.startswith(prefix)), None) for prefix in (TARGET_PREFIX, BASE_PREFIX)}
    tickets: list[dict[str, Any]] = []
    problems: list[str] = []
    for child in children_of(gh, spec_ref):
        ref = ref_of_api(child)
        blockers = [blocker_record(item) for item in gh.pages(f"repos/{ref.repo}/issues/{ref.number}/dependencies/blocked_by")]
        labels = labels_of(child)
        path = out / "tickets" / f"{ref.file_stem}.json"
        write_json(path, {"ref": str(ref), "issue": child, "comments": read_comments(gh, ref), "blocked_by": blockers})
        for prefix, expected in routing.items():
            own = next((label for label in labels if label.startswith(prefix)), None)
            if own and expected and own != expected:
                problems.append(f"{ref}: routing label {own} conflicts with spec {expected}")
        tickets.append({
            "ref": str(ref), "title": child["title"], "state": child["state"], "state_reason": child.get("state_reason"),
            "labels": labels, "hitl": "hitl" in labels, "blocked_by": blockers, "file": str(path),
        })
    graph: dict[str, Any] = {
        "spec": {
            "ref": str(spec_ref), "title": spec["title"], "state": spec["state"], "labels": spec_labels, "file": str(out / "spec.json"),
            "artifacts": artifacts, "artifacts_dir": str(out / "artifacts"), "artifacts_note": artifacts_note,
        },
        "tickets": tickets,
        "problems": problems,
    }
    graph["frontier"] = analyse(graph, set())
    write_json(out / "graph.json", graph)
    return graph


def find_cycles(edges: dict[str, list[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> None:
        state[node] = 1
        stack.append(node)
        for blocker in edges.get(node, []):
            if blocker not in edges:
                continue
            if state.get(blocker) == 1:
                cycles.append(stack[stack.index(blocker):] + [blocker])
            elif blocker not in state:
                visit(blocker)
        stack.pop()
        state[node] = 2

    for node in edges:
        if node not in state:
            visit(node)
    return cycles


def analyse(graph: dict[str, Any], done: set[str]) -> dict[str, Any]:
    tickets = {ticket["ref"]: ticket for ticket in graph["tickets"]}
    complete = {
        ref for ref, ticket in tickets.items()
        if ref in done or (ticket["state"] == "closed" and ticket["state_reason"] == "completed")
    }
    edges = {ref: [blocker["ref"] for blocker in ticket["blocked_by"]] for ref, ticket in tickets.items()}

    def defer_reason(ref: str, seen: frozenset[str] = frozenset()) -> str | None:
        if ref in complete or ref in seen or ref not in tickets:
            return None
        if tickets[ref]["hitl"]:
            return "hitl"
        for blocker in edges[ref]:
            if defer_reason(blocker, seen | {ref}):
                return f"blocked by {blocker}"
        return None

    deferred = {ref: reason for ref in tickets if (reason := defer_reason(ref))}
    ready: list[str] = []
    blocked: list[dict[str, Any]] = []
    needs_resolution: list[dict[str, Any]] = []
    for ref, ticket in tickets.items():
        if ref in complete or ref in deferred:
            continue
        unmet = []
        for blocker in ticket["blocked_by"]:
            if blocker["ref"] in complete or blocker["ref"] in done:
                continue
            if blocker["ref"] not in tickets and blocker["state"] == "closed" and blocker["state_reason"] == "completed":
                continue
            unmet.append(blocker["ref"])
            if blocker["state"] == "closed" and blocker["state_reason"] != "completed":
                needs_resolution.append({"ref": ref, "blocker": blocker["ref"], "state_reason": blocker["state_reason"]})
        if unmet:
            blocked.append({"ref": ref, "unmet": unmet})
        else:
            ready.append(ref)
    return {
        "done": sorted(complete),
        "ready": ready,
        "blocked": blocked,
        "deferred": [{"ref": ref, "reason": reason} for ref, reason in deferred.items()],
        "needs_resolution": needs_resolution,
        "cycles": find_cycles(edges),
    }


def cmd_graph_frontier(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    graph = json.loads(Path(args.graph).read_text(encoding="utf-8"))
    return analyse(graph, {str(parse_ref(ref)) for ref in args.done})


def children_of(gh: Gh, spec: Ref) -> list[dict[str, Any]]:
    return gh.pages(f"repos/{spec.repo}/issues/{spec.number}/sub_issues")


def cmd_ticket_create(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    spec = parse_ref(args.spec)
    label = f"{TARGET_PREFIX}{single_label(labels_of(read_issue(gh, spec)), TARGET_PREFIX)}"
    ensure_label(gh, spec.repo, label, color="0e8a16", description="Source repository for spec tickets")
    linked = [child for child in children_of(gh, spec) if child["title"] == args.title]
    unlinked = [] if linked else [
        item for item in gh.json("issue", "list", "--repo", spec.repo, "--label", label, "--state", "all",
                                 "--search", f"{args.title} in:title", "--json", "number,title")
        if item["title"] == args.title
    ]
    matches = linked or unlinked
    if len(matches) > 1:
        raise UsageError(f"{len(matches)} issues already titled {args.title!r}; resolve manually")
    created = not matches
    if created:
        url = gh.text("issue", "create", "--repo", spec.repo, "--title", args.title, "--body-file", args.body_file,
                      "--label", label).strip().splitlines()[-1]
        ref = parse_ref(url)
    else:
        ref = Ref(spec.repo, matches[0]["number"])
    if not linked:
        child_id = gh.json("api", f"repos/{ref.repo}/issues/{ref.number}", "--jq", ".id")
        gh.text("api", f"repos/{spec.repo}/issues/{spec.number}/sub_issues", "--method", "POST", "-F", f"sub_issue_id={child_id}")
        if not any(ref_of_api(child) == ref for child in children_of(gh, spec)):
            raise GhError(f"{ref} not linked as sub-issue of {spec} after create")
    return {"ref": str(ref), "created": created, "linked": True}


def cmd_issue_block(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    issue = parse_ref(args.ref)
    wanted = [parse_ref(text) for text in args.by]
    endpoint = f"repos/{issue.repo}/issues/{issue.number}/dependencies/blocked_by"
    existing = {ref_of_api(item) for item in gh.pages(endpoint)}
    added = []
    for blocker in wanted:
        if blocker in existing:
            continue
        blocker_id = gh.json("api", f"repos/{blocker.repo}/issues/{blocker.number}", "--jq", ".id")
        gh.text("api", endpoint, "--method", "POST", "-F", f"issue_id={blocker_id}")
        added.append(str(blocker))
    final = {ref_of_api(item) for item in gh.pages(endpoint)}
    missing = [str(blocker) for blocker in wanted if blocker not in final]
    if missing:
        raise GhError(f"blocker edges missing after link: {missing}")
    return {"ref": str(issue), "added": added, "blocked_by": sorted(str(ref) for ref in final)}


def cmd_issue_edit_body(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref)
    gh.text("issue", "edit", str(ref.number), "--repo", ref.repo, "--body-file", args.body_file)
    expected = Path(args.body_file).read_text(encoding="utf-8").strip()
    problems = [] if (read_issue(gh, ref).get("body") or "").strip() == expected else ["body differs after edit"]
    return {"ref": str(ref), "problems": problems}


def cmd_issue_comment(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref)
    url = gh.text("issue", "comment", str(ref.number), "--repo", ref.repo, "--body-file", args.body_file).strip().splitlines()[-1]
    match = re.search(r"#issuecomment-(\d+)", url)
    if not match:
        raise GhError(f"no comment id in gh output: {url}")
    body = gh.json("api", f"repos/{ref.repo}/issues/comments/{match.group(1)}").get("body", "")
    expected = Path(args.body_file).read_text(encoding="utf-8").strip()
    return {"ref": str(ref), "url": url, "id": int(match.group(1)), "problems": [] if body.strip() == expected else ["comment body differs"]}


def cmd_issue_close(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref)
    if "hitl" in labels_of(read_issue(gh, ref)):
        raise UsageError(f"{ref} is hitl; never close it from the run")
    if args.comment:
        comment = args.comment
    elif args.commit and args.branch:
        comment = f"Implemented in {args.commit} on {args.branch}" + (f" ({args.pr})." if args.pr else ".")
    else:
        raise UsageError("provide --comment, or --commit and --branch")
    gh.text("issue", "close", str(ref.number), "--repo", ref.repo, "--reason", "completed", "--comment", comment)
    issue = read_issue(gh, ref)
    if issue["state"] != "closed" or issue.get("state_reason") != "completed":
        raise GhError(f"{ref} not closed as completed: {issue['state']}/{issue.get('state_reason')}")
    return {"ref": str(ref), "state": issue["state"], "state_reason": issue["state_reason"]}


def managed_block(body: str) -> str:
    match = re.search(rf"{re.escape(BLOCK_BEGIN)}(.*?){re.escape(BLOCK_END)}", body, flags=re.DOTALL)
    return match.group(1) if match else ""


def user_text(body: str, initiative_id: str) -> str:
    body = re.sub(rf"{re.escape(BLOCK_BEGIN)}.*?{re.escape(BLOCK_END)}", "", body, flags=re.DOTALL)
    kept = [
        line for line in body.splitlines()
        if line.strip() != initiative_id
        and not re.match(r"\s*\[#[^\]]+\]", line)
        and not re.match(r"\s*Initiative( source)?:", line)
    ]
    return "\n".join(kept).strip()


def block_refs(body: str, keyword: str) -> list[str]:
    return re.findall(rf"^{keyword} ({REPO_PATTERN}#\d+)\s*$", managed_block(body), flags=re.MULTILINE)


def build_body(initiative_id: str, rationale: str, closes: list[str], refs: list[str], evidence: str, extra: str) -> str:
    bullets = [line.rstrip() for line in rationale.splitlines() if line.strip()]
    if not bullets or any(not line.startswith("- ") for line in bullets):
        raise UsageError("rationale must be non-empty `- ` bullets that each answer Why?; report missing rationale, never invent it")
    links = [f"Closes {ref}" for ref in closes] + [f"Refs {ref}" for ref in refs]
    parts = ["\n".join(bullets), "\n".join(links), f"## Evidence\n\n{evidence.strip()}" if evidence.strip() else ""]
    block = "\n\n".join(part for part in parts if part)
    return f"{initiative_id}\n\n{BLOCK_BEGIN}\n{block}\n{BLOCK_END}\n" + (f"\n{extra}\n" if extra else "")


def sorted_unique(items: list[str]) -> list[str]:
    return sorted(set(items), key=lambda ref: (ref.split("#")[0], int(ref.split("#")[1])))


def pr_checks(gh: Gh, repo: str, number: int) -> dict[str, Any]:
    code, out, err = gh.raw("pr", "checks", str(number), "--repo", repo, "--json", "name,bucket")
    rows = json.loads(out) if out.strip() else []
    if not rows and "no checks" not in err.lower():
        raise GhError(f"gh pr checks failed ({code}): {err.strip()}")
    buckets = {"pass": "passed", "fail": "failed", "cancel": "failed", "pending": "pending", "skipping": "skipped"}
    result: dict[str, Any] = {"status": "absent", "passed": [], "failed": [], "pending": [], "skipped": []}
    for row in rows:
        result[buckets.get(row["bucket"], "pending")].append(row["name"])
    if rows:
        result["status"] = "failed" if result["failed"] else "pending" if result["pending"] else "passed"
    return result


def read_pr(gh: Gh, repo: str, number: int, initiative_id: str | None, expect_closes: list[str]) -> dict[str, Any]:
    pr = gh.json("pr", "view", str(number), "--repo", repo,
                 "--json", "url,title,body,headRefOid,isDraft,baseRefName,headRefName,state")
    body = pr["body"] or ""
    first_line = next((line.strip() for line in body.splitlines() if line.strip()), "")
    closes = re.findall(rf"^Closes ({REPO_PATTERN}#\d+)\s*$", body, flags=re.MULTILINE)
    problems = []
    if initiative_id:
        if first_line != initiative_id:
            problems.append(f"first body line is {first_line!r}, expected {initiative_id!r}")
        if not pr["title"].startswith(f"{initiative_id}: "):
            problems.append("title lacks initiative prefix")
    if not pr["isDraft"]:
        problems.append("PR is not draft")
    missing = [str(parse_ref(ref)) for ref in expect_closes if str(parse_ref(ref)) not in closes]
    if missing:
        problems.append(f"missing Closes lines: {missing}")
    return {
        "number": number, "url": pr["url"], "title": pr["title"], "state": pr["state"], "is_draft": pr["isDraft"],
        "base": pr["baseRefName"], "head": pr["headRefName"], "head_sha": pr["headRefOid"],
        "first_body_id": first_line, "closes": closes, "checks": pr_checks(gh, repo, number), "problems": problems,
    }


def find_pr(gh: Gh, repo: str, head: str) -> dict[str, Any] | None:
    found = gh.json("pr", "list", "--repo", repo, "--head", head, "--state", "open",
                    "--json", "number,url,isDraft,baseRefName,headRefName,body")
    if len(found) > 1:
        raise UsageError(f"{len(found)} open PRs for head {head}; resolve manually")
    return found[0] if found else None


def cmd_pr_publish(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    initiative = validate_initiative_id(args.initiative_id)
    if not args.title.startswith(f"{initiative}: "):
        raise UsageError(f"title must start with '{initiative}: '")
    closes = [str(parse_ref(ref)) for ref in args.closes]
    for ref in map(parse_ref, closes):
        if "hitl" in labels_of(read_issue(gh, ref)):
            raise UsageError(f"{ref} is hitl; never add a closing reference to it")
    existing = find_pr(gh, args.source_repository, args.head)
    if existing and existing["baseRefName"] != args.base:
        raise UsageError(f"existing PR #{existing['number']} targets {existing['baseRefName']}, expected {args.base}")
    old_body = (existing["body"] or "") if existing else ""
    all_closes = sorted_unique(closes + block_refs(old_body, "Closes"))
    refs = sorted_unique([str(parse_ref(ref)) for ref in args.refs] + block_refs(old_body, "Refs"))
    refs = [ref for ref in refs if ref not in all_closes]
    evidence = Path(args.evidence_file).read_text(encoding="utf-8") if args.evidence_file else ""
    body = build_body(initiative, Path(args.rationale_file).read_text(encoding="utf-8"), all_closes, refs, evidence,
                      user_text(old_body, initiative))
    with tempfile.TemporaryDirectory() as tmp:
        body_file = Path(tmp) / "pr.md"
        body_file.write_text(body, encoding="utf-8")
        if existing:
            gh.text("pr", "edit", str(existing["number"]), "--repo", args.source_repository,
                    "--title", args.title, "--body-file", str(body_file))
            number = existing["number"]
        else:
            url = gh.text("pr", "create", "--repo", args.source_repository, "--base", args.base, "--head", args.head,
                          "--draft", "--title", args.title, "--body-file", str(body_file)).strip().splitlines()[-1]
            number = int(url.rstrip("/").rsplit("/", 1)[-1])
    result = read_pr(gh, args.source_repository, number, initiative, all_closes)
    result["created"] = not existing
    return result


def cmd_pr_read(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    number = args.number
    if number is None:
        pr = find_pr(gh, args.source_repository, args.head) if args.head else None
        if not pr:
            raise UsageError("no open PR found; pass --number or a --head with an open PR")
        number = pr["number"]
    return read_pr(gh, args.source_repository, number, args.initiative_id, args.expect_closes)


def split_diff(diff: str) -> list[tuple[str, str]]:
    """Split a unified `git diff` into (real path, diff text) per file; the path is the `b/` side."""
    chunks: list[tuple[str, list[str]]] = []
    for line in diff.splitlines(keepends=True):
        header = re.match(r"diff --git a/.+ b/(.+?)\r?\n?$", line)
        if header:
            chunks.append((header.group(1), []))
        if chunks:
            chunks[-1][1].append(line)
    return [(path, "".join(lines)) for path, lines in chunks]


def cmd_pr_diff_split(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    target = [args.pr] + (["--repo", args.source_repository] if args.source_repository else [])
    files = split_diff(gh.text("pr", "diff", *target))
    if not files:
        raise GhError(f"empty or unparsable diff for {args.pr}; never run the subagent without a diff")
    diff_dir = Path(tempfile.mkdtemp(prefix="pr-diff-"))
    manifest, used = [], set()
    for path, text in files:
        name = path.replace("/", "_")
        while name in used or name == "_manifest.tsv":
            name += "_"
        used.add(name)
        (diff_dir / name).write_text(text, encoding="utf-8")
        manifest.append(f"{path}\t{name}")
    (diff_dir / "_manifest.tsv").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    return {"diff_dir": str(diff_dir), "manifest": str(diff_dir / "_manifest.tsv"), "files": len(files)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="implement-spec GitHub operations")
    groups = parser.add_subparsers(dest="group", required=True)
    nested = {
        group: groups.add_parser(group).add_subparsers(dest="action", required=True)
        for group in ("spec", "graph", "ticket", "issue", "pr")
    }

    def command(group: str | None, name: str, handler: Callable[..., dict[str, Any]]) -> argparse.ArgumentParser:
        sub = (groups if group is None else nested[group]).add_parser(name)
        sub.set_defaults(handler=handler)
        return sub

    p = command(None, "preflight", cmd_preflight)
    p.add_argument("--spec", required=True)
    p.add_argument("--harness-root")
    p.add_argument("--source-repository")
    p.add_argument("--base-branch")

    p = command("spec", "create", cmd_spec_create)
    for flag in ("source-repository", "base-branch", "initiative-id", "summary", "body-file", "source-note"):
        p.add_argument(f"--{flag}", required=True)
    p.add_argument("--tracker-repository")

    p = command("graph", "read", cmd_graph_read)
    p.add_argument("--spec", required=True)
    p.add_argument("--out", required=True)

    p = command("graph", "frontier", cmd_graph_frontier)
    p.add_argument("--graph", required=True)
    p.add_argument("--done", action="extend", nargs="+", default=[])

    p = command("ticket", "create", cmd_ticket_create)
    for flag in ("spec", "title", "body-file"):
        p.add_argument(f"--{flag}", required=True)

    p = command("issue", "block", cmd_issue_block)
    p.add_argument("ref")
    p.add_argument("--by", action="extend", nargs="+", required=True)

    for name, handler in (("edit-body", cmd_issue_edit_body), ("comment", cmd_issue_comment)):
        p = command("issue", name, handler)
        p.add_argument("ref")
        p.add_argument("--body-file", required=True)

    p = command("issue", "close", cmd_issue_close)
    p.add_argument("ref")
    for flag in ("commit", "branch", "pr", "comment"):
        p.add_argument(f"--{flag}")

    p = command("pr", "publish", cmd_pr_publish)
    for flag in ("source-repository", "base", "head", "title", "initiative-id", "rationale-file"):
        p.add_argument(f"--{flag}", required=True)
    p.add_argument("--closes", action="extend", nargs="+", default=[])
    p.add_argument("--refs", action="extend", nargs="+", default=[])
    p.add_argument("--evidence-file")

    p = command("pr", "diff-split", cmd_pr_diff_split)
    p.add_argument("--pr", required=True)
    p.add_argument("--source-repository")

    p = command("pr", "read", cmd_pr_read)
    p.add_argument("--source-repository", required=True)
    p.add_argument("--number", type=int)
    p.add_argument("--head")
    p.add_argument("--initiative-id")
    p.add_argument("--expect-closes", action="extend", nargs="+", default=[])
    return parser


def main(argv: list[str] | None = None, *, gh: Gh | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = args.handler(gh or Gh(), args)
    except (UsageError, GhError) as exception:
        print(f"error: {exception}", file=sys.stderr)
        return exception.exit_code
    except (OSError, json.JSONDecodeError) as exception:
        print(f"error: {exception}", file=sys.stderr)
        return UsageError.exit_code
    print(json.dumps(result, indent=2))
    return 3 if result.get("problems") else 0


if __name__ == "__main__":
    sys.exit(main())
