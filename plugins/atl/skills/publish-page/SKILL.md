---
name: publish-page
description: Create or update a Confluence page from a local Markdown file, running one script that extracts diagrams, converts to ADF, uploads attachments, and publishes — over REST when diagrams are present or the body is large, over MCP otherwise. Use when asked to publish, create, or update a Confluence page from a markdown file.
argument-hint: '<md_file_path>, [pageId], [spaceId]'
---

# Publish Page

Create or update a Confluence **page** from a local Markdown file, via one `run` command that chains extract -> convert -> attach -> substitute -> publish. Text-only publishes go over the MCP when the body is small; a diagram-bearing publish always forces a REST publish, since attachment upload needs `atlassian-python-api` (an `ATLASSIAN_API_TOKEN`) regardless of body size.

## Prerequisites

- `pip install -r requirements.txt` (relative to this skill's directory) — needed for every REST-publish path (diagrams present, or a large diagram-free body).
- A diagram-bearing publish always goes REST, so for that branch `ATLASSIAN_API_TOKEN` (in `.atlassian`) and `mmdc` are **mandatory**, not optional:
  - `mmdc` on PATH: `npm install -g @mermaid-js/mermaid-cli` (npm, not pip); verify `mmdc --version`.
  - `mmdc` renders via headless Chrome (puppeteer), needing these shared libraries on Debian/Ubuntu (names shown for Ubuntu 24.04; older releases drop `t64`): `sudo apt-get update && sudo apt-get install -y libnspr4 libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2t64`.
- A diagram-free source needs none of this — it publishes over the MCP alone when small, or REST (still no `mmdc`) when large.

## Diagram renderer

`ATLASSIAN_DIAGRAM_RENDERER` in `.atlassian` selects how a mermaid fence reaches the page. Absent or empty → `png`.

| Value | Page output | Extra prerequisite | Status |
|---|---|---|---|
| `png` | Static image attached to the page | none beyond `mmdc` | Usable |
| `drawio` | Editable Confluence Draw.io diagram | Draw.io app, `drawio` CLI on PATH, `ATLASSIAN_DRAWIO_EXTENSION_KEY` | Usable |
| `mermaid` | Live Confluence Mermaid macro | Confluence Mermaid app | Refused — macro shape not yet captured |

`mmdc` is required for every value: it renders the image for `png` and validates the source for the other two. An unknown value, or a value whose macro shape is still uncaptured, fails **before** any page is created or updated — nothing is half-published. See `docs/ongoing/publish-page-diagram-renderers.md` for what the pending renderer still needs.

### `ATLASSIAN_DRAWIO_EXTENSION_KEY`

Required by `drawio` mode, and by nothing else. Format `<appId>/<envId>/static/drawio` — the app id and environment id differ per site and per install, so there is no default. To find yours, read a Confluence page that already carries a Draw.io diagram with `contentFormat: "adf"` and copy the diagram node's `attrs.extensionKey`. A missing or malformed key fails before any page is touched.

`drawio` mode publishes four objects per diagram: the `.drawio` attachment (the editable XML), the `.drawio.png` attachment (the preview), a custom content record of the app's own type, and the ADF extension node pointing at that record. Republishing looks the record up by page and diagram name first, so it bumps the existing one rather than stacking a duplicate.

The custom content record must name the page's **space** as well as its container, or the create fails with `Could not create content with type ac:com.mxgraph.confluence.plugins.diagramly:drawio-diagram`. `run` reads the space off the target page, so nothing extra is configured — but that failure text means the payload, not a missing app. To check the app really is installed, read `/rest/api/content/<pageId>/child` and look for the type among `_expandable`; the site-wide `GET /rest/api/content?type=<type>` answers `Cannot find custom content type` even on sites where the app works, so it proves nothing.

### Installing the Draw.io CLI

Only for `ATLASSIAN_DIAGRAM_RENDERER=drawio`. When `drawio --version` fails, run:

```bash
python plugins/atl/skills/publish-page/scripts/install_drawio.py
```

Unpacks the official AppImage into `~/.local/opt/drawio` and puts a wrapper at `~/.local/bin/drawio` — no root, no FUSE, stdlib only. Re-running is safe; it exits early when the version already matches. Pass a version (`install_drawio.py 31.4.5`) to pin one, or `--prefix`/`--bindir` to relocate.

The wrapper supplies `--no-sandbox --disable-gpu`, and falls back to `xvfb-run` when `DISPLAY` is unset — so a headless machine also needs `apt-get install -y xvfb`. The script verifies the Mermaid import before declaring success, so a green run means `drawio` can actually do the conversion this renderer needs.

## Confidentiality

Never print, log, quote, or publish `ATLASSIAN_SITE`, `ATLASSIAN_EMAIL`, or `ATLASSIAN_API_TOKEN` — not in page content, tool arguments, or output. `run` reads credentials from `.atlassian` itself; never pass them as CLI arguments.

## Inputs

- **mdPath** — required, path to the local Markdown file.
- **pageId** — optional; when named, update that page instead of creating one.
- **spaceId** — optional; resolved per Step 4 when omitted.
- **title** — optional; defaults to the Markdown's first `#` heading. The update path writes the resolved title too, so updating a page whose title differs from that heading **renames it** — pass the existing title to keep it.

## Workflow

**1 — Preflight.** Run `/preflight-atl` skill **Action: Resolve**.

**2 — Resolve `cloudId`.** Preflight's `cloudId`; still empty → `getAccessibleAtlassianResources` once, per Preflight's standing rule.

**3 — Resolve the publish target.**

`pageId` named → **update**, pass it as `--page-id`. Else → **create**, resolve `spaceId`: supplied → use it. Else Preflight's `defaultSpaceId` if non-empty, reported as resolved. Else `getConfluenceSpaces` with `limit: 10` — exactly one → use it and report it; more than one → ask, never choose silently (Preflight's Ambiguity rule). Pass it as `--space-id`.

