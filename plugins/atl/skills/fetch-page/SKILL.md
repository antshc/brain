---
name: fetch-page
description: Fetch a Confluence page as Markdown from its identifier or URL, returning every long field in full. Use when asked to fetch, read, show, or summarize a Confluence page by ID or URL. No Atlassian config required.
argument-hint: '<page_id_or_url> (e.g. "123456789", "Fc1bBw", or "https://<site>.atlassian.net/wiki/spaces/<space>/pages/123456789/<title>")'
---

# Fetch Page

Return a Confluence **Page** as Markdown from its identifier or URL. MCP only — no API token.

## Workflow

**1 — Preflight.** Run `/preflight-atl` skill **Action: Resolve**.

**2 — Parse `{{input}}`.**
- `https://<site>/wiki/spaces/<space>/pages/<page_id>/<title>` → `<site>`, `<page_id>`.
- `https://<site>/wiki/x/<tiny_id>` → `<site>`, `<page_id> := <tiny_id>`.
- Bare `<page_id>` (numeric or tiny token) → no `<site>`; pass through as-is, `getConfluencePage` accepts either form.

**3 — Resolve `cloudId`.** `<site>` from URL → use it. Else Preflight's `cloudId`. Else `getAccessibleAtlassianResources` once, per Preflight's standing rule.

**4 — Fetch.** `getConfluencePage` with `cloudId`, `pageId: <page_id>`, `contentFormat: "adf"`.

**5 — Guard truncation.** Save the tool result to `content.json` and parse with Python — never `read_file`.

**6 — Convert.** Extract the ADF body (value under `body` matching `contentFormat: "adf"`); pipe it into `/map-markdown-adf` **Action: Convert ADF to Markdown**.

**7 — Return** only:
```
# <title>

<converted body Markdown>
```

## Degraded mode

No **Atlassian config** → `site`/`cloudId` empty; Step 3's `getAccessibleAtlassianResources` supplies `cloudId`. All other steps unchanged.
