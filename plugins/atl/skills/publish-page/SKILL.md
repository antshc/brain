---
name: publish-page
description: Create or update a Confluence page from a local Markdown file, running one script that extracts diagrams, converts to ADF, uploads attachments, and publishes — over REST when diagrams are present or the body is large, over MCP otherwise. Use when asked to publish, create, or update a Confluence page from a markdown file.
argument-hint: '<md_file_path>, [pageId], [spaceId]'
---

# Publish Page

Publish local Markdown to a Confluence page via one `run` command: extract → convert → attach → substitute → publish. Diagrams or local attachments → always REST (upload needs token). Otherwise small body → MCP, large → REST.

## Prerequisites

- `atlassian-python-api` — installed by `init-atl`; run it first. Needed by every REST path.
- Diagrams or local attachments → **MUST** have `apiToken` configured in `.atlassian.json.user`.
- Diagram present → **MUST** have `mmdc` on PATH: `npm install -g @mermaid-js/mermaid-cli`; verify `mmdc --version`. Headless Chrome libs (Ubuntu 24.04; older releases drop `t64`): `sudo apt-get update && sudo apt-get install -y libnspr4 libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2t64`.
- Diagram-free source: small → MCP only; large → REST, no `mmdc`.

## Diagram renderer

`diagramRenderer` in `.atlassian.json.user` (see `preflight-atlassian`). Absent/empty → `png`.

| Value | Page output | Extra prerequisite | Status |
|---|---|---|---|
| `png` | Static image attached to the page | none beyond `mmdc` | Usable |
| `drawio` | Editable Confluence Draw.io diagram | Draw.io app, `drawio` CLI on PATH, `drawioExtensionKey` | Usable |
| `mermaid` | Live Confluence Mermaid macro | Confluence Mermaid app | Refused — macro shape not yet captured |

`mmdc` required for every value: renders `png`, validates source for others. Unknown or uncaptured value fails before any page is touched. Pending renderer work: `docs/ongoing/publish-page-diagram-renderers.md`.

### `drawioExtensionKey`

`drawio` mode only. Format `<appId>/<envId>/static/drawio`; per site/install, no default. Find it: read a page already holding a Draw.io diagram with `contentFormat: "adf"`, copy the node's `attrs.extensionKey`. Missing/malformed → fails before any page is touched.

Per diagram `drawio` publishes: `.drawio` attachment (editable XML), `.drawio.png` preview, app custom content record, ADF extension node. Republish finds the record by page + diagram name and bumps it.

Draw.io's bundled older Mermaid rejects some types (e.g. `swimlane-beta`). Failed or empty-canvas import → that diagram alone falls back to `png` with stderr warning; others stay editable. New rejected types need no code change.

Error `Could not create content with type ac:com.mxgraph.confluence.plugins.diagramly:drawio-diagram` → payload lacks page **space**, not missing app (`run` reads space from target page). Check app installed via `/rest/api/content/<pageId>/child` → type in `_expandable`. Ignore `GET /rest/api/content?type=<type>`: answers `Cannot find custom content type` even when app works.

### Installing the Draw.io CLI

`drawio` mode only, when `drawio --version` fails. From this skill's directory (see Gotchas):

```bash
python scripts/install_drawio.py
```

Installs to `~/.local/opt/drawio` + wrapper `~/.local/bin/drawio`; no root/FUSE. Idempotent. Optional: version arg (`install_drawio.py 31.4.5`), `--prefix`, `--bindir`. No `DISPLAY` → wrapper uses `xvfb-run`; install `apt-get install -y xvfb`. Green run = Mermaid import verified.

## Diagram ids

`%% diagram-id: <id>` gives a mermaid fence stable identity: `[a-z0-9-]`, unique per file, after any `---` frontmatter or `%%{init: …}%%`, directly above the diagram-type line. Id = attachment filename + Draw.io record title → republish replaces in place despite reorders or heading edits. `run` strips the line before rendering. Emitted by `doc-architecture-diagram`, `doc-behavior-diagram`, `doc-code-diagram`.

No id → `{index}-{nearest-heading-slug}` naming; reorder or heading rewording → next publish adds a duplicate.

Ids are permanent: rename/delete orphans the attachment and record (`run` never deletes). Prune manually in Confluence.

### Round-trip sidecar

`png`/`drawio` also attach `{name}.source.mmd` (fence verbatim, id line included); `fetch-page` uses it to restore the ```` ```mermaid ```` block. `mermaid` mode skips it. Never read on publish; mirrors last `run`, not Confluence-side edits.

## Confidentiality

**MUST NOT** print, log, quote, or publish `site`, `email`, `apiToken` (the `.atlassian.json.user` credential fields) in page content, tool args, or output. `run` reads `.atlassian.json.user` itself; never pass credentials as CLI args.

## Inputs

- **mdPath** — required; local Markdown path.
- **pageId** — optional; update that page instead of creating.
- **spaceId** — optional; resolved in Step 2.
- **title** — optional; defaults to first `#` heading. Update writes title too → differing heading **renames** page; pass existing title to keep it.

## Workflow

