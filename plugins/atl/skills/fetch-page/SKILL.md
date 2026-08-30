---
name: fetch-page
description: Fetch a Confluence page as Markdown from its identifier or URL, returning every long field in full. Use when asked to fetch, read, show, or summarize a Confluence page by ID or URL. No Atlassian config required. Absorbs `fetch-conf`.
argument-hint: '<page_id_or_url> (e.g. "123456789", "Fc1bBw", or "https://<site>.atlassian.net/wiki/spaces/<space>/pages/123456789/<title>")'
---

# Fetch Page

Return a Confluence **Page** as Markdown, from its identifier or URL, over the MCP alone — no `acli`, no API token.

## Workflow

**Step 1 — Preflight**
Run `/preflight-atl`' skill **Action: Resolve**.

**Step 2 — Parse the input**
Parse `{{input}}`:
- Full-path URL form `https://<site>/wiki/spaces/<space>/pages/<page_id>/<title>` → extract `<site>` and `<page_id>`.
- Tiny-link URL form `https://<site>/wiki/x/<tiny_id>` → extract `<site>` and `<tiny_id>` as `<page_id>`.
- Bare identifier form `<page_id>` (numeric ID or tiny-link token) → `<site>` unknown; pass it straight through — `getConfluencePage`'s `pageId` accepts either form.

**Step 3 — Resolve `cloudId`**
- `<site>` extracted from a URL → use it directly as `cloudId`.
- Else use Preflight's `cloudId`.
- Still empty → call `getAccessibleAtlassianResources` once and use the matching resource's `cloudId`, per Preflight's standing rule.

**Step 4 — Fetch**
Call `getConfluencePage` with `cloudId`, `pageId: <page_id>`, `contentFormat: "adf"`.

**Step 5 — Guard against truncation**
Save the tool result to `content.json` and parse it with Python — never `read_file` — per Preflight's standing rule, so a long body is never silently truncated.

**Step 6 — Convert**
Extract the page body's ADF document from the tool result (the value under `body` matching `contentFormat: "adf"`). Run `/map-markdown-adf`' skill **Action: Convert ADF to Markdown**, piping the extracted document in.

**Step 7 — Compose and return**
Return only:
```
# <title>

<converted body Markdown>
```

## Degraded mode

No **Atlassian config** file → Preflight's `site`/`cloudId` come back empty; Step 3's `getAccessibleAtlassianResources` fallback supplies `cloudId` instead. Every other step is unchanged.
