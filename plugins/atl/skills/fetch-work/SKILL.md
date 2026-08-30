---
name: fetch-work
description: Fetch a Jira work item as Markdown from its key or URL, returning every long field in full. Use when asked to fetch, read, show, or summarize a Jira work item/issue by key or URL. No Atlassian config required. Absorbs `fetch-jira`.
argument-hint: '<work_item_key_or_url> (e.g. "PROJ-123" or "https://<site>.atlassian.net/browse/PROJ-123")'
---

# Fetch Work

Return a Jira **Work item** as Markdown, from its key or URL, over the MCP alone — no `acli`, no API token.

## Workflow

**Step 1 — Preflight**
Run `/preflight-atl`' skill **Action: Resolve**.

**Step 2 — Parse the input**
Parse `{{input}}`:
- URL form `https://<site>/browse/<key>` → extract `<site>` and `<key>`.
- Bare key form `<key>` → `<site>` unknown.

**Step 3 — Resolve `cloudId`**
- `<site>` extracted from a URL → use it directly as `cloudId`.
- Else use Preflight's `cloudId`.
- Still empty → call `getAccessibleAtlassianResources` once and use the matching resource's `cloudId`, per Preflight's standing rule.

**Step 4 — Fetch**
Call `getJiraIssue` with `cloudId`, `issueIdOrKey: <key>`, `responseContentFormat: "adf"`. Omit `fields` — the tool's default set already covers summary, description, status, issuetype, priority, labels, components, assignee, reporter, created, updated, resolution, project.

**Step 5 — Guard against truncation**
Save the tool result to `content.json` and parse it with Python — never `read_file` — per Preflight's standing rule, so a long `description` is never silently truncated.

**Step 6 — Convert**
Extract `fields.description` (the ADF document). Run `/map-markdown-adf`' skill **Action: Convert ADF to Markdown**, piping the extracted document in.

**Step 7 — Compose and return**
Return only:
```
# <key> — <summary>
**Status:** <status> · **Type:** <issuetype> · **Assignee:** <assignee>

<converted description Markdown>
```

## Degraded mode

No **Atlassian config** file → Preflight's `site`/`cloudId` come back empty; Step 3's `getAccessibleAtlassianResources` fallback supplies `cloudId` instead. Every other step is unchanged.