**1 — Preflight.** Run `preflight-atlassian` **Action: Resolve**; keep `cloudId`, `configPath`.

**2 — Resolve target.** `pageId` → update, `--page-id`. Else create, `--space-id` from first hit: supplied `spaceId` → Preflight `defaultSpaceId` (report) → `getConfluenceSpaces` `limit: 10`: one → use, report; several → ask (Preflight Ambiguity rule).

**3 — Run.** From this skill's directory (see Gotchas):

```bash
python scripts/publish_page_diagrams.py run \
  --md-path <mdPath> \
  --page-id <pageId> | --space-id <spaceId> \
  --title <title, if named> \
  --config "<configPath>"
```

Pipeline: strip `<!-- adf:ignore:start/end -->` spans; replace ```mermaid fences and standalone local image/file refs (as `fetch-page` writes) with markers; convert via `map-markdown-adf` CLI (never import its code); then:

- Diagrams/local attachments + token → REST: ensure page (placeholder when creating), render, upload, substitute markers at any depth (image → `mediaSingle`, filename as `alt`, `fetch-page`-recorded `width`/`height` when present; other file → `mediaGroup`), publish.
- Neither + token → REST if ADF > `--threshold-bytes` (default 50KB = safe MCP-inline size), else MCP handback.
- No token → markers become notes naming `apiToken`; always MCP handback.

Exits non-zero naming the cause on: missing `mmdc` (diagram path) or `drawio` (`drawio` mode); unsupported/unusable `diagramRenderer`; missing `drawioExtensionKey`; duplicate `%% diagram-id`; leftover marker after substitution. All but the last fail before any page is touched. Fix and re-run; don't work around.

Outputs default to `<mdPath>.tmp/` (e.g. `docs/design.md.tmp/final-adf.json`); override with `--assets-dir`, `--out`.

Stdout JSON:
- `{"method":"rest","pageId":...,"title":...,"sizeBytes":...,"diagrams":N,"attachments":N,"renderer":...,"adfPath":...}` → published; report.
- `{"method":"mcp","adfPath":...,"sizeBytes":...,"pageId":...,"spaceId":...,"title":...,"diagramsRendered":0,"renderer":...,"missingPrerequisite":"apiToken"}` → Step 4. `missingPrerequisite` only when diagrams became notes.

**4 — MCP handback.** Read the whole `adfPath` file (pretty-printed so line-truncating reads lose nothing), then:

- Update → `updateConfluencePage`: `cloudId`, `pageId`, `body`, `contentFormat: "adf"`, `title` if changed.
- Create → `createConfluencePage`: `cloudId`, `spaceId`, `title`, `body`, `contentFormat: "adf"`.

**`body` MUST be the literal stringified ADF JSON**, never a file reference (`{"adf_file": ...}` → opaque 400).

Body too large to inline, or no matching MCP tool found for Step 4 → re-run with `--threshold-bytes 0` (forces REST for the whole publish, skipping Step 4).

Report page URL; with diagrams, confirm page and attachment list show every image.

## Rules

- Never rephrase Markdown; `map-markdown-adf` handles structure.
- Named `pageId` → update in place; create only when none named.
- Never choose a space silently.
- Out of scope: non-mermaid diagram formats, bulk publishing.
- Verify publish read-only (fetch page back); **MUST NOT** re-run `updateConfluencePage`/`createConfluencePage` with test content — overwrites real publish.

## Degraded mode

- No Atlassian config → Preflight resolves `cloudId`, Step 2 resolves `spaceId`; diagram-free source publishes normally.
- No token + diagrams → text publishes via MCP; result names missing prerequisite.
- Any Step 3 failure → nothing published; fix and re-run. `diagramRenderer=mermaid` → switch to `png` or `drawio` to publish now.

## Gotchas

**MUST NOT `find`/`grep`/`ls -R` to locate this skill's directory.** Take the parent of the `SKILL.md` path you loaded this from; scripts live in its `scripts/`.

## Other subcommands

`extract`, `render-attach`, `substitute-media`, `publish-adf`, `combine` = steps `run` chains; each invokable alone for fallback or ad-hoc use (`--help`). `replace-markers` = legacy top-level-only alias for `substitute-media`. `render-attach` supports `png` only; refuses macro renderers, points at `run`.

## Verification

- Unit: `python -m pytest plugins/atl/skills/publish-page/` from repo root (pipeline, mocked); conversion: `python -m pytest plugins/atl/skills/map-markdown-adf/`.
- Live: `getConfluencePage` with `body-format: atlas_doc_format`. `png` → `"type": "media"` count = diagram count; 2 attachments per diagram (`.png`, `.source.mmd`). `drawio` → count `"type": "extension"` with `static/drawio`; 3 attachments per diagram (`.drawio`, `.drawio.png`, `.source.mmd`).
- Confirm MCP response shape empirically before asserting top-level keys (e.g. `title`/`version`).
- Raw REST probes MUST use `<site>/wiki/...`; `site_url()` returns bare site, only `atlassian-python-api` adds `/wiki` (else 404 `No endpoint POST /rest/api/content`).
- MCP-only path and token-free degradation: manual verification only.

