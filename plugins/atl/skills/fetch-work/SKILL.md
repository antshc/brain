---
name: fetch-work
description: Fetch a Jira work item as Markdown from its key or URL, returning every long field in full. Use when asked to fetch, read, show, or summarize a Jira work item/issue by key or URL. No Atlassian config required.
argument-hint: '<work_item_key_or_url> (e.g. "PROJ-123" or "https://<site>.atlassian.net/browse/PROJ-123")'
---

# Fetch Work

Return a Jira **Work item** as Markdown from its key or URL. MCP only — no API token.

## Workflow

**1 — Preflight.** Run `/preflight-atl` **Action: Resolve**.

**2 — Parse `{{input}}`.**
- `https://<site>/browse/<key>` → `<site>`, `<key>`.
- Bare `<key>` → no `<site>`.

**3 — Resolve `cloudId`.** `<site>` from URL → use it. Else Preflight's `cloudId`. Else `getAccessibleAtlassianResources` once, per Preflight's standing rule.

**4 — Fetch.** `getJiraIssue` with `cloudId`, `issueIdOrKey: <key>`, `responseContentFormat: "adf"`. Omit `fields` — the default set already covers summary, description, status, issuetype, priority, labels, components, assignee, reporter, created, updated, resolution, project.

**5 — Guard truncation.** Save the tool result to `content.json` and parse with Python — never `read_file`.

**6 — Convert.** Extract `fields.description` (ADF); pipe it into `/map-markdown-adf` **Action: Convert ADF to Markdown**.

**7 — Return** only:
```
# <key> — <summary>
**Status:** <status> · **Type:** <issuetype> · **Assignee:** <assignee>

<converted description Markdown>
```

## Degraded mode

No **Atlassian config** → `site`/`cloudId` empty; Step 3's `getAccessibleAtlassianResources` supplies `cloudId`. All other steps unchanged.
