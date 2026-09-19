---
name: brief-daily
description: Report the current Jira user's blocked work items and open items where they're @mentioned in a comment, over a period defaulting to the last month. Use when asked for a daily briefing, standup update, or to show blocked or mentioned Jira items. Works against any connected Jira site — no project key or site configuration required.
argument-hint: '[period] (e.g. "2 weeks", "3 months"; default: 1 month)'
---

# Brief Daily

Two read-only Jira reports: work items blocked and assigned to the current user, and open items where the current user is `@mentioned` in a comment. Output is chat markdown only — never writes to a file, never calls a Jira write tool.

Budget: **two searches and two script runs**. Query B projects `comment`, so every comment body arrives with its issue — a per-issue `getJiraIssue` follow-up is the N+1 this skill exists to avoid. Both searches go out in one turn, then both scripts run in one turn.

## Workflow

**1 — Preflight.** Run `/preflight-atl` skill **Action: Resolve**. It returns `cloudId`, `accountId` and `displayName` — this skill resolves none of them itself.

**2 — Resolve period.** Parse `{{input}}`: empty → default `1 month`. Convert it into a JQL relative-date modifier in **days only** — never the `M` (month) unit (see Gotchas) — using 1 month ≈ 30 days: `1 month` → `-30d`, `"2 weeks"` → `-14d`, `"3 months"` → `-90d`. Keep the day count: it is Step 5's `--cutoff-days`.

**3 — Query A: blocked items assigned to me.** `searchJiraIssuesUsingJql` with `cloudId`, `jql: 'assignee = currentUser() AND (status = "Blocked" OR flagged = Impediment) AND updated >= <cutoffJql> ORDER BY updated DESC'`, `maxResults: 25`. Paginate per Pagination. Renders as section 1 of the output template.
- **Fallback:** some Jira instances have no `"Blocked"` status literal and the clause errors — retry with `jql: 'flagged = Impediment AND updated >= <cutoffJql> ORDER BY updated DESC'`, record the dropped clause under Excluded, and never fail the whole report over it.

**4 — Query B: mentions.** `searchJiraIssuesUsingJql` with `cloudId`, `fields: ["summary","status","comment"]`, `jql: 'comment ~ "<accountId>" AND statusCategory != Done AND updated >= <cutoffJql> ORDER BY updated DESC'`, `maxResults: 25`. Search by Preflight's `accountId`, never display name — a display-name search both false-positives on comments the user authored and misses real `@mentions`. Issue this in the same turn as Step 3.

**Pagination** (Steps 3 and 4): `maxResults` caps each call, not the result set. Page via `nextPageToken: d["issues"]["pageInfo"]["endCursor"]` until `hasNextPage` is `false` or 5 pages. Keep every page's `content.json` path — the scripts merge them, so pass one `--content` per page rather than merging by hand. Both scripts report `"truncated": true` when the last page still had more.

**5 — Extract.** Both searches spill to `content.json` (see Gotchas). `cd` to this skill's `scripts/` directory and run both in one turn:

```bash
python3 blocked.py --content <queryA.json>
python3 mentions.py --content <queryB.json> --account-id <accountId> --display-name "<displayName>" --cutoff-days <N>
```

`blocked.py` prints `{"rows": [...], "truncated": bool}` for section 1. `mentions.py` prints the buckets below, each row carrying `key`, `url`, `summary`, `status`, `mentionedBy`, `mentionedOn` — plus `answeredOn` and `answeredBy` where they apply. It keeps only comments mentioning `displayName` and `created` on or after the cutoff — JQL has no comment-date operator, so that filter runs after fetch, never in the JQL — then takes each issue's **latest** surviving mention and buckets it by what follows:

| JSON key | Rule | Renders as |
|---|---|---|
| `answeredByYou` | a comment authored by `accountId` created after the mention | section 3, `Answered by: you` |
| `answeredByOther` | a third party's comment created after the mention, no reply from you | section 3, `Answered by: <name>` |
| `unanswered` | no comment of either kind follows | section 2 |
| `cutoffExcluded` | issue matched the JQL, every mention of you predates the cutoff | Excluded |
| `partialComments` | the issue's comment thread came back shorter than its `total` | Excluded |

**6 — Output.** Print the template below as chat markdown — never write to `daily.md` or any other file.

## Output template

Omit a section with no rows rather than printing an empty table. Link every key with the row's own `url` — the payload carries it, so never assemble a browse link by hand.

````markdown
## Daily Briefing — {{site}} — Period: {{period}} (→ {{cutoffJql}}) — {{today}}

### 1. Blocked items assigned to you

