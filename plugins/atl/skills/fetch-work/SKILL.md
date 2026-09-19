---
name: fetch-work
description: Fetch a Jira work item as Markdown from its key or URL, returning every long field in full. Use when asked to fetch, read, show, or summarize a Jira work item/issue by key or URL. No Atlassian config required.
argument-hint: '<work_item_key_or_url> (e.g. "PROJ-123" or "https://<site>.atlassian.net/browse/PROJ-123")'
---

# Fetch Work

Return a Jira **Work item** as Markdown from its key or URL. MCP only — no API token.

## Workflow

**1 — Preflight.** Run `/preflight-atl` skill **Action: Resolve**.

**2 — Parse `{{input}}`.**
- `https://<site>/browse/<key>` → `<site>`, `<key>`; `<site>` wins as `cloudId` over Preflight's.
- Bare `<key>` → use Preflight's `cloudId`.

**3 — Fetch.** `getJiraIssue` with `cloudId`, `issueIdOrKey: <key>`, `responseContentFormat: "adf"`. Omit `fields` — the default set already covers summary, description, status, issuetype, priority, labels, components, assignee, reporter, created, updated, resolution, project.

**4 — Guard truncation.** Save the tool result to `content.json` and read it with Python, per Preflight's standing rule.

**5 — Convert.** Extract `fields.description` (ADF); pipe it into `/map-markdown-adf` **Action: Convert ADF to Markdown**.

**6 — Return** only:
```
# <key> — <summary>
**Status:** <status> · **Type:** <issuetype> · **Assignee:** <assignee>

<converted description Markdown>
```

## Degraded mode

No **Atlassian config** → `site`/`cloudId` empty; Preflight's Step 2 supplies `cloudId`. All other steps unchanged.
