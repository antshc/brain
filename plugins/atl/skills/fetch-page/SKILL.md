---
name: fetch-page
description: Run when fetch the Confluence page. Fetch a Confluence page as Markdown from its identifier or URL, returning every long field in full. Use when asked to fetch, read, show, or summarize a Confluence page by ID or URL. No Atlassian config required; a page whose attachments are referenced from its body (diagrams, images, or files) caches them to a `.md.assets` folder alongside the Markdown and references them in it when `ATLASSIAN_API_TOKEN` is configured and retrieval succeeds — `--attachments` controls that behavior.
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
python3 scripts/assemble_page.py --page-id <page_id> --root "$HARNESS_REPO_PATH" --md-path page.md < content.json
```

from this skill's directory. Writes `page.md` directly (add `--assets-dir <dir>` to override where attachments are cached, default `page.md.assets`; add `--attachments auto|skip|required` to override the default retrieval policy — see below). Internally: converts the ADF body via `/map-markdown-adf` **Action: Convert ADF to Markdown** (a Draw.io macro, Confluence TOC macro, smart link, or `media`/`mediaSingle`/`mediaGroup` node becomes a placeholder or a normal link, never a raw error). A rejected conversion (a genuinely unsupported ADF construct) exits non-zero with `ADF conversion failed: <reason>` on stderr and never writes `--md-path` — no Python traceback, since the reason is already `/map-markdown-adf`'s own sanitized diagnostic. Only when a pure offline scan of the raw ADF body finds a node referencing an attached file does this step touch the Confluence REST/attachment path at all, and only per the `--attachments` policy below. `page.md` already reads `# <title>\n\n<body Markdown>`.

**5 — Return** the contents of `page.md` unchanged.

## Attachment cache and rendering rules

Detection is a pure, offline, recursive scan of the raw ADF body — no REST call at all when it finds nothing, regardless of whether a token is configured — for any node shaped like:
- `type: "media"` with `attrs.type == "file"` (a generic attached file),
- `type: "media"` whose `attrs.alt` ends in an image extension (`.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.bmp`),
- `type: "extension"` whose `attrs.extensionKey` contains `"drawio"` (a Draw.io macro).

Only when the scan matches does every attachment on the page get listed and downloaded, once (metadata and bytes are fetched a single time and reused for both caching and placeholder resolution), then published atomically to the assets dir (`page.md.assets/` by default): every download is staged in a sibling directory first, and only a fully-written staging directory ever replaces the live cache, so a failed refresh never leaves a partial cache and never damages a prior complete one. Each placeholder then resolves by rule:
1. A `{stem}.source.mmd` sidecar is also attached (a `/publish-page`-rendered diagram) → the verbatim ```mermaid fence.
2. No sidecar, the file is an image → `![<alt or filename>](page.md.assets/<file>)`. When the placeholder also carries Confluence's own reported `width`/`height` (see `/map-markdown-adf`'s mapping table — only ever present for an image, never a generic file), a `<!-- media-size: width=<w> height=<h> -->` comment follows on its own line right after, so a later `/publish-page` republish can carry the real size through instead of falling back to a fixed placeholder width.
3. No sidecar, not an image → a plain link `[<filename>](page.md.assets/<file>)`.

The relative link is percent-encoded (spaces etc.) and always relative to `page.md`'s own directory. Rule 1 never adds a separate image reference alongside the fence — the mermaid source is the sole publishable artifact for a diagram; republishing via `/publish-page` regenerates its rendered image fresh. Rules 2/3's standalone reference lines are also what `/publish-page` re-uploads as a real attachment on republish — see its own SKILL.md.

Attachment downloads always go over TLS with certificate verification enabled; this skill never disables it and never will, regardless of `--attachments` mode.

## Attachment retrieval policy (`--attachments`)

`assemble_page.py --attachments auto|skip|required` (default `auto`) controls what happens once the offline scan finds a reference:

- **`auto`** (default) — attempt retrieval when credentials exist; on any listing, download, or cache-publish failure (TLS, timeout, HTTP, or disk I/O), keep the page's title and converted body and replace each placeholder with a note naming only a safe failure category (e.g. `attachment retrieval failed (SSLError)`) — never the original exception text, which can carry a signed media URL or token.
- **`skip`** — make no credential lookup and no Confluence REST call at all; every placeholder becomes an `attachment retrieval skipped (--attachments skip)` note. Use this for a fast, fully offline fetch.
- **`required`** — treat missing credentials, retrieval/publish failure, or an attachment placeholder that cannot be resolved from the fetched metadata as fatal: `assemble_page.py` exits non-zero with `Attachment retrieval failed: <reason>` on stderr and never writes `--md-path`, so a caller never gets a silently incomplete page.

## Degraded mode

No **Atlassian config** → `site`/`cloudId` empty; Preflight's Step 2 supplies `cloudId`. All other steps unchanged.

No **API token** with an attachment reference present and `--attachments auto` (the default) → the page's text and structure still return in full, with a `set ATLASSIAN_API_TOKEN to restore it` note in place of each placeholder and no `.md.assets` folder created. This is distinct from a `skip`-mode note (retrieval was never attempted) and from an `auto`-mode retrieval-failure note (credentials existed but TLS, network, API, or disk I/O failed) — each names its own reason instead of always pointing at the token.

A page whose raw ADF body has none of the three referenced-attachment shapes never touches the Confluence REST/attachment path at all, regardless of credentials or `--attachments`.

A diagram published before the round-trip sidecar existed → its placeholder resolves to a note naming the missing `{name}.source.mmd` attachment instead of a fence; republish the page with `/publish-page` to enable the round-trip, then fetch again.

## Gotchas

**Never `find`/`grep`/`ls -R` the filesystem to locate this skill's own directory.** The tool/system context that told you this skill exists already gave you `fetch-page/SKILL.md`'s absolute path verbatim (it's how you're reading this). Take that literal path's parent directory directly (e.g. strip the trailing `/SKILL.md` yourself) — never rediscover it with a search rooted at `/`, `$HOME`, or any other unbounded root, even bounded by `-maxdepth`.

## Verification

`python3 -m pytest plugins/atl/skills/fetch-page/tests/` (from the repo root) — title/body extraction, the conversion handoff and its sanitized non-zero-exit failure path, offline attachment-reference detection, single-pass attachment listing/download, atomic cache publication (including preserving a prior complete cache on failure and leaving no partial staging directory), sidecar/image/file resolution (drawio and media-id, all three rendering rules), the no-sidecar and no-attachment notes, the `--md-path`/`--assets-dir`/`--attachments` CLI wiring, all three `--attachments` modes (including that `skip` makes no credential or REST call), TLS/timeout/listing/download/write failure paths and their redacted category-only notes, and a synthetic cross-skill fixture covering TOC, inline cards, lists, tables, and media — all mocked except the fixture, which runs the real CLI end to end. The ADF-to-placeholder seam is covered at its own home, `python3 -m pytest plugins/atl/skills/map-markdown-adf/`.
