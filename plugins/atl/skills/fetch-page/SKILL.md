---
name: fetch-page
description: Fetch a Confluence page as Markdown from its identifier or URL, returning every long field in full. Use when asked to fetch, read, show, or summarize a Confluence page by ID or URL. No Atlassian config required; a page whose attachments are referenced from its body (diagrams, images, or files) caches them to a `.tmp` folder alongside the Markdown and references them in it when `ATLASSIAN_API_TOKEN` is configured.
argument-hint: '<page_id_or_url> (e.g. "123456789", "Fc1bBw", or "https://<site>.atlassian.net/wiki/spaces/<space>/pages/123456789/<title>")'
---

# Fetch Page

Return a Confluence **Page** as Markdown from its identifier or URL. MCP only for the page body itself — no API token required unless the page carries a `/publish-page`-rendered diagram, in which case restoring its mermaid source needs one.

## Prerequisites

- `atlassian-python-api` is installed once by `/init-atl` for the whole `atl` plugin — run that first if you haven't; this skill installs nothing of its own.
- Caching a page's attachments and restoring a diagram's mermaid source both need `ATLASSIAN_API_TOKEN` (in `.atlassian`), the same credential `/publish-page` uses to upload it. Without it, nothing is downloaded and each reference comes back as a placeholder note instead.

## Workflow

**1 — Preflight.** Run `/preflight-atl` skill **Action: Resolve**.

**2 — Parse `{{input}}`.**
- `https://<site>/wiki/spaces/<space>/pages/<page_id>/<title>` → `<site>`, `<page_id>`.
- `https://<site>/wiki/x/<tiny_id>` → `<site>`, `<page_id> := <tiny_id>`.
- Bare `<page_id>` (numeric or tiny token) → no `<site>`; pass through as-is, `getConfluencePage` accepts either form.

A `<site>` from the URL wins as `cloudId`; otherwise use Preflight's.

**3 — Fetch.** `getConfluencePage` with `cloudId`, `pageId: <page_id>`, `contentFormat: "adf"`. Guard truncation per Preflight's standing rule — the tool result (or your own save of it) lands at `content.json`; its title and ADF body live at `content.nodes[0].title` / `content.nodes[0].body`, a stable shape you never need to explore by hand.

**4 — Assemble.** One call does conversion, attachment caching, and placeholder resolution together:

```bash
python scripts/assemble_page.py --page-id <page_id> --root "$HARNESS_REPO_PATH" --md-path page.md < content.json
```

from this skill's directory. Writes `page.md` directly (add `--assets-dir <dir>` to override where attachments are cached; defaults to `page.md.tmp`, next to `page.md`). Internally: converts the ADF body via `/map-markdown-adf` **Action: Convert ADF to Markdown** (a Draw.io macro or a `media`/`mediaSingle`/`mediaGroup` node becomes a placeholder, never a raw error); then, only when a pure offline scan of the raw ADF body finds a node referencing an attached file, resolves it — no token configured → every placeholder becomes a note naming `ATLASSIAN_API_TOKEN`, nothing downloaded; token configured → every attachment on the page is cached to the assets dir, and each placeholder resolves per the rendering rules below. `page.md` already reads `# <title>\n\n<body Markdown>`.

**5 — Return** the contents of `page.md` unchanged.

## Attachment cache and rendering rules

Detection is a pure, offline, recursive scan of the raw ADF body — no REST call at all when it finds nothing, regardless of whether a token is configured — for any node shaped like:
- `type: "media"` with `attrs.type == "file"` (a generic attached file),
- `type: "media"` whose `attrs.alt` ends in an image extension (`.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.bmp`),
- `type: "extension"` whose `attrs.extensionKey` contains `"drawio"` (a Draw.io macro).

Only when the scan matches does every attachment on the page get downloaded and cached under the assets dir (`page.md.tmp/` by default, mirroring `/publish-page`'s own `<mdPath>.tmp/` convention — already covered by this repo's `*.tmp` gitignore pattern). Each placeholder then resolves by rule:
1. A `{stem}.source.mmd` sidecar is also attached (a `/publish-page`-rendered diagram) → the verbatim ```mermaid fence.
2. No sidecar, the file is an image → `![<alt or filename>](page.md.tmp/<file>)`. When the placeholder also carries Confluence's own reported `width`/`height` (see `/map-markdown-adf`'s mapping table — only ever present for an image, never a generic file), a `<!-- media-size: width=<w> height=<h> -->` comment follows on its own line right after, so a later `/publish-page` republish can carry the real size through instead of falling back to a fixed placeholder width.
3. No sidecar, not an image → a plain link `[<filename>](page.md.tmp/<file>)`.

The relative link is percent-encoded (spaces etc.) and always relative to `page.md`'s own directory. Rule 1 never adds a separate image reference alongside the fence — the mermaid source is the sole publishable artifact for a diagram; republishing via `/publish-page` regenerates its rendered image fresh. Rules 2/3's standalone reference lines are also what `/publish-page` re-uploads as a real attachment on republish — see its own SKILL.md.

## Degraded mode

No **Atlassian config** → `site`/`cloudId` empty; Preflight's Step 2 supplies `cloudId`. All other steps unchanged.

No **API token** with an attachment reference present → Step 4's no-token branch runs; the page's text and structure still return in full, with a note in place of each placeholder and no `.tmp` folder created.

A page whose raw ADF body has none of the three referenced-attachment shapes never touches the Confluence REST/attachment path at all, regardless of whether a token is configured.

A diagram published before the round-trip sidecar existed → its placeholder resolves to a note naming the missing `{name}.source.mmd` attachment instead of a fence; republish the page with `/publish-page` to enable the round-trip, then fetch again.

## Verification

`python -m pytest plugins/atl/skills/fetch-page/tests/` (from the repo root) — title/body extraction, the conversion handoff, offline attachment-reference detection, attachment caching, sidecar/image/file resolution (drawio and media-id, all three rendering rules), the no-sidecar and no-attachment notes, the `--md-path`/`--assets-dir` CLI wiring, and the no-credentials degraded path, all mocked. The ADF-to-placeholder seam is covered at its own home, `python -m pytest plugins/atl/skills/map-markdown-adf/`.
