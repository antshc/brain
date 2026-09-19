---
name: brief-daily
description: Report the current Jira user's blocked work items and open items where they're @mentioned in an unanswered comment, over a period defaulting to the last month. Use when asked for a daily briefing, standup update, or to show blocked or mentioned Jira items. Works against any connected Jira site — no project key or site configuration required.
argument-hint: '[period] (e.g. "2 weeks", "3 months"; default: 1 month)'
---

# Brief Daily

Two read-only Jira reports: work items blocked and assigned to the current user, and open items where the current user is `@mentioned` in a comment that looks unanswered. Output is chat markdown only — never writes to a file, never calls a Jira write tool.

## Workflow

**1 — Preflight.** Run `/preflight-atl` skill **Action: Resolve**.

**2 — Resolve identity.** Call `atlassianUserInfo` once and cache the returned `accountId` for the session — never take it from a file, a prior report, or ask the user to supply it.

**3 — Resolve site.** Preflight's `cloudId` non-empty → use it. Else `getAccessibleAtlassianResources` once, cached for the session, per Preflight's standing rule: exactly one resource → use it; more than one → ask the user which site, never assume one (the same Ambiguity rule Preflight applies to project key/space id, extended here to site choice).

**4 — Resolve period.** Parse `{{input}}`: empty → default `1 month`. Convert it into a JQL relative-date modifier for the coarse bound (`-1M` for the default; `"2 weeks"` → `-2w`; `"3 months"` → `-3M`) and into an absolute cutoff date for the precise per-comment filter in Step 6.

**5 — Query A: blocked items assigned to me.** `searchJiraIssuesUsingJql` with `cloudId`, `jql: 'assignee = currentUser() AND (status = "Blocked" OR flagged = Impediment) AND updated >= <cutoffJql> ORDER BY updated DESC'`, `maxResults: 10`. Render a table `Key | Summary | Type | Status | Priority | Updated`, each key linked to `https://<site>/browse/<key>`.
- **Fallback:** some Jira instances have no `"Blocked"` status literal and the clause errors — retry with `jql: 'flagged = Impediment AND updated >= <cutoffJql> ORDER BY updated DESC'`, `maxResults: 10`, note the dropped status clause in the report, and never fail the whole query over it.

**6 — Query B: unanswered mentions.**
- `searchJiraIssuesUsingJql` with `cloudId`, `jql: 'comment ~ "<accountId>" AND statusCategory != Done AND updated >= <cutoffJql> ORDER BY updated DESC'`, `maxResults: 10`. Search by the `accountId` resolved in Step 2, never display name — a display-name search both false-positives on comments the user authored and misses real `@mentions`.
- For each candidate, `getJiraIssue` with `cloudId`, `issueIdOrKey`, `fields: ["comment"]`, and read `fields.comment.comments`; keep only comments mentioning `accountId` created on or after the period cutoff — JQL has no comment-date operator, so this precise filter happens after fetch, never in the JQL.
- Apply the answered rule: a comment authored by `accountId` appearing after the mention → answered, drop it from the unanswered table. No such reply → list it as "possibly answered via emoji reaction" (reactions are invisible via the `comment` field) and ask the user to confirm — never assert unanswered on their behalf.
- **Closed-ticket cross-check.** Re-run the same `accountId` comment search restricted to `statusCategory = Done` over the same period cutoff, `jql: 'comment ~ "<accountId>" AND statusCategory = Done AND updated >= <cutoffJql> ORDER BY updated DESC'`, `maxResults: 10`, to surface "possibly incorrectly closed" candidates — report these separately, never folded into the main unanswered table.

**7 — Output.** Print both reports as chat markdown, headed by the resolved site, the resolved period, and today's date — never write to `daily.md` or any other file. Render Query B as an unanswered table (`Key | Summary | Status | Mentioned by | Mentioned on`), an "already answered" list, a "needs reaction confirmation" list, and a "possibly incorrectly closed" list. End by asking the user to confirm every "needs reaction confirmation" item.

## Gotchas

**Searching `comment ~ "<display name>"` false-positives on the user's own authored comments and misses real `@mentions`** — Jira indexes `@mentions` by `accountId`, not display name; always search by the `accountId` resolved in Step 2.

**JQL has no operator for "unanswered since mention"** — narrowing candidates via JQL only gets you the list; Step 6's per-comment fetch and manual timestamp/author check is what actually determines "unanswered."

**Comment emoji reactions are invisible via `getJiraIssue`'s `comment` field** — a mention can be acknowledged with a reaction and no reply ever appears in the thread; never assert a mention is unanswered without asking the user to confirm.

**Not every Jira workflow defines a `"Blocked"` status literal** — the clause can error outright rather than just return zero rows; Step 5's fallback drops it and retries with `flagged = Impediment` alone rather than failing the whole report.

## Degraded mode

No **Atlassian config** → Preflight's `cloudId` is empty; Step 3's `getAccessibleAtlassianResources` resolves it (asking when ambiguous). All other steps unchanged.