**4 — Run the pipeline.** From the directory holding this `SKILL.md`:

```bash
python scripts/publish_page_diagrams.py run \
  --md-path <mdPath> \
  --page-id <pageId> | --space-id <spaceId> \
  --title <title, if named> \
  --root "$HARNESS_REPO_PATH"
```

One call does the rest: strips `<!-- confluence:ignore:start/end -->` spans, extracts ```mermaid fences into markers, converts the Markdown to ADF (shelling out to `/map-markdown-adf`'s CLI, never importing its code), and — depending on what's configured — either publishes directly via REST v2 or hands back an ADF ready for the MCP publish tools:

- Diagrams present and a token is configured → forces REST end to end: ensures the page exists (creating a placeholder when none was named), renders each diagram, uploads it as an attachment, substitutes every marker (at any nesting depth) for its media node, and publishes the final body.
- No diagrams, token configured → REST when the ADF body is over `--threshold-bytes` (default 50KB — the practical ceiling is what an agent can safely inline into an MCP tool argument, not Confluence/MCP transport), otherwise MCP handback.
- No token → substitutes every marker for a note naming `ATLASSIAN_API_TOKEN` as the missing prerequisite when diagrams are present, then always hands back to MCP (REST needs the same token, so it can't cover this case either).

Failure framing: `mmdc` missing on the REST/diagram path exits non-zero naming `mmdc`, and `drawio` missing in `drawio` mode exits non-zero naming `drawio`; an unsupported or not-yet-usable `ATLASSIAN_DIAGRAM_RENDERER`, or `drawio` mode without `ATLASSIAN_DRAWIO_EXTENSION_KEY`, exits non-zero naming the renderer or the key, before any page is touched; a leftover marker after substitution exits non-zero naming it — fix and re-run rather than working around it.

Rendered `.mmd`/`.png`/`.drawio` files and the final ADF default to `<mdPath>.tmp/` beside the source (suffix included, e.g. `docs/design.md` → `docs/design.md.tmp/`, holding `final-adf.json`). Override with `--assets-dir` and `--out`.

Prints one JSON result to stdout:
- `{"method":"rest","pageId":...,"title":...,"sizeBytes":...,"diagrams":N,"attachments":N,"renderer":...,"adfPath":...}` — already published; nothing left to do but report.
- `{"method":"mcp","adfPath":...,"sizeBytes":...,"pageId":...,"spaceId":...,"title":...,"diagramsRendered":0,"renderer":...,"missingPrerequisite":"ATLASSIAN_API_TOKEN"}` (the `missingPrerequisite` key is present only when diagrams were substituted for notes) — proceed to Step 5.

**5 — When `run` returns `method: mcp`.** Read the ADF from `adfPath` (always written pretty-printed, `json.dump(..., indent=2)`, for exactly the reason below) and publish it:

- Update case → `updateConfluencePage` with `cloudId`, `pageId`, `body`, `contentFormat: "adf"`, `title` (if changed).
- Create case → `createConfluencePage` with `cloudId`, `spaceId`, `title`, `body`, `contentFormat: "adf"`.

**The `body` argument MUST be the literal stringified ADF JSON, never a file reference** — passing something like `{"adf_file": "/tmp/final_adf.json"}` fails with an opaque 400. Correct: read `adfPath`'s contents, then pass that string as `body`. Incorrect: `{"body": {"adf_file": "/tmp/final_adf.json"}}`.

`adfPath`'s minified-equivalent content can be one very long line if read the wrong way — `read_file` truncates a single line at roughly 2000 characters, so a naive read can silently lose content. `run` writes `--out` pretty-printed (one node per line) for exactly this reason; read the whole file rather than assuming a single-line body.

**Escape hatch:** if the ADF body still can't be safely inlined into an MCP tool call, re-run `run` with `--threshold-bytes 0` to force a REST publish instead.

Report the page URL from the tool result and, when diagrams were rendered, confirm both the page and its attachment list show every image.

## Rules

- Never rephrase Markdown content — `map-markdown-adf` handles structure.
- A named `pageId` is always updated in place; a page is created only when none is named.
- Never choose a space silently.
- Non-```mermaid diagram formats and bulk publishing are out of scope.
- Verifying a publish MUST use a read-only call (e.g. fetching the page back) — never re-run `updateConfluencePage`/`createConfluencePage` with placeholder or test content just to check the result, which would overwrite the real publish.

