"""Look up emoji reactions on Jira comments via the undocumented internal gateway endpoint.

Comment reactions are invisible through `getJiraIssue`'s `comment` field (see brief-daily's
Gotchas) but are exposed by Jira's browser-only `gateway/api/reactions/reactions/view`
endpoint. That endpoint only accepts a live browser session cookie (`tenant.session.token` +
friends) — `.atlassian`'s API token gets a 401. Capture the cookie from your browser's dev
tools (Network tab, any request to a `*.atlassian.net` page) and pass it via
`--cookie-file` or the `ATLASSIAN_SESSION_COOKIE` env var. The session expires in hours;
re-capture it when calls start returning 401.

Usage:
    python3 check_reactions.py --site zerto.atlassian.net --cloud-id 4b23b31c-89fc-47d9-a2e5-3018d6a55a66 \\
        --issue-id 693693 --comment-ids 2595640,2583602 --cookie-file /tmp/cookie.txt
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def _build_payload(cloud_id: str, issue_id: str, comment_ids: list[str]) -> dict:
    container_ari = f"ari:cloud:jira:{cloud_id}:issue/{issue_id}"
    return {
        "containerAri": container_ari,
        "aris": [f"ari:cloud:jira:{cloud_id}:comment/{cid}" for cid in comment_ids],
    }


def _resolve_cookie(cookie_arg: str | None, cookie_file: str | None) -> str:
    if cookie_arg:
        return cookie_arg
    if cookie_file:
        with open(cookie_file, encoding="utf-8") as fh:
            return fh.read().strip()
    env_cookie = os.environ.get("ATLASSIAN_SESSION_COOKIE", "").strip()
    if env_cookie:
        return env_cookie
    raise SystemExit("No session cookie supplied — use --cookie, --cookie-file, or ATLASSIAN_SESSION_COOKIE")


def fetch_reactions(site: str, cloud_id: str, issue_id: str, comment_ids: list[str], cookie: str) -> dict:
    url = f"https://{site}/gateway/api/reactions/reactions/view"
    payload = _build_payload(cloud_id, issue_id, comment_ids)
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cookie": cookie,
            "Origin": f"https://{site}",
            "Referer": f"https://{site}/browse/{issue_id}",
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code} from reactions endpoint — session cookie likely expired: {body}") from exc


def summarize(raw: dict) -> str:
    lines = []
    for ari, reactions in raw.items():
        comment_id = ari.rsplit("/", 1)[-1]
        if not reactions:
            lines.append(f"- comment {comment_id}: no reactions")
            continue
        for reaction in reactions:
            name = reaction.get("emojiName", "?")
            count = reaction.get("count", 0)
            reacted = " (you reacted)" if reaction.get("reacted") else ""
            lines.append(f"- comment {comment_id}: {name} x{count}{reacted}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", required=True, help="Jira site host, e.g. zerto.atlassian.net")
    parser.add_argument("--cloud-id", required=True, help="Site cloudId UUID (not the ATLASSIAN_SITE host form)")
    parser.add_argument("--issue-id", required=True, help="Numeric issue id (not the issue key)")
    parser.add_argument("--comment-ids", required=True, help="Comma-separated numeric comment ids")
    parser.add_argument("--cookie", help="Raw Cookie header value")
    parser.add_argument("--cookie-file", help="Path to a file containing the Cookie header value")
    args = parser.parse_args()

    cookie = _resolve_cookie(args.cookie, args.cookie_file)
    comment_ids = [c.strip() for c in args.comment_ids.split(",") if c.strip()]
    raw = fetch_reactions(args.site, args.cloud_id, args.issue_id, comment_ids, cookie)
    print(summarize(raw))
    return 0


if __name__ == "__main__":
    sys.exit(main())