| Key | Summary | Type | Status | Priority | Updated |
|---|---|---|---|---|---|
| [{{key}}]({{url}}) | {{summary}} | {{type}} | {{status}} | {{priority}} | {{updated}} |

### 2. Unanswered @mentions

No reply from you is visible via the API for these. Comment reactions are invisible to this tool, so one may already have been acknowledged with an emoji.

| Key | Summary | Status | Mentioned by | Mentioned on |
|---|---|---|---|---|
| [{{key}}]({{url}}) | {{summary}} | {{status}} | {{mentionedBy}} | {{mentionedOn}} |

### 3. Already answered

| Key | Summary | Mentioned by | Mentioned on | Answered on | Answered by |
|---|---|---|---|---|---|
| [{{key}}]({{url}}) | {{summary}} | {{mentionedBy}} | {{mentionedOn}} | {{answeredOn}} | {{answeredBy}} |

### Excluded

- Mention predates the period cutoff (issue `updated` in range, comment `created` not): {{cutoffExcluded}}
- Comment thread came back partial, so an answer may be missing: {{partialComments}} <!-- only when non-empty -->
- Results truncated at the 5-page cap — more candidates may exist. <!-- only when `truncated` -->
- `"Blocked"` status clause dropped; Query A ran on `flagged = Impediment` alone. <!-- only on fallback -->
````

## Gotchas

**The scripts resolve `brief_daily/` relative to the current directory** — run them from anywhere else and the import fails. `cd` to the directory holding this `SKILL.md`, then `cd scripts`, and call them by bare filename.

**Every search and most issue reads spill to a `content.json` path instead of returning inline** — `read_file` truncates a long line at roughly 2000 characters and loses the rest silently. Pass the path to `blocked.py`/`mentions.py` rather than reading it, per `/preflight-atl` skill **Standing MCP usage rules**.

**The response nests everything under `issues`** — `d["issues"]["nodes"]` is the issue list (a list even for a single-issue read), `d["issues"]["pageInfo"]` holds `hasNextPage` and `endCursor`, and `d["issues"]["nodes"][i]["fields"]["comment"]["comments"]` is the comment thread. `d["issues"]` is a dict: `d["issues"][0]` raises `KeyError: 0`, and a top-level `d.get("pageInfo")` returns `None`, which reads as "no more pages" and hides truncation.

**A mention's `data-id` is a positional placeholder, not an `accountId`** — a mention renders as `<custom data-type="mention" data-id="id-0">@Display Name</custom>`, where `id-0`, `id-1`, `id-2` restart per comment and map back to nothing. The comment carries `author.accountId` (a real id) but no legend for the mentioned party, so **matching the mention on `accountId` finds nothing and drops every candidate, producing a falsely empty report**. `mentions.py` matches the mention on `displayName` and reply authorship on `author.accountId`, which is why it needs both.

**`responseContentFormat: "adf"` changes nothing on this search** — verified against this MCP: the `adf` and default responses were byte-identical across all 38 comment bodies, both returning the `<custom …>` string form rather than an ADF document tree. Asking for it buys no `attrs.id` to match on.

**Searching `comment ~ "<display name>"` false-positives on the user's own authored comments and misses real `@mentions`** — Jira indexes `@mentions` by `accountId`; the JQL always searches by Preflight's `accountId`, even though the body match uses the display name.

**JQL has no operator for "unanswered since mention"** — JQL narrows candidates; `mentions.py`'s per-comment timestamp and author check decides the bucket.

**A third party often answers a mention addressed to you** — treating every non-you reply as silence produces recurring false positives, which is why `answeredByOther` is its own bucket instead of folding into `unanswered`.

**Comment emoji reactions are invisible via the `comment` field** — a mention can be acknowledged with a reaction and no reply ever appears, so a row in section 2 is "no reply visible", not "ignored". Section 2 says so and the report moves on.

**An issue's comment thread can come back shorter than its own `total`** — the `comment` envelope carries `total`, `startAt` and `maxResults`, and a mention sitting in an unreturned slice would read as absent. `mentions.py` reports those keys under `partialComments`.

**Not every Jira workflow defines a `"Blocked"` status literal** — the clause can error outright rather than return zero rows; Step 3's fallback retries with `flagged = Impediment` alone.

**The JQL relative-date modifier's `M` (month) unit silently returns zero matches instead of erroring** — confirmed against this MCP: `updated >= -1M` returns no rows for an issue updated days ago, while `updated >= -30d` returns it. Step 2 converts every period to `-Nd` for this reason.

## Degraded mode

No **Atlassian config** → Preflight's `cloudId` is empty and its Step 2 resolves it (asking when ambiguous). All other steps unchanged.
