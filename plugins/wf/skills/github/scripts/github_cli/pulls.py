from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode

from .gh import Gh, GhError, Ref, UsageError, parse_ref, read_body, repository, request
from .git import checkout, sha, verify_remote
from .implement_spec import cmd_pr_diff_split, find_pr, pr_checks
from .issues import read_comments


def metadata(gh: Gh, ref: Ref) -> dict[str, Any]:
    return gh.json("api", f"repos/{ref.repo}/pulls/{ref.number}")


def require_snapshot(gh: Gh, ref: Ref, head: str, base: str | None = None) -> dict[str, Any]:
    pr = metadata(gh, ref)
    if pr["state"] != "open" or pr["head"]["sha"] != head or (base and pr["base"]["sha"] != base):
        raise UsageError(f"pull request state or reviewed head/base changed: {ref}")
    return pr


def pr_find(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    return {"pullRequest": find_pr(gh, repository(args.repo), args.head)}


def pr_snapshot(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref, kind="pull")
    result = metadata(gh, ref)
    if args.inline:
        result["inlineComments"] = gh.pages(f"repos/{ref.repo}/pulls/{ref.number}/comments?per_page=100")
    if args.comments:
        result["comments"] = read_comments(gh, ref)
    return result


def pr_diff(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref, kind="pull")
    require_snapshot(gh, ref, args.expected, args.base)
    diff = gh.text("pr", "diff", str(ref.number), "--repo", ref.repo)
    require_snapshot(gh, ref, args.expected, args.base)
    return {"diff": diff, "head": args.expected, "base": args.base}


def pr_diff_split(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    if not args.expected and not args.base:
        return cmd_pr_diff_split(gh, args)
    if not args.expected or not args.base:
        raise UsageError("pinned diff acquisition requires both --expected and --base")
    ref = parse_ref(args.pr, args.source_repository, kind="pull")
    require_snapshot(gh, ref, args.expected, args.base)
    result = cmd_pr_diff_split(gh, args)
    try:
        require_snapshot(gh, ref, args.expected, args.base)
    except (GhError, UsageError) as exception:
        raise GhError(f"PR diff unverified; discard snapshot at {result['diff_dir']}: {exception}") from exception
    return result


def pr_checkout(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref, kind="pull")
    root = checkout(gh, args)
    if Path.cwd().resolve() != Path(root):
        raise UsageError("run interactive PR checkout from the verified checkout root")
    verify_remote(gh, root, args.remote, ref.repo)
    if gh.git("-C", root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise UsageError("interactive checkout is dirty")
    require_snapshot(gh, ref, args.expected, args.base)
    gh.text("pr", "checkout", str(ref.number), "--repo", ref.repo)
    if gh.git("-C", root, "rev-parse", "HEAD").strip() != args.expected:
        raise UsageError("checked-out HEAD differs from the reviewed head")
    return {"checkout": root, "head": args.expected}


def pr_comment(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref, kind="pull")
    metadata(gh, ref)
    return write_comment(gh, ref, args)


def issue_comment(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    return write_comment(gh, parse_ref(args.ref, kind="issues"), args)


def write_comment(gh: Gh, ref: Ref, args: argparse.Namespace) -> dict[str, Any]:
    body = read_body(args.body_file)
    marker = args.marker
    if marker and (not marker.startswith("<!-- ") or not marker.endswith(" -->") or marker not in body.splitlines()):
        raise UsageError("the body must contain the exact standalone comment marker")
    matches = [comment for comment in read_comments(gh, ref)
               if (marker in comment["body"].splitlines() if marker else comment["body"] == body)]
    if len(matches) > 1:
        raise UsageError("multiple matching comments; reconcile before writing")
    comments = f"repos/{ref.repo}/issues"
    if matches and matches[0]["body"] == body:
        observed = matches[0]
    else:
        if matches:
            login = gh.json("api", "user")["login"]
            if matches[0]["user"]["login"] != login:
                raise UsageError("matched comment belongs to another author")
            changed = request(gh, f"{comments}/comments/{matches[0]['id']}", "PATCH", {"body": body})
        else:
            changed = request(gh, f"{comments}/{ref.number}/comments", "POST", {"body": body})
        observed = gh.json("api", f"{comments}/comments/{changed['id']}")
    if observed["body"] != body:
        raise GhError(f"comment {observed['id']} differs after write")
    return {"id": observed["id"], "url": observed.get("html_url"), "body": observed["body"]}


def checks(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref, kind="pull")
    require_snapshot(gh, ref, args.expected)
    result = pr_checks(gh, ref.repo, ref.number)
    require_snapshot(gh, ref, args.expected)
    return {**result, "head": args.expected}


def pr_open(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    repo = repository(args.repo)
    owner = repo.split("/")[0]
    body = read_body(args.body_file)
    branch = gh.json("api", f"repos/{repo}/branches/{quote(args.head, safe='')}")
    if branch["commit"]["sha"] != args.expected:
        raise UsageError("remote PR branch head changed")
    query = urlencode({"head": f"{owner}:{args.head}", "base": args.base, "state": "open", "per_page": 100})
    matches = gh.pages(f"repos/{repo}/pulls?{query}")
    if len(matches) > 1:
        raise UsageError("multiple pull requests match the head and base")
    if matches:
        number = matches[0]["number"]
    else:
        created = request(gh, f"repos/{repo}/pulls", "POST", {
            "head": args.head, "base": args.base, "title": args.title, "body": body, "draft": args.draft,
        })
        number = created["number"]
    pr = require_snapshot(gh, Ref(repo, number), args.expected)
    if (pr["head"]["repo"]["full_name"].casefold() != repo.casefold() or pr["head"]["ref"] != args.head
            or pr["base"]["ref"] != args.base or pr["title"] != args.title or pr.get("body") != body
            or pr["draft"] != args.draft):
        raise UsageError(f"existing pull request differs: {pr['html_url']}")
    return pr


def pr_fetch(gh: Gh, args: argparse.Namespace) -> dict[str, Any]:
    ref = parse_ref(args.ref, kind="pull")
    root = checkout(gh, args)
    verify_remote(gh, root, args.remote, ref.repo)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", args.run_id):
        raise UsageError("invalid PR snapshot run ID")
    head = sha(args.expected)
    base = sha(args.base)
    namespace = f"refs/review/{args.run_id}"
    head_ref, base_ref = f"{namespace}/head", f"{namespace}/base"
    if gh.git("-C", root, "for-each-ref", "--format=%(refname)", namespace):
        raise UsageError(f"PR snapshot refs already exist: {namespace}")
    require_snapshot(gh, ref, head, base)
    gh.git("-C", root, "fetch", "--no-tags", "--no-write-fetch-head", "--atomic", "--", args.remote,
           f"refs/pull/{ref.number}/head:{head_ref}", f"{base}:{base_ref}")
    observed_head = gh.git("-C", root, "rev-parse", "--verify", head_ref).strip()
    observed_base = gh.git("-C", root, "rev-parse", "--verify", base_ref).strip()
    try:
        if observed_head != head or observed_base != base:
            raise UsageError("fetched PR head or base changed")
        require_snapshot(gh, ref, head, base)
        merge_base = gh.git("-C", root, "merge-base", base, head).strip()
    except (GhError, UsageError) as exception:
        raise GhError(f"PR snapshot incomplete; reconcile {head_ref} at {observed_head} "
                      f"and {base_ref} at {observed_base}: {exception}") from exception
    return {"head": head, "base": base, "mergeBase": merge_base, "headRef": head_ref, "baseRef": base_ref}