## Degraded mode

- No **Atlassian config** → `cloudId`/`defaultSpaceId` empty; Step 2's `getAccessibleAtlassianResources` resolves `cloudId`, Step 3's space-visibility lookup resolves `spaceId` (asking when ambiguous). A diagram-free source publishes identically to full configuration.
- No **API token** with diagrams present → `run`'s no-token branch runs; text still publishes over MCP and the result names the unrendered diagrams' missing prerequisite.
- Token configured but `mmdc` missing → `run` exits non-zero naming `mmdc`; nothing is published (re-run once `mmdc` is installed).
- `ATLASSIAN_DIAGRAM_RENDERER=drawio` with `drawio` missing or `ATLASSIAN_DRAWIO_EXTENSION_KEY` unset → `run` exits non-zero naming the missing one; nothing is published.
- `ATLASSIAN_DIAGRAM_RENDERER` set to `mermaid` → `run` exits non-zero naming the renderer and the capture it still needs; nothing is published. Set the key to `png` or `drawio` to publish now.

## Other subcommands

`extract`, `render-attach`, `substitute-media`, `publish-adf`, and `combine` are the pipeline steps `run` chains together; each stays independently invokable for the MCP/degraded fallback above or ad-hoc use — see `python scripts/publish_page_diagrams.py --help` and each subcommand's own `--help`. `replace-markers` is a legacy, top-level-only back-compat alias for `substitute-media`. `render-attach` ends in a media-id map, which only `png` output fits, so it refuses the macro renderers and points at `run`.

## Verification

`python -m pytest plugins/atl/skills/publish-page/` (from the repo root) — the full pipeline: extraction, conversion hand-off, attachment upload, marker substitution, and REST/MCP branching, all mocked. Conversion itself is covered at its own seam, `python -m pytest plugins/atl/skills/map-markdown-adf/`. When verifying a live publish via `getConfluencePage`, request `body-format: atlas_doc_format` and check the returned body for `"type": "media"` node occurrences matching the diagram count — in `drawio` mode count `"type": "extension"` nodes carrying `static/drawio` instead, and expect two attachments (`.drawio` + `.drawio.png`) per diagram. Confirm the actual response shape empirically before asserting specific top-level keys (e.g. `title`/`version`) you haven't verified against the live MCP tool. Raw REST probes go through `<site>/wiki/...` — `site_url()` returns the bare site, and only `atlassian-python-api` adds the `/wiki` prefix, so a hand-rolled `requests` call without it 404s with `No endpoint POST /rest/api/content`. The MCP-only publish path and token-free degradation are verified manually against this skill's acceptance criteria — MCP transport and this prose are deliberately untested.

