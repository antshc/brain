from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from .gh import Gh, GhError, UsageError, parse_ref, read_body, repository
from .implement_spec import cmd_spec_create, read_artifacts, validate_initiative_id
from .issues import create_issue, label_names, list_issues, manage_labels


def spec_create(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    if args.profile == "implement-spec":
        if not args.source_note:
            raise UsageError("Implement Spec publication requires --source-note")
        return cmd_spec_create(gh, args)

    tracker = repository(args.tracker_repository or "")
    source = repository(args.source_repository)
    initiative = validate_initiative_id(args.initiative_id)
    target = f"repo:target:{source}"
    base = f"repo:base:{args.base_branch}"
    body = read_body(args.body_file)
    if "spec" not in label_names(gh, tracker):
        raise UsageError(f"{tracker} lacks the spec label; run WF labels-only setup")
    candidates = [item for item in list_issues(gh, tracker, ["spec", target])
                  if item["title"].startswith(f"{initiative}:")]
    if candidates:
        raise UsageError("spec already exists: " + ", ".join(item["html_url"] for item in candidates))
    for name, color, description in (
        (target, "0e8a16", "Source repository for this spec's tickets"),
        (base, "c5def5", "Base branch for this spec's feature branch"),
    ):
        result = manage_labels(gh, argparse.Namespace(repo=tracker, manifest=None, name=name,
                                                      color=color, description=description, action="ensure"))
        if result["problems"]:
            raise GhError(result["problems"][0])
    return create_issue(gh, tracker, f"{initiative}: {args.summary}", body, ["spec", target, base], reconcile=False)


def artifacts(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref, kind="issues")
    rows, unavailable = read_artifacts(gh, ref)
    if unavailable:
        raise GhError(unavailable)
    if args.action == "list":
        return {"artifacts": rows}
    if args.action == "get":
        matches = [item for item in rows if item["number"] == args.number]
        if len(matches) != 1:
            raise UsageError(f"artifact {args.number} not found on {ref}")
        return matches[0]

    version = re.search(r"gh version (\d+)\.(\d+)\.(\d+)", gh.text("--version"))
    if not version or tuple(map(int, version.groups())) < (2, 103, 2):
        raise UsageError("writing issue artifacts requires gh 2.103.2 or newer")
    path = Path(args.body_file).resolve(strict=True)
    expected = read_body(path)
    matches = [item for item in rows if item["name"] == args.name]
    if len(matches) > 1 or (matches and matches[0]["type"] != args.type):
        raise UsageError(f"artifact name or type conflicts on {ref}: {args.name}")
    common = ("--body-file", str(path), "-R", ref.repo)
    if not matches:
        gh.text("issue", "artifact", "create", str(ref.number), "--name", args.name, "--type", args.type, *common)
    elif matches[0].get("body") != expected:
        gh.text("issue", "artifact", "edit", str(ref.number), str(matches[0]["number"]), *common)
    observed, unavailable = read_artifacts(gh, ref)
    exact = [item for item in observed if item["name"] == args.name]
    if unavailable or len(exact) != 1 or exact[0]["type"] != args.type or exact[0].get("body") != expected:
        raise GhError(f"artifact write unconfirmed on {ref}: {args.name}")
    return exact[0]
