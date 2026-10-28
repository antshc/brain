#!/usr/bin/env python3
"""Stateful stand-in for the `gh` CLI used by the spec_gh integration tests.

State lives in the JSON file named by FAKE_GH_STATE. Only the commands spec_gh issues are emulated;
anything else exits 99 so an unexpected call fails the test loudly.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

STATE = Path(os.environ["FAKE_GH_STATE"])


def fail(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    sys.exit(code)


def opt(args: list[str], name: str, default: str | None = None) -> str | None:
    return args[args.index(name) + 1] if name in args else default


def public(issue: dict) -> dict:
    return {key: value for key, value in issue.items() if not key.startswith("_")}


def new_number(state: dict, repo: str) -> int:
    state["counters"][repo] = state["counters"].get(repo, 0) + 1
    return state["counters"][repo]


def new_issue(state: dict, repo: str, title: str, body: str, labels: list[str]) -> dict:
    missing = [name for name in labels if name not in state["labels"].get(repo, [])]
    if missing:
        fail(f"could not add label: {missing[0]!r} not found")
    state["next_id"] += 1
    number = new_number(state, repo)
    issue = {
        "id": state["next_id"], "number": number, "title": title, "body": body, "state": "open", "state_reason": None,
        "labels": [{"name": name} for name in labels], "repository_url": f"https://api.github.com/repos/{repo}",
        "html_url": f"https://github.com/{repo}/issues/{number}", "_sub": [], "_blocked_by": [],
    }
    state["issues"][f"{repo}#{number}"] = issue
    return issue


def get_issue(state: dict, repo: str, number: int) -> dict:
    issue = state["issues"].get(f"{repo}#{number}")
    if not issue:
        fail("gh: Not Found (HTTP 404)")
    return issue


def by_id(state: dict, issue_id: int) -> dict:
    for issue in state["issues"].values():
        if issue["id"] == issue_id:
            return issue
    fail("gh: Not Found (HTTP 404)")


def emit(data, args: list[str]) -> None:
    jq = opt(args, "--jq")
    if jq == ".id":
        print(data["id"])
    elif "--slurp" in args:
        print(json.dumps([data]))
    else:
        print(json.dumps(data))


def api(state: dict, args: list[str]) -> bool:
    endpoint = next(arg for arg in args if arg.startswith("repos/"))
    method = opt(args, "--method", "GET")
    field = opt(args, "-F", "")
    match = re.fullmatch(r"repos/([^/]+/[^/]+)/branches/(.+)", endpoint)
    if match:
        if unquote(match.group(2)) not in state["repos"].get(match.group(1), {}).get("branches", []):
            fail("gh: Branch not found (HTTP 404)")
        print("{}")
        return False
    match = re.fullmatch(r"repos/([^/]+/[^/]+)/issues/comments/(\d+)", endpoint)
    if match:
        emit(state["comments"][match.group(2)], args)
        return False
    match = re.fullmatch(r"repos/([^/]+/[^/]+)/issues/(\d+)/(comments|sub_issues|dependencies/blocked_by)", endpoint)
    if match:
        repo, number, kind = match.group(1), int(match.group(2)), match.group(3)
        issue = get_issue(state, repo, number)
        if kind == "comments":
            emit([c for c in state["comments"].values() if c["issue"] == f"{repo}#{number}"], args)
        elif method == "POST":
            target = by_id(state, int(field.split("=")[1]))
            slot = "_sub" if kind == "sub_issues" else "_blocked_by"
            if target["id"] in issue[slot]:
                fail("gh: already exists (HTTP 422)")
            issue[slot].append(target["id"])
            print("{}")
            return True
        else:
            slot = "_sub" if kind == "sub_issues" else "_blocked_by"
            emit([public(by_id(state, issue_id)) for issue_id in issue[slot]], args)
        return False
    match = re.fullmatch(r"repos/([^/]+/[^/]+)/issues/(\d+)", endpoint)
    if match:
        emit(public(get_issue(state, match.group(1), int(match.group(2)))), args)
        return False
    fail(f"fake gh: unsupported api endpoint {endpoint}", 99)
    return False


def add_comment(state: dict, repo: str, number: int, body: str) -> str:
    state["next_id"] += 1
    comment_id = str(state["next_id"])
    state["comments"][comment_id] = {"id": int(comment_id), "body": body, "issue": f"{repo}#{number}"}
    return f"https://github.com/{repo}/issues/{number}#issuecomment-{comment_id}"


def run(args: list[str], state: dict) -> bool:
    if args[:1] == ["--version"]:
        print("gh version fake")
    elif args[:2] == ["auth", "status"]:
        return False
    elif args[:2] == ["repo", "view"]:
        repo = next((arg for arg in args[2:] if not arg.startswith("-") and "/" in arg), state["default_repo"])
        if repo not in state["repos"]:
            fail("gh: Could not resolve to a Repository (HTTP 404)")
        if "--jq" in args:
            print(repo)
        else:
            print(json.dumps({"nameWithOwner": repo, "defaultBranchRef": {"name": state["repos"][repo]["default"]}}))
    elif args[:1] == ["api"]:
        return api(state, args)
    elif args[:2] == ["label", "list"]:
        repo, needle = opt(args, "--repo"), opt(args, "--search", "")
        print(json.dumps([{"name": name} for name in state["labels"].get(repo, []) if needle in name]))
    elif args[:2] == ["label", "create"]:
        state["labels"].setdefault(opt(args, "--repo"), []).append(args[2])
    elif args[:2] == ["issue", "create"]:
        repo = opt(args, "--repo")
        labels = [name for name in (opt(args, "--label", "") or "").split(",") if name]
        issue = new_issue(state, repo, opt(args, "--title"), Path(opt(args, "--body-file")).read_text(), labels)
        print(issue["html_url"])
    elif args[:2] == ["issue", "comment"]:
        print(add_comment(state, opt(args, "--repo"), int(args[2]), Path(opt(args, "--body-file")).read_text()))
    elif args[:2] == ["issue", "close"]:
        issue = get_issue(state, opt(args, "--repo"), int(args[2]))
        issue["state"], issue["state_reason"] = "closed", opt(args, "--reason", "completed")
        if opt(args, "--comment"):
            add_comment(state, opt(args, "--repo"), int(args[2]), opt(args, "--comment"))
    elif args[:2] == ["issue", "edit"]:
        get_issue(state, opt(args, "--repo"), int(args[2]))["body"] = Path(opt(args, "--body-file")).read_text()
    elif args[:2] == ["issue", "list"]:
        repo, label = opt(args, "--repo"), opt(args, "--label")
        needle = (opt(args, "--search", "") or "").replace(" in:title", "")
        print(json.dumps([
            {"number": i["number"], "title": i["title"]} for key, i in state["issues"].items()
            if key.startswith(f"{repo}#") and label in [x["name"] for x in i["labels"]] and needle in i["title"]
        ]))
    elif args[:2] == ["pr", "create"]:
        repo = opt(args, "--repo")
        number = new_number(state, repo)
        state["prs"].append({
            "repo": repo, "number": number, "url": f"https://github.com/{repo}/pull/{number}", "title": opt(args, "--title"),
            "body": Path(opt(args, "--body-file")).read_text(), "isDraft": "--draft" in args, "baseRefName": opt(args, "--base"),
            "headRefName": opt(args, "--head"), "headRefOid": "deadbeef", "state": "OPEN",
        })
        print(state["prs"][-1]["url"])
    elif args[:2] == ["pr", "list"]:
        print(json.dumps([p for p in state["prs"] if p["repo"] == opt(args, "--repo") and p["headRefName"] == opt(args, "--head")]))
    elif args[:2] in (["pr", "edit"], ["pr", "view"]):
        pr = next(p for p in state["prs"] if p["number"] == int(args[2]) and p["repo"] == opt(args, "--repo"))
        if args[1] == "edit":
            pr["title"], pr["body"] = opt(args, "--title"), Path(opt(args, "--body-file")).read_text()
        else:
            print(json.dumps(pr))
    elif args[:2] == ["pr", "diff"]:
        print(state.get("diff", ""), end="")
    elif args[:2] == ["pr", "checks"]:
        checks = state["checks"].get(args[2])
        if not checks:
            fail("no checks reported on the 'feat' branch")
        print(json.dumps(checks))
        sys.exit(8 if any(c["bucket"] == "pending" for c in checks) else 0)
    else:
        fail(f"fake gh: unsupported command {' '.join(args)}", 99)
    return True


def main() -> None:
    state = json.loads(STATE.read_text())
    if run(sys.argv[1:], state):
        STATE.write_text(json.dumps(state))


if __name__ == "__main__":
    main()
