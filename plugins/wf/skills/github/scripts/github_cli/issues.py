from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from .gh import Gh, GhError, Ref, UsageError, parse_ref, read_body, repository, request


def endpoint(ref: Ref) -> str:
    return f"repos/{ref.repo}/issues/{ref.number}"


def read_issue(gh: Gh, ref: Ref) -> dict[str, Any]:
    return gh.json("api", endpoint(ref))


def read_comments(gh: Gh, ref: Ref) -> list[dict[str, Any]]:
    return gh.pages(f"{endpoint(ref)}/comments")


def labels_of(issue: dict[str, Any]) -> list[str]:
    return [label["name"] if isinstance(label, dict) else label for label in issue.get("labels", [])]


def issue_read(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref, kind="issues")
    issue = read_issue(gh, ref)
    if args.comments:
        issue["comments"] = read_comments(gh, ref)
    return issue


def list_issues(gh: Gh, repo: str, labels: list[str]) -> list[dict[str, Any]]:
    query = urlencode({"state": "all", "labels": ",".join(labels), "per_page": 100})
    return [item for item in gh.pages(f"repos/{repository(repo)}/issues?{query}") if "pull_request" not in item]


def issue_list(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    return {"issues": list_issues(gh, args.repo, args.label)}


def create_issue(
    gh: Gh, repo: str, title: str, body: str, labels: list[str], *, reconcile: bool = True
) -> dict[str, Any]:
    def matches(issue: dict[str, Any]) -> bool:
        return issue["title"] == title and issue.get("body") == body and set(labels) <= set(labels_of(issue))

    candidates = [issue for issue in list_issues(gh, repo, labels) if issue["title"] == title] if reconcile else []
    if candidates:
        if len(candidates) != 1 or not matches(candidates[0]):
            raise UsageError(f"ambiguous or conflicting issue for {title!r}")
        return {**candidates[0], "created": False}
    created = request(gh, f"repos/{repository(repo)}/issues", "POST", {
        "title": title, "body": body, "labels": labels,
    })
    ref = Ref(repo, created["number"])
    try:
        observed = read_issue(gh, ref)
    except GhError as exception:
        raise GhError(f"created {ref}; verification failed: {exception}") from exception
    return {**observed, "created": True, "problems": [] if matches(observed) else ["issue differs after create"]}


def issue_create(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    return create_issue(gh, args.repo, args.title, read_body(args.body_file), args.label)


def children(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref, kind="issues")
    return {"children": gh.pages(f"{endpoint(ref)}/sub_issues?per_page=100")}


def blockers(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref, kind="issues")
    return {"blockers": gh.pages(f"{endpoint(ref)}/dependencies/blocked_by?per_page=100")}


def link_child(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    parent, child = parse_ref(args.ref, kind="issues"), parse_ref(args.child, kind="issues")
    if parent == child:
        raise UsageError("an issue cannot be its own child")
    child_id = read_issue(gh, child)["id"]
    path = f"{endpoint(parent)}/sub_issues?per_page=100"
    if not any(row["id"] == child_id for row in gh.pages(path)):
        try:
            request(gh, f"{endpoint(parent)}/sub_issues", "POST", {"sub_issue_id": child_id})
        except GhError as exception:
            if not any(row["id"] == child_id for row in gh.pages(path)):
                raise GhError(f"{child} exists; parent link to {parent} unconfirmed: {exception}") from exception
    if not any(row["id"] == child_id for row in gh.pages(path)):
        raise GhError(f"{child} exists; parent link to {parent} unconfirmed")
    return {"parent": str(parent), "child": str(child), "linked": True}


def change_assignment(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref, kind="issues")
    login = gh.json("api", "user")["login"] if args.login == "@me" else args.login
    issue = read_issue(gh, ref)
    assigned = [user["login"] for user in issue["assignees"]]
    if args.action == "assign":
        if issue["state"] != "open" or any(other != login for other in assigned):
            raise UsageError(f"issue is no longer claimable: {ref}")
        if not assigned:
            request(gh, f"{endpoint(ref)}/assignees", "POST", {"assignees": [login]})
    elif login in assigned:
        request(gh, f"{endpoint(ref)}/assignees", "DELETE", {"assignees": [login]})
    observed = read_issue(gh, ref)
    assigned = [user["login"] for user in observed["assignees"]]
    verified = observed["state"] == "open" and assigned == [login] if args.action == "assign" else login not in assigned
    return {"assignees": assigned, "problems": [] if verified else ["assignment differs after write"]}


def label_names(gh: Gh, repo: str) -> set[str]:
    return {item["name"] for item in gh.pages(f"repos/{repository(repo)}/labels?per_page=100")}


def manage_labels(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    repo = repository(args.repo)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8")) if args.manifest else []
    labels = {item["name"]: item for item in manifest}
    if args.name:
        if args.name in labels:
            raise UsageError("label already supplied in manifest")
        labels[args.name] = {"name": args.name, "color": args.color, "description": args.description}
    if not labels:
        raise UsageError("supply a label name or manifest")
    if args.action == "ensure":
        for label in labels.values():
            if not re.fullmatch(r"[0-9a-fA-F]{6}", label.get("color") or ""):
                raise UsageError(f"invalid label color: {label['name']}")
    existing = label_names(gh, repo)
    created = []
    if args.action == "ensure":
        for name, label in labels.items():
            if name not in existing:
                try:
                    request(gh, f"repos/{repo}/labels", "POST", label)
                except GhError:
                    if name not in label_names(gh, repo):
                        raise
                created.append(name)
        existing = label_names(gh, repo)
    missing = [name for name in labels if name not in existing]
    return {"labels": [name for name in labels if name in existing], "created": created, "missing": missing,
            "problems": [f"missing label: {name}" for name in missing]}
