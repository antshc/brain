---
name: fetch-page
description: Fetch a Confluence page as Markdown from its ID, tiny ID, or URL, returning every long field in full. Use when asked to fetch, read, show, or summarize a Confluence page. No Atlassian config required; body-referenced attachments (diagrams, images, files) cache to `.md.assets` when `ATLASSIAN_API_TOKEN` is set — `--attachments` controls it.
argument-hint: '<page_id_or_url> (e.g. "123456789", "Fc1bBw", or "https://<site>.atlassian.net/wiki/spaces/<space>/pages/123456789/<title>")'
---

# Fetch Page

Return a Confluence **Page** as Markdown. MCP fetches the body; REST (token required) only for body-referenced attachments.

## Prerequisites

- `atlassian-python-api` installed by `init-atl`; run it first if missing. This skill installs nothing.
- Attachment caching and mermaid restore need `ATLASSIAN_API_TOKEN` (`apiToken` in `.atlassian.json.user`, see `preflight-atlassian`). Without it: no downloads; placeholders become notes.

## Workflow

1. **Preflight.** Run `preflight-atlassian` **Action: Resolve**; keep `configPath`.
2. **Parse `{{input}}`.** URL `<site>` wins as `cloudId`; else Preflight's.
   - `https://<site>/wiki/spaces/<space>/pages/<page_id>/<title>` → `<site>`, `<page_id>`.
   - `https://<site>/wiki/x/<tiny_id>` → `<site>`, `<page_id> := <tiny_id>`.
   - Bare numeric or tiny ID → `<page_id>` as-is.
3. **Fetch.** `getConfluencePage` with `cloudId`, `pageId: <page_id>`, `contentFormat: "adf"`. Guard truncation per Preflight; no matching MCP tool → REST fallback per Preflight. Result lands at `content.json` (title/body at `content.nodes[0].title` / `.body`; don't explore).
4. **Assemble** from this skill's base directory:
   ```bash
   python3 scripts/assemble_page.py --page-id <page_id> --config "<configPath>" --md-path page.md < content.json
   ```
   Optional: `--assets-dir <dir>` (default `page.md.assets`), `--attachments auto|skip|required`. Converts via `map-markdown-adf` **Action: Convert ADF to Markdown** (Draw.io, TOC, smart links, media → placeholders/links), caches attachments, resolves placeholders; writes `# <title>\n\n<body>`. Unsupported ADF → non-zero exit, `ADF conversion failed: <reason>` on stderr, no `page.md`.
5. **Return** `page.md` unchanged.

## Attachments

**Detection:** offline recursive scan of raw ADF; no match → no REST call regardless of token or mode. Matches:
- `media` with `attrs.type == "file"`;
- `media` with `attrs.alt` ending `.png|.jpg|.jpeg|.gif|.svg|.webp|.bmp`;
- `extension` with `attrs.extensionKey` containing `drawio`.

**Caching:** on match, list and download all page attachments once; stage in sibling dir, then atomically replace assets dir — failure never leaves a partial cache or damages a prior one. TLS verification always on.

**Placeholder resolution:**
1. `{stem}.source.mmd` sidecar attached → verbatim ```mermaid fence only, no image (`publish-page` re-renders).
2. Image, no sidecar → `![<alt or filename>](page.md.assets/<file>)`; if placeholder has `width`/`height`, add `<!-- media-size: width=<w> height=<h> -->` on the next line.
3. Other file → `[<filename>](page.md.assets/<file>)`.

Links percent-encoded, relative to `page.md`'s dir. `publish-page` re-uploads rule 2/3 references on republish.

## `--attachments` modes

- **`auto`** (default) — retrieve when credentials exist. No token → `set ATLASSIAN_API_TOKEN to restore it` note per placeholder, no assets dir. Listing/download/publish failure (TLS, timeout, HTTP, disk) → keep title/body; note with safe category only, e.g. `attachment retrieval failed (SSLError)` — **MUST NOT** include exception text (may hold signed URL/token).
- **`skip`** — no credential lookup, no REST; note `attachment retrieval skipped (--attachments skip)`.
- **`required`** — missing credentials, failure, or unresolvable placeholder → non-zero exit, `Attachment retrieval failed: <reason>` on stderr, no `page.md`.

## Degraded mode

- Diagram published before sidecars existed → note naming missing `{name}.source.mmd`; republish via `publish-page`, then refetch.

## Gotchas

- **MUST NOT** `find`/`grep`/`ls -R` to locate this skill's directory. Use the parent of this `SKILL.md`'s absolute path, already given in context.

## Verification

From repo root: `python3 -m pytest plugins/atl/skills/fetch-page/tests/`; ADF-to-placeholder seam: `python3 -m pytest plugins/atl/skills/map-markdown-adf/`.
