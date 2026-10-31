---
name: fetch-page
description: >-
  Fetch a Confluence page as Markdown from its ID, tiny ID, or URL, returning every long field in full. Use when asked to fetch, read, show, or summarize a Confluence page. Reads real ADF over REST and converts via map-markdown-adf; body-referenced attachments (diagrams, images, files) cache to `.md.assets`, `--attachments` controls it; inline-comment anchors and a `## Comments` section keep comments through republish. Needs `apiToken` in `.atlassian.json.user`.
argument-hint: '<page_id_or_url> (e.g. "123456789", "Fc1bBw", or "https://<site>.atlassian.net/wiki/spaces/<space>/pages/123456789/<title>")'
---

# Fetch Page

Return a Confluence **Page** as Markdown. REST reads the real ADF body, attachments, and comments; *`map-markdown-adf` skill converts ADF back to Markdown, preserving source wording verbatim*. Not twg: its Markdown export drops `map-markdown-adf` constructs and comment anchors.

## Prerequisites

- `atlassian-python-api` installed by `init-atl` skill; if missing, *run `init-atl` skill for first-run setup of `.atlassian.json.user` and Atlassian dependencies* first. This skill installs nothing.
- `cloudId`, `email`, `apiToken` in `.atlassian.json.user` (see `preflight-atlassian` skill). Missing → script exits non-zero naming them; report and stop.

## Workflow

1. **Preflight.** *Run `preflight-atlassian` skill to resolve site, credentialed twg command, and token availability from `.atlassian.json.user` config* **Action: Resolve**; keep `configPath`, `site`, `twg`.
2. **Parse `{{input}}`.** URL `<site>` differing from Preflight `site` → pass `--site https://<site>`.
   - `https://<site>/wiki/spaces/<space>/pages/<page_id>/<title>` → `<page_id>`.
   - Bare numeric ID → `<page_id>` as-is.
   - Tiny link `https://<site>/wiki/x/<tiny_id>`, or bare tiny ID → URL `<site>/wiki/x/<tiny_id>`; resolve with `<twg> confluence content get <url> --detail summary -o json --output-file tiny.json` → `<page_id> := data.id`.
3. **Fetch and assemble** from this skill's base directory:
   ```bash
   python3 scripts/assemble_page.py --page-id <page_id> --config "<configPath>" --md-path page.md [--site https://<site>]
   ```
   Fetches title + ADF over REST v2 (`body-format=atlas_doc_format`). Optional: `--assets-dir <dir>` (default `page.md.assets`), `--attachments auto|skip|required`, `--comments auto|skip`. Converts via *`map-markdown-adf` skill to convert Atlassian Document Format (ADF) back to Markdown, preserving source wording verbatim* **Action: Convert ADF to Markdown** (Draw.io, TOC, smart links, media → placeholders/links), caches attachments, resolves placeholders; writes `# <title>\n\n<body>`. Unsupported ADF → non-zero exit, `ADF conversion failed: <reason>` on stderr, no `page.md`. REST failure → `Page fetch failed: <category>`, no `page.md`.
4. **Return** `page.md` unchanged.

Non-zero exit → report stderr; **MUST NOT** run `wc`/`cat` on the missing `page.md` or retry with edited ADF.

## Attachments

**Detection:** offline recursive scan of raw ADF; no match → no attachment call regardless of mode. Matches:
- `media` with `attrs.type == "file"`;
- `media` with `attrs.alt` ending `.png|.jpg|.jpeg|.gif|.svg|.webp|.bmp`;
- `extension` with `attrs.extensionKey` containing `drawio`.

**Caching:** on match, list and download all page attachments once; stage in sibling dir, then atomically replace assets dir — failure never leaves a partial cache or damages a prior one. TLS verification always on.

**Placeholder resolution:**
1. `{stem}.source.mmd` sidecar attached → verbatim ```mermaid fence only, no image (`publish-page` skill re-renders).
2. Image, no sidecar → `![<alt or filename>](page.md.assets/<file>)`; if placeholder has `width`/`height`, add `<!-- media-size: width=<w> height=<h> -->` on the next line.
3. Other file → `[<filename>](page.md.assets/<file>)`.

Links percent-encoded, relative to `page.md`'s dir. `publish-page` skill re-uploads rule 2/3 references on republish.

## `--attachments` modes

- **`auto`** (default) — retrieve. Listing/download/publish failure (TLS, timeout, HTTP, disk) → keep title/body; note with safe category only, e.g. `attachment retrieval failed (SSLError)` — **MUST NOT** include exception text (may hold signed URL/token).
- **`skip`** — no attachment REST call; note `attachment retrieval skipped (--attachments skip)`.
- **`required`** — failure or unresolvable placeholder → non-zero exit, `Attachment retrieval failed: <reason>` on stderr, no `page.md`.

## Comments

- Body inline comments arrive as `<!-- adf:comment id="<id>" -->text<!-- /adf:comment -->` spans (via `map-markdown-adf` skill); they keep comments attached when `publish-page` skill republishes.
- **`--comments auto`** (default): appends `## Comments` inside `<!-- adf:ignore:start/end -->` — each inline/footer thread with author, date, plain-text body, replies, Confluence link; inline threads say whether their id is anchored in the body.
- REST failure → note with safe category only, e.g. `comment retrieval failed (ConnectionError)`; `page.md` still written.
- **`--comments skip`** — no lookup.

## Degraded mode

- Diagram published before sidecars existed → note naming missing `{name}.source.mmd`; *republish via `publish-page` skill to update the Confluence page from Markdown*, then refetch.

## Gotchas

- **MUST NOT** `find`/`grep`/`ls -R` to locate this skill's directory. Use the parent of this `SKILL.md`'s absolute path, already given in context.
