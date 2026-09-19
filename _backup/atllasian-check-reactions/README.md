# check_reactions.py (archived)
Open issue in the atllasian https://jira.atlassian.com/browse/JRACLOUD-78153
Standalone script that queries Jira's **undocumented internal** endpoint
`gateway/api/reactions/reactions/view` to read emoji reactions on comments —
data that `getJiraIssue`'s `comment` field never exposes (see `brief-daily`'s
Gotchas on unanswered `@mentions`).

## Why it's archived, not a live skill script

- The endpoint only accepts a **live browser session cookie**
  (`tenant.session.token` + friends). `.atlassian`'s `ATLASSIAN_API_TOKEN`
  gets a `401` — confirmed by testing Basic auth against it directly.
- Without any cookie at all, the endpoint returns
  `{"code":401,"message":"Unauthorized"}` — there is no anonymous path.
- A session cookie is ephemeral (expires in hours) and must be hand-captured
  from the browser's dev tools (Network tab, any request to a
  `*.atlassian.net` page), so this can't be wired into `brief-daily`'s
  automated flow without a manual step every run.
- It's reverse-engineered, unofficial API surface — not documented by
  Atlassian and liable to change or break without notice.

## Usage (when a fresh cookie is available)

```bash
python3 check_reactions.py --site zerto.atlassian.net \
  --cloud-id 4b23b31c-89fc-47d9-a2e5-3018d6a55a66 \
  --issue-id 693693 --comment-ids 2595640,2583602 \
  --cookie-file /tmp/cookie.txt
```

- `--cloud-id` is the site's UUID `cloudId` (not the `ATLASSIAN_SITE` host
  string) — visible in any `getJiraIssue` response's `self` URL
  (`.../ex/jira/<cloud-id>/rest/...`).
- `--issue-id` / `--comment-ids` are the **numeric** internal IDs, not the
  issue key or a public comment reference.
- Cookie can also come from `--cookie` (raw string) or the
  `ATLASSIAN_SESSION_COOKIE` env var.

Output is a one-line-per-reaction summary, e.g.:

```
- comment 2583602: no reactions
- comment 2595640: thumbs up x1 (you reacted)
```
