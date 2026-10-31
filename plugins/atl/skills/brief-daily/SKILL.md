---
name: brief-daily
description: >-
  Report the current Jira user's blocked work items and open items where they're @mentioned in a comment, over a period defaulting to the last month. Use when asked for a daily briefing, standup update, or to show blocked or mentioned Jira items. Queries Jira through the twg CLI; no project key required.
argument-hint: '[period] (e.g. "2 weeks", "3 months"; default: 1 month)'
---

# Brief Daily

Two read-only Jira reports: work items blocked and assigned to the current user, and open items where the current user is `@mentioned` in a comment. Output is chat markdown only — never writes a report file, never runs a twg write command.

Budget: **two searches and two script runs**. Query B requests `comment`, so every comment body arrives with its issue — a per-issue follow-up read is the N+1 this skill exists to avoid. Both searches go out in one shell call, then both scripts run in one shell call.

## Workflow

**1 — Preflight.** *Run `preflight-atlassian` skill to resolve site, credentialed twg command, and identity from `.atlassian.json.user` config* **Action: Resolve**. It returns `twg` and `accountId` — this skill resolves neither itself. Searches follow *`twg` skill for Jira workitems and JQL* through Preflight's `twg`.

**2 — Resolve period.** Parse `{{input}}`: empty → default `1 month`. Convert it into a JQL relative-date modifier in **days only** — never the `M` (month) unit (see Gotchas) — using 1 month ≈ 30 days: `1 month` → `-30d`, `"2 weeks"` → `-14d`, `"3 months"` → `-90d`. Keep the day count: it is Step 5's `--cutoff-days`.

**3 — Query A: blocked items assigned to me.**
```bash
<twg> jira workitem query --jql 'assignee = currentUser() AND (status = "Blocked" OR flagged = Impediment) AND updated >= <cutoffJql> ORDER BY updated DESC' --fields summary,status,issuetype,priority,updated --limit 25 -o json --output-file queryA-1.json
```
Renders as section 1 of the output template.
- **Fallback:** some Jira instances have no `"Blocked"` status literal and the clause errors — retry with `jql: 'flagged = Impediment AND updated >= <cutoffJql> ORDER BY updated DESC'`, record the dropped clause under Excluded, and never fail the whole report over it.

**4 — Query B: mentions.**
```bash
<twg> jira workitem query --jql 'comment ~ "<accountId>" AND statusCategory != Done AND updated >= <cutoffJql> ORDER BY updated DESC' --fields summary,status,comment --limit 25 -o json --output-file queryB-1.json
```
Search by Preflight's `accountId`, never display name — a display-name search both false-positives on comments the user authored and misses real `@mentions`. Issue this in the same shell call as Step 3, separated by `;`.

**Pagination** (Steps 3 and 4): `--limit` caps each call, not the result set. Page with `--after <pageInfo.nextCursor>` into `query<A|B>-<n>.json` until `pageInfo.hasNextPage` is `false` or 5 pages. Pass one `--content` per page rather than merging by hand. Both scripts report `"truncated": true` when the last page still had more.

**5 — Extract.** `cd` to this skill's `scripts/` directory and run both in one shell call:

```bash
python3 blocked.py --content <queryA-1.json> [--content <queryA-2.json> ...]
python3 mentions.py --content <queryB-1.json> [--content ...] --account-id <accountId> --cutoff-days <N>
```

`blocked.py` prints `{"rows": [...], "truncated": bool}` for section 1. `mentions.py` prints the buckets below, each row carrying `key`, `url`, `summary`, `status`, `mentionedBy`, `mentionedOn` — plus `answeredOn` and `answeredBy` where they apply. It keeps only comments whose ADF holds a `mention` node for `accountId` and `created` on or after the cutoff — JQL has no comment-date operator, so that filter runs after fetch, never in the JQL — then takes each issue's **latest** surviving mention and buckets it by what follows:

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

**Never `find`/`grep`/`ls -R` the filesystem to locate this skill's own directory.** The tool/system context that told you this skill exists already gave you `brief-daily/SKILL.md`'s absolute path verbatim (it's how you're reading this). Take that literal path's parent directory directly (e.g. strip the trailing `/SKILL.md` yourself) — never rediscover it with a search rooted at `/`, `$HOME`, or any other unbounded root, even bounded by `-maxdepth`.

**The scripts resolve `brief_daily/` relative to the current directory** — run them from anywhere else and the import fails. `cd` to the directory holding this `SKILL.md`, then `cd scripts`, and call them by bare filename.

**Always pass `-o json --output-file <path>` to twg** — run by an agent, twg otherwise prints a YAML envelope pointing at spill files, not the payload, and `read_file` truncates long lines at roughly 2000 characters. Pass the path to `blocked.py`/`mentions.py` rather than reading it, per `preflight-atlassian` skill **Standing usage rules**.

**twg flattens Jira fields onto each issue** — `data.issues[i].summary`, `.status`, `.comment.comments`, plus a ready browse `url`; there is no `fields` wrapper. Pagination is `pageInfo.hasNextPage`/`nextCursor` at the top level.

**A mention is an ADF `mention` node whose `attrs.id` is the mentioned `accountId`** — comment bodies arrive as ADF, so `mentions.py` matches the mention and reply authorship on `accountId` alone; a display name in plain text never counts.

**Searching `comment ~ "<display name>"` false-positives on the user's own authored comments and misses real `@mentions`** — Jira indexes `@mentions` by `accountId`; the JQL always searches by Preflight's `accountId`.

**JQL has no operator for "unanswered since mention"** — JQL narrows candidates; `mentions.py`'s per-comment timestamp and author check decides the bucket.

**A third party often answers a mention addressed to you** — treating every non-you reply as silence produces recurring false positives, which is why `answeredByOther` is its own bucket instead of folding into `unanswered`.

**Comment emoji reactions are invisible via the `comment` field** — a mention can be acknowledged with a reaction and no reply ever appears, so a row in section 2 is "no reply visible", not "ignored". Section 2 says so and the report moves on.

**An issue's comment thread can come back shorter than its own `total`** — twg returns the newest 20 comments; the `comment` envelope carries `total`, `startAt` and `maxResults`, and a mention sitting in an unreturned slice would read as absent. `mentions.py` reports those keys under `partialComments`.

**Not every Jira workflow defines a `"Blocked"` status literal** — the clause can error outright rather than return zero rows; Step 3's fallback retries with `flagged = Impediment` alone.

**The JQL relative-date modifier's `M` (month) unit silently returns zero matches instead of erroring** — confirmed live: `updated >= -1M` returns no rows for an issue updated days ago, while `updated >= -30d` returns it. Step 2 converts every period to `-Nd` for this reason.

## Degraded mode

No **Atlassian config** → Preflight asks for `site`; twg needs `email`/`apiToken` (or its own saved login). `<twg>` exit `127` → report missing "twg CLI". All other steps unchanged.
