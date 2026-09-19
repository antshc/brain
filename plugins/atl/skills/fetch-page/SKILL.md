---
name: fetch-page
description: Fetch a Confluence page as Markdown from its identifier or URL, returning every long field in full. Use when asked to fetch, read, show, or summarize a Confluence page by ID or URL. No Atlassian config required; a page carrying `/publish-page` diagrams restores their mermaid source when `ATLASSIAN_API_TOKEN` is configured.
argument-hint: '<page_id_or_url> (e.g. "123456789", "Fc1bBw", or "https://<site>.atlassian.net/wiki/spaces/<space>/pages/123456789/<title>")'
---

# Fetch Page

Return a Confluence **Page** as Markdown from its identifier or URL. MCP only for the page body itself — no API token required unless the page carries a `/publish-page`-rendered diagram, in which case restoring its mermaid source needs one.

## Prerequisites

- `pip install -r requirements.txt` (relative to this skill's directory) — needed only when a fetched page turns out to carry a diagram; a diagram-free page never touches it.
- Restoring a diagram's mermaid source needs `ATLASSIAN_API_TOKEN` (in `.atlassian`), the same credential `/publish-page` uses to upload it. Without it, the diagram comes back as a placeholder note instead of a ```mermaid fence.

## Workflow

**1 — Preflight.** Run `/preflight-atl` skill **Action: Resolve**.

**2 — Parse `{{input}}`.**
- `https://<site>/wiki/spaces/<space>/pages/<page_id>/<title>` → `<site>`, `<page_id>`.
- `https://<site>/wiki/x/<tiny_id>` → `<site>`, `<page_id> := <tiny_id>`.
- Bare `<page_id>` (numeric or tiny token) → no `<site>`; pass through as-is, `getConfluencePage` accepts either form.

A `<site>` from the URL wins as `cloudId`; otherwise use Preflight's.

**3 — Fetch.** `getConfluencePage` with `cloudId`, `pageId: <page_id>`, `contentFormat: "adf"`. Guard truncation per Preflight's standing rule — the tool result (or your own save of it) lands at `content.json`; its title and ADF body live at `content.nodes[0].title` / `content.nodes[0].body`, a stable shape you never need to explore by hand.

**4 — Assemble.** One call does conversion and diagram restoration together:

```bash
python scripts/assemble_page.py --page-id <page_id> --root "$HARNESS_REPO_PATH" < content.json > page.md
```

from this skill's directory. Internally: converts the ADF body via `/map-markdown-adf` **Action: Convert ADF to Markdown** (a Draw.io or attached-image diagram becomes a `<!-- adf:diagram ... -->` placeholder, never a raw error); then, only when a placeholder survives conversion, resolves it — no token configured → every placeholder becomes a note naming `ATLASSIAN_API_TOKEN`, nothing downloaded, `requirements.txt` not needed; token configured → each placeholder resolves to its `{name}.source.mmd` sidecar and is replaced with the verbatim ```mermaid fence `/publish-page` originally rendered, or a note naming a missing sidecar instead of failing the fetch. A diagram-free page never touches the Confluence REST/attachment path at all. `page.md` already reads `# <title>\n\n<body Markdown>`.

**5 — Return** the contents of `page.md` unchanged.

## Degraded mode

No **Atlassian config** → `site`/`cloudId` empty; Preflight's Step 2 supplies `cloudId`. All other steps unchanged.

No **API token** with a diagram present → Step 4's no-token branch runs; the page's text and structure still return in full, with a note in place of each diagram's mermaid source.

A diagram published before the round-trip sidecar existed → its placeholder resolves to a note naming the missing `{name}.source.mmd` attachment instead of a fence; republish the page with `/publish-page` to enable the round-trip, then fetch again.

## Verification

`python -m pytest plugins/atl/skills/fetch-page/tests/` (from the repo root) — title/body extraction, the conversion handoff, placeholder detection, sidecar resolution (drawio and media-id), the no-sidecar and no-attachment notes, and the no-credentials degraded path, all mocked. The ADF-to-placeholder seam is covered at its own home, `python -m pytest plugins/atl/skills/map-markdown-adf/`.
