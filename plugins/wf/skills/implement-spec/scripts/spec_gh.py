#!/usr/bin/env python3
"""GitHub operations for the implement-spec skill: one command per intent, JSON on stdout.

Self-contained: stdlib only, shells out to `gh` and `git`. Errors go to stderr.
Exit codes: 0 ok, 1 GitHub/tool failure, 2 invalid input or unresolved routing,
3 completed but read-back verification reported `problems`.

    preflight   (--spec REF | --source-repository R --base-branch B --initiative-id I)
                [--harness-root P] [--mode MODE] [--max-parallel N] [--integration-branch H] [--pin-base]
    run checkpoint --run-dir DIR --input FILE
    spec create --source-repository R --base-branch B --initiative-id I --summary S --body-file F --source-note N
    graph read  --spec REF --out RUN_DIR      (also saves spec issue artifacts under RUN_DIR/artifacts, indexed by name in index.json)
    graph frontier --graph FILE [--planner FILE --out EFFECTIVE_FILE] [--done REF ...]
    ticket create --spec REF --title T --body-file F
    issue block REF --by REF [--by REF ...]
    issue edit-body REF --body-file F
    issue comment REF --body-file F [--run-id ID]
    issue close REF (--run-id ID --evidence-comment N | --commit SHA --branch B [--pr URL] | --comment TEXT)
    pr publish  --source-repository R --base B --head H --title T --initiative-id I
                --rationale-file F --changes-file F --evidence-file F [--refs REF ...]
    pr read     --source-repository R (--number N | --head H) [--initiative-id I] [--expect-refs REF ...]
    pr diff-split --pr URL_OR_NUMBER [--source-repository R]

REF is `OWNER/REPO#NUMBER` or an issue URL.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
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
RUN_ID_PATTERN = r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*"
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
    def key(self) -> str:
        digest = hashlib.sha256(str(self).lower().encode("ascii")).hexdigest()[:24]
        return f"t{self.number}-{digest}"


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


def verify_source(gh: Gh, source_repo: str, base_branch: str, *, pin_base: bool = False) -> dict[str, Any]:
    info = gh.json("repo", "view", source_repo, "--json", "nameWithOwner,defaultBranchRef")
    branch = gh.json("api", f"repos/{source_repo}/branches/{quote(base_branch, safe='')}")
    result = {"source_repository": info["nameWithOwner"], "default_branch": (info.get("defaultBranchRef") or {}).get("name")}
    if pin_base:
        sha = (branch.get("commit") or {}).get("sha")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise GhError(f"no valid base commit for {source_repo}:{base_branch}")
        result["base_commit"] = sha
    return result


def origin_matches(gh: Gh, root: Path, source_repo: str) -> bool:
    origin = gh.git("-C", str(root), "remote", "get-url", "origin").strip()
    return bool(re.search(rf"[:/]{re.escape(source_repo)}(\.git)?/?$", origin, re.IGNORECASE))


def is_ignored(gh: Gh, root: Path, path: Path) -> bool:
    try:
        gh.git("-C", str(root), "check-ignore", "-q", str(path))
    except GhError:
        return False
    return True


def resolve_checkout(gh: Gh, harness_root: Path, source_repo: str, spec_number: int | None) -> dict[str, str | None]:
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
    candidate = None
    if spec_number is not None:
        candidate, suffix = runs / str(spec_number), 1
        while candidate.exists():
            suffix += 1
            candidate = runs / f"{spec_number}-{suffix}"
    return {
        "harness_root": str(harness_root),
        "source_root": str(source_root),
        "run_dir": str(candidate) if candidate is not None else None,
        "evidence_root": str(base_dir / f"{name}.evidence"),
    }


def cmd_preflight(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    if args.max_parallel is not None and (args.mode != "parallel" or args.max_parallel < 1):
        raise UsageError("--max-parallel requires parallel mode and a positive integer")
    if args.spec:
        if args.initiative_id or bool(args.source_repository) != bool(args.base_branch):
            raise UsageError("--spec accepts only paired --source-repository and --base-branch overrides")
    elif not (args.source_repository and args.base_branch and args.initiative_id):
        raise UsageError("provide --spec or --source-repository, --base-branch and --initiative-id")

    branch = args.integration_branch
    if branch is not None and not re.fullmatch(r"(?:feat|fix)/[a-z0-9]+(?:-[a-z0-9]+)*", branch):
        raise UsageError("integration branch must be a lowercase feat/<slug> or fix/<slug>")
    if args.pin_base and branch is None:
        raise UsageError("--pin-base requires --integration-branch")

    gh.text("--version")
    gh.text("auth", "status")
    harness_root = Path(args.harness_root or gh.git("rev-parse", "--show-toplevel").strip()).resolve()
    ref, issue = None, {}
    if args.spec:
        default_repo = None
        if "/" not in args.spec:
            default_repo = gh.text("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner").strip()
        ref = parse_ref(args.spec, default_repo)
        issue = read_issue(gh, ref)
        labels = labels_of(issue)
        source = args.source_repository or single_label(labels, TARGET_PREFIX)
        base = args.base_branch or single_label(labels, BASE_PREFIX)
        initiative_id = initiative_id_of(issue["title"])
    else:
        source, base = args.source_repository, args.base_branch
        initiative_id = validate_initiative_id(args.initiative_id)

    verified = verify_source(gh, source, base, pin_base=args.pin_base)
    checkout = resolve_checkout(gh, harness_root, verified["source_repository"], ref.number if ref else None)
    if args.pin_base:
        root, sha = checkout["source_root"], verified["base_commit"]
        gh.git("-C", root, "check-ref-format", "--branch", branch)
        gh.git("-C", root, "fetch", "--no-tags", "--no-write-fetch-head", "origin", sha)
        gh.git("-C", root, "cat-file", "-e", f"{sha}^{{commit}}")
    return {
        "spec": str(ref) if ref else None,
        "tracker_repository": ref.repo if ref else None,
        "title": issue.get("title"),
        "state": issue.get("state"),
        "base_branch": base,
        "initiative_id": initiative_id,
        "integration_branch": branch,
        **verified,
        **checkout,
    }


def cmd_run_checkpoint(_gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    run_dir = Path(args.run_dir).resolve()
    path = run_dir / "publication-checkpoint.json"
    checkpoint = json.loads(Path(args.input).read_text(encoding="utf-8"))
    identity = checkpoint.get("run") if isinstance(checkpoint, dict) else None
    fields = ("id", "specRef", "sourceRepository", "baseBranch", "baseCommit", "integrationBranch", "worktreePath")
    if not isinstance(identity, dict) or any(not isinstance(identity.get(field), str) or not identity[field] for field in fields):
        raise UsageError("checkpoint is missing run identity")
    mode, cap = identity.get("mode"), identity.get("maxParallel")
    if mode not in ("sequential", "parallel") or (
        cap is not None and (mode != "parallel" or type(cap) is not int or cap < 1)
    ):
        raise UsageError("invalid checkpoint execution mode or worker cap")
    if not re.fullmatch(RUN_ID_PATTERN, identity["id"]) or not re.fullmatch(r"[0-9a-f]{40}", identity["baseCommit"]):
        raise UsageError("invalid checkpoint run id or base SHA")
    parse_ref(identity["specRef"])
    tickets = checkpoint.get("tickets")
    if not isinstance(tickets, dict):
        raise UsageError("checkpoint tickets must be keyed by ticket key")
    for key, ticket in tickets.items():
        if not isinstance(ticket, dict) or not isinstance(ticket.get("ref"), str) or parse_ref(ticket["ref"]).key != key:
            raise UsageError(f"checkpoint key does not match ticket identity: {key}")
    branches = [ticket["branch"] for ticket in tickets.values() if "branch" in ticket]
    if any(not isinstance(branch, str) or not branch for branch in branches):
        raise UsageError("invalid recorded worker branch")
    if len(set(branches)) != len(branches) or identity["integrationBranch"] in branches:
        raise UsageError("checkpoint worker branches must be distinct")

    if path.exists():
        previous = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(previous, dict) or not isinstance(previous.get("tickets"), dict):
            raise UsageError(f"invalid existing checkpoint: {path}")
        if previous.get("run") != identity or previous["tickets"].keys() - tickets.keys():
            raise UsageError("checkpoint must preserve run identity and recorded tickets")
        for key, ticket in previous["tickets"].items():
            if not isinstance(ticket, dict) or ticket.get("ref") != tickets[key]["ref"]:
                raise UsageError(f"checkpoint must preserve the recorded ticket identity: {key}")
            for field in ("branch", "worktreePath"):
                if field in ticket and ticket[field] != tickets[key].get(field):
                    raise UsageError(f"checkpoint must preserve recorded worker {field}: {key}")
    run_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=run_dir) as temporary:
        draft = Path(temporary) / path.name
        write_json(draft, checkpoint)
        draft.replace(path)
    return {"file": str(path)}


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
    return {"ref": str(ref_of_api(blocker)), "state": blocker["state"], "state_reason": blocker.get("state_reason"),
            "hitl": "hitl" in labels_of(blocker)}


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
    keys: set[str] = set()
    for child in children_of(gh, spec_ref):
        ref = ref_of_api(child)
        key = ref.key
        if key in keys:
            raise UsageError(f"duplicate or colliding ticket key for {ref}: {key}")
        keys.add(key)
        blockers = [blocker_record(item) for item in gh.pages(f"repos/{ref.repo}/issues/{ref.number}/dependencies/blocked_by")]
        labels = labels_of(child)
        path = out / "tickets" / f"{key}.json"
        if path.exists():
            stored_ref = json.loads(path.read_text(encoding="utf-8")).get("ref")
            if not isinstance(stored_ref, str) or stored_ref.lower() != str(ref).lower():
                raise UsageError(f"ticket snapshot {path} belongs to {stored_ref}, not {ref}")
        write_json(path, {"ref": str(ref), "issue": child, "comments": read_comments(gh, ref), "blocked_by": blockers})
        for prefix, expected in routing.items():
            own = next((label for label in labels if label.startswith(prefix)), None)
            if own and expected and own != expected:
                problems.append(f"{ref}: routing label {own} conflicts with spec {expected}")
        tickets.append({
            "ref": str(ref), "title": child["title"], "state": child["state"], "state_reason": child.get("state_reason"),
            "labels": labels, "hitl": "hitl" in labels, "blocked_by": blockers, "key": key, "file": str(path),
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

    def can_verify(ticket: dict[str, Any]) -> bool:
        if ticket["state"] == "closed":
            return ticket["state_reason"] == "completed"
        return not ticket.get("hitl", False)

    complete = {ref for ref, ticket in tickets.items() if ref in done and can_verify(ticket)}
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
        if ticket["state"] == "closed":
            reason = ticket["state_reason"]
            needs_resolution.append({"ref": ref, "state_reason": reason,
                                     "reason": "unverified-closed" if reason == "completed" else "closed-without-completion"})
            continue
        unmet = []
        for blocker in ticket["blocked_by"]:
            blocker_ref = blocker["ref"]
            external = blocker_ref not in tickets
            current = tickets.get(blocker_ref, blocker)
            if blocker_ref in complete or (external and blocker_ref in done and can_verify(current)):
                continue
            unmet.append(blocker_ref)
            reason = current["state_reason"]
            resolution = {"ref": ref, "blocker": blocker_ref, "state_reason": reason}
            if current["state"] == "closed":
                if reason == "completed":
                    resolution["reason"] = "unverified-closed"
                needs_resolution.append(resolution)
            elif external:
                needs_resolution.append({**resolution, "reason": "open-external"})
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


def effective_graph(graph: dict[str, Any], planner: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(planner, dict) or planner.get("status") != "completed":
        raise UsageError("planner result must have status completed")
    result = planner.get("result")
    if not isinstance(result, dict) or result.get("specRef") != graph["spec"]["ref"]:
        raise UsageError("planner specRef must match the native graph")
    planned = result.get("tickets")
    if not isinstance(planned, list):
        raise UsageError("planner tickets must be a list")
    effective = copy.deepcopy(graph)
    tickets = {ticket["ref"]: ticket for ticket in effective["tickets"]}
    seen: set[str] = set()
    for ticket in planned:
        if not isinstance(ticket, dict) or not isinstance(ticket.get("ref"), str):
            raise UsageError("planner ticket needs a qualified ref")
        ref = ticket["ref"]
        if ref not in tickets or ref in seen:
            raise UsageError(f"unknown or duplicate planner ticket: {ref}")
        seen.add(ref)
        blockers = ticket.get("blockers")
        if not isinstance(blockers, list) or any(not isinstance(blocker, str) for blocker in blockers):
            raise UsageError(f"{ref}: planner blockers must be a list of qualified refs")
        if len(set(blockers)) != len(blockers):
            raise UsageError(f"{ref}: duplicate planner blockers")
        existing = {blocker["ref"] for blocker in tickets[ref]["blocked_by"]}
        for blocker in blockers:
            if blocker == ref:
                raise UsageError(f"{ref}: self dependency")
            if blocker in existing:
                continue
            if blocker not in tickets:
                raise UsageError(f"{ref}: unknown planner blocker {blocker}; fetch and resolve external dependencies first")
            producer = tickets[blocker]
            tickets[ref]["blocked_by"].append({
                "ref": blocker, "state": producer["state"], "state_reason": producer.get("state_reason"),
                "source": "planner",
            })
    if seen != tickets.keys():
        raise UsageError(f"planner recommendations missing tickets: {sorted(tickets.keys() - seen)}")
    cycles = find_cycles({ref: [blocker["ref"] for blocker in ticket["blocked_by"]] for ref, ticket in tickets.items()})
    if cycles:
        raise UsageError(f"effective graph contains dependency cycles: {cycles}")
    return effective


def cmd_graph_frontier(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    graph_path = Path(args.graph)
    inputs = [graph_path] + ([Path(args.planner)] if args.planner else [])
    if args.out and Path(args.out).resolve() in {path.resolve() for path in inputs}:
        raise UsageError("effective output must not overwrite the native graph or planner result")
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    if args.planner:
        graph = effective_graph(graph, json.loads(Path(args.planner).read_text(encoding="utf-8")))
    graph["frontier"] = analyse(graph, {str(parse_ref(ref)) for ref in args.done})
    if args.out:
        write_json(Path(args.out), graph)
    return graph["frontier"]


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


def marked_evidence(gh: Gh, ref: Ref, run_id: str) -> tuple[str, dict[str, Any] | None]:
    if not re.fullmatch(RUN_ID_PATTERN, run_id):
        raise UsageError("invalid run id for ticket evidence")
    marker = f"<!-- implement-spec:evidence {run_id} {ref.key} -->"
    matches = [comment for comment in read_comments(gh, ref) if marker in comment.get("body", "").splitlines()]
    if len(matches) > 1:
        raise UsageError(f"{ref}: multiple evidence comments for run {run_id}")
    return marker, matches[0] if matches else None


def cmd_issue_comment(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref)
    source = Path(args.body_file)
    expected = source.read_text(encoding="utf-8").strip()
    with tempfile.TemporaryDirectory() as temporary:
        if args.run_id:
            issue = read_issue(gh, ref)
            if "hitl" in labels_of(issue):
                raise UsageError(f"{ref} is hitl; never post evidence from the run")
            marker, existing = marked_evidence(gh, ref, args.run_id)
            expected = f"{expected}\n\n{marker}"
            if existing:
                if existing["body"].strip() != expected:
                    raise UsageError(f"{ref}: marked evidence differs from the recorded body")
                comment_id = existing["id"]
                url = existing.get("html_url") or f"https://github.com/{ref.repo}/issues/{ref.number}#issuecomment-{comment_id}"
                return {"ref": str(ref), "url": url, "id": comment_id, "problems": []}
            if issue["state"] != "open":
                raise UsageError(f"{ref} is closed; reconcile its evidence before posting")
            source = Path(temporary) / "evidence.md"
            source.write_text(expected, encoding="utf-8")
        output = gh.text("issue", "comment", str(ref.number), "--repo", ref.repo, "--body-file", str(source))
    url = output.strip().split("\n")[-1]
    match = re.search(r"#issuecomment-(\d+)", url)
    if not match:
        raise GhError(f"no comment id in gh output: {url}")
    body = gh.json("api", f"repos/{ref.repo}/issues/comments/{match.group(1)}").get("body", "")
    return {"ref": str(ref), "url": url, "id": int(match.group(1)), "problems": [] if body.strip() == expected else ["comment body differs"]}


def cmd_issue_close(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref)
    issue = read_issue(gh, ref)
    if "hitl" in labels_of(issue):
        raise UsageError(f"{ref} is hitl; never close it from the run")
    close_args = ["issue", "close", str(ref.number), "--repo", ref.repo, "--reason", "completed"]
    if args.run_id or args.evidence_comment is not None:
        if not args.run_id or not args.evidence_comment or any((args.commit, args.branch, args.pr, args.comment)):
            raise UsageError("workflow closure requires only --run-id and --evidence-comment")
        _, evidence = marked_evidence(gh, ref, args.run_id)
        if not evidence or evidence["id"] != args.evidence_comment:
            raise UsageError(f"{ref}: expected marked evidence comment {args.evidence_comment}")
        if issue["state"] == "closed":
            if issue.get("state_reason") != "completed":
                raise UsageError(f"{ref}: closed without completion; preserve tracker state")
            return {"ref": str(ref), "state": "closed", "state_reason": "completed"}
    elif args.comment:
        close_args += ["--comment", args.comment]
    elif args.commit and args.branch:
        comment = f"Implemented in {args.commit} on {args.branch}" + (f" ({args.pr})." if args.pr else ".")
        close_args += ["--comment", comment]
    else:
        raise UsageError("provide --comment, --commit and --branch, or workflow evidence")
    gh.text(*close_args)
    issue = read_issue(gh, ref)
    if issue["state"] != "closed" or issue.get("state_reason") != "completed":
        raise GhError(f"{ref} not closed as completed: {issue['state']}/{issue.get('state_reason')}")
    return {"ref": str(ref), "state": issue["state"], "state_reason": issue["state_reason"]}


def managed_block(body: str) -> str:
    match = re.search(rf"{re.escape(BLOCK_BEGIN)}(.*?){re.escape(BLOCK_END)}", body, flags=re.DOTALL)
    return match.group(1) if match else ""


def user_text(body: str, initiative_id: str) -> str:
    lines = body.splitlines(keepends=True)
    while lines:
        line = lines[0].strip()
        if line not in ("", initiative_id, f"[{initiative_id}]") and not (
            re.fullmatch(r"\[#\d+\]", line) or re.match(r"Initiative(?: source)?:", line)
        ):
            break
        lines.pop(0)
    managed_pattern = rf"{re.escape(BLOCK_BEGIN)}.*?{re.escape(BLOCK_END)}"
    return re.sub(managed_pattern, "", "".join(lines), count=1, flags=re.DOTALL).strip("\r\n")


def block_refs(body: str) -> list[str]:
    return re.findall(rf"^(?:Refs|Closes) ({REPO_PATTERN}#\d+)[ \t]*$", managed_block(body), flags=re.MULTILINE)


def pr_initiative(value: str) -> str:
    if re.fullmatch(rf"(?:{REPO_PATTERN})?#\d+", value):
        return value
    if re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*", value):
        return value
    raise UsageError(f"invalid PR initiative ID: {value!r}")


def valid_pr_title(title: str, initiative: str) -> bool:
    prefix = f"[{initiative}] "
    return title.startswith(prefix) and bool(
        re.fullmatch(r"[a-z]+(?:\([a-z0-9]+(?:[._/-][a-z0-9]+)*\))?!?: \S[^\r\n]*", title[len(prefix):])
    )


def build_body(initiative: str, rationale: str, changes: str, evidence: str, refs: list[str], extra: str) -> str:
    bullets = [line.rstrip() for line in rationale.splitlines() if line.strip()]
    if not bullets or any(not line.startswith("- ") for line in bullets):
        raise UsageError("rationale must be non-empty `- ` bullets that each answer Why?; report missing rationale, never invent it")
    if not changes.strip() or not evidence.strip():
        raise UsageError("What changed and Verification must be non-empty")
    parts = [
        "## Why\n\n" + "\n".join(bullets),
        f"## What changed\n\n{changes.strip()}",
        f"## Verification\n\n{evidence.strip()}",
    ]
    if refs:
        parts.append("## References\n\n" + "\n".join(f"Refs {ref}" for ref in refs))
    block = "\n\n".join(parts)
    if BLOCK_BEGIN in block or BLOCK_END in block:
        raise UsageError("PR content contains a reserved managed-block marker")
    if re.search(r"\b(?:close[sd]?|fix(?:es|ed)?|resolve[sd]?)[ :]+(?:[\w./-]+)?#\d+\b", block, re.IGNORECASE):
        raise UsageError("PR content contains an issue-closing keyword; use a plain reference")
    return f"[{initiative}]\n\n{BLOCK_BEGIN}\n{block}\n{BLOCK_END}\n" + (f"\n{extra}\n" if extra else "")


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


def read_pr(gh: Gh, repo: str, number: int, initiative_id: str | None, expect_refs: list[str]) -> dict[str, Any]:
    pr = gh.json("pr", "view", str(number), "--repo", repo,
                 "--json", "url,title,body,headRefOid,isDraft,baseRefName,headRefName,state")
    body = pr["body"] or ""
    first_line = next((line.strip() for line in body.splitlines() if line.strip()), "")
    marker = re.fullmatch(r"\[([^\[\]]+)\]", first_line)
    body_id = marker[1] if marker else first_line
    refs = sorted_unique(block_refs(body))
    problems = []
    if initiative_id:
        legacy = not marker and pr["title"].startswith(f"{initiative_id}: ")
        if body_id != initiative_id or (not marker and not legacy):
            problems.append(f"first body initiative is {body_id!r}, expected {initiative_id!r}")
        if not legacy and not valid_pr_title(pr["title"], initiative_id):
            problems.append("title lacks the expected initiative and conventional subject")
    if not pr["isDraft"]:
        problems.append("PR is not draft")
    missing = [str(parse_ref(ref)) for ref in expect_refs if str(parse_ref(ref)) not in refs]
    if missing:
        problems.append(f"missing managed references: {missing}")
    return {
        "number": number, "url": pr["url"], "title": pr["title"], "state": pr["state"], "is_draft": pr["isDraft"],
        "base": pr["baseRefName"], "head": pr["headRefName"], "head_sha": pr["headRefOid"],
        "first_body_id": body_id, "refs": refs, "checks": pr_checks(gh, repo, number), "problems": problems,
    }


def find_pr(gh: Gh, repo: str, head: str, *, state: str = "open") -> dict[str, Any] | None:
    found = gh.json("pr", "list", "--repo", repo, "--head", head, "--state", state,
                    "--json", "number,url,title,state,isDraft,baseRefName,headRefName,body")
    if len(found) > 1:
        raise UsageError(f"{len(found)} matching PRs for head {head}; resolve manually")
    return found[0] if found else None


def cmd_pr_publish(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    initiative = pr_initiative(args.initiative_id)
    if not valid_pr_title(args.title, initiative):
        raise UsageError(f"title must start with '[{initiative}] ' followed by a conventional commit subject")
    existing = find_pr(gh, args.source_repository, args.head, state="all")
    if existing and (existing.get("state", "OPEN") != "OPEN" or not existing["isDraft"]):
        raise UsageError(f"existing PR #{existing['number']} is not an open draft")
    if existing and existing["baseRefName"] != args.base:
        raise UsageError(f"existing PR #{existing['number']} targets {existing['baseRefName']}, expected {args.base}")
    old_body = (existing["body"] or "") if existing else ""
    if existing:
        old_title = existing["title"]
        first_line = next((line.strip() for line in old_body.splitlines() if line.strip()), "")
        matches = (
            old_title.startswith(f"{initiative}: ") and first_line == initiative
        ) or (
            valid_pr_title(old_title, initiative) and first_line == f"[{initiative}]"
        )
        if not matches:
            raise UsageError(f"existing PR #{existing['number']} has conflicting initiative metadata")
    refs = sorted_unique([str(parse_ref(ref)) for ref in args.refs] + block_refs(old_body))
    body = build_body(initiative, Path(args.rationale_file).read_text(encoding="utf-8"),
                      Path(args.changes_file).read_text(encoding="utf-8"), Path(args.evidence_file).read_text(encoding="utf-8"),
                      refs, user_text(old_body, initiative))
    with tempfile.TemporaryDirectory() as tmp:
        body_file = Path(tmp) / "pr.md"
        body_file.write_text(body, encoding="utf-8")
        if existing:
            number = existing["number"]
            if old_body != body or existing.get("title") != args.title:
                gh.text("pr", "edit", str(number), "--repo", args.source_repository,
                        "--title", args.title, "--body-file", str(body_file))
        else:
            url = gh.text("pr", "create", "--repo", args.source_repository, "--base", args.base, "--head", args.head,
                          "--draft", "--title", args.title, "--body-file", str(body_file)).strip().splitlines()[-1]
            number = int(url.rstrip("/").rsplit("/", 1)[-1])
    result = read_pr(gh, args.source_repository, number, initiative, refs)
    result["created"] = not existing
    return result


def cmd_pr_read(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    number = args.number
    if number is None:
        pr = find_pr(gh, args.source_repository, args.head) if args.head else None
        if not pr:
            raise UsageError("no open PR found; pass --number or a --head with an open PR")
        number = pr["number"]
    return read_pr(gh, args.source_repository, number, args.initiative_id, args.expect_refs)


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
        for group in ("spec", "graph", "ticket", "issue", "pr", "run")
    }

    def command(group: str | None, name: str, handler: Callable[..., dict[str, Any]]) -> argparse.ArgumentParser:
        sub = (groups if group is None else nested[group]).add_parser(name)
        sub.set_defaults(handler=handler)
        return sub

    p = command(None, "preflight", cmd_preflight)
    p.add_argument("--spec")
    p.add_argument("--harness-root")
    p.add_argument("--source-repository")
    p.add_argument("--base-branch")
    p.add_argument("--initiative-id")
    p.add_argument("--mode", choices=("sequential", "parallel"), default="sequential")
    p.add_argument("--max-parallel", type=int)
    p.add_argument("--pin-base", action="store_true")
    p.add_argument("--integration-branch")

    p = command("run", "checkpoint", cmd_run_checkpoint)
    p.add_argument("--run-dir", required=True)
    p.add_argument("--input", required=True)

    p = command("spec", "create", cmd_spec_create)
    for flag in ("source-repository", "base-branch", "initiative-id", "summary", "body-file", "source-note"):
        p.add_argument(f"--{flag}", required=True)
    p.add_argument("--tracker-repository")

    p = command("graph", "read", cmd_graph_read)
    p.add_argument("--spec", required=True)
    p.add_argument("--out", required=True)

    p = command("graph", "frontier", cmd_graph_frontier)
    p.add_argument("--graph", required=True)
    p.add_argument("--planner")
    p.add_argument("--out")
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
        if name == "comment":
            p.add_argument("--run-id")

    p = command("issue", "close", cmd_issue_close)
    p.add_argument("ref")
    for flag in ("commit", "branch", "pr", "comment", "run-id"):
        p.add_argument(f"--{flag}")
    p.add_argument("--evidence-comment", type=int)

    p = command("pr", "publish", cmd_pr_publish)
    for flag in ("source-repository", "base", "head", "title", "initiative-id", "rationale-file", "changes-file", "evidence-file"):
        p.add_argument(f"--{flag}", required=True)
    p.add_argument("--refs", action="extend", nargs="+", default=[])

    p = command("pr", "diff-split", cmd_pr_diff_split)
    p.add_argument("--pr", required=True)
    p.add_argument("--source-repository")

    p = command("pr", "read", cmd_pr_read)
    p.add_argument("--source-repository", required=True)
    p.add_argument("--number", type=int)
    p.add_argument("--head")
    p.add_argument("--initiative-id")
    p.add_argument("--expect-refs", action="extend", nargs="+", default=[])
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
