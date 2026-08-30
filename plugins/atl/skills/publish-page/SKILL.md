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

## Confidentiality

Never print, log, quote, or publish `ATLASSIAN_SITE`, `ATLASSIAN_EMAIL`, or `ATLASSIAN_API_TOKEN` — not in page content, tool arguments, or output. `run` reads credentials from `.atlassian` itself; never pass them as CLI arguments.

## Inputs

- **mdPath** — required, path to the local Markdown file.
- **pageId** — optional; when named, update that page instead of creating one.
- **spaceId** — optional; resolved per Step 4 when omitted.
- **title** — optional; defaults to the Markdown's first `#` heading.

## Workflow

**1 — Preflight.** Run `/preflight-atl` **Action: Resolve**.

**2 — Resolve `cloudId`.** Preflight's `cloudId`; still empty → `getAccessibleAtlassianResources` once, per Preflight's standing rule.

**3 — Resolve the publish target.**

`pageId` named → **update**, pass it as `--page-id`. Else → **create**, resolve `spaceId`: supplied → use it. Else Preflight's `defaultSpaceId` if non-empty, reported as resolved. Else `getConfluenceSpaces` with `limit: 10` — exactly one → use it and report it; more than one → ask, never choose silently (Preflight's Ambiguity rule). Pass it as `--space-id`.

**4 — Run the pipeline.** From the directory holding this `SKILL.md`:

```bash
python3 scripts/publish_page_diagrams.py run \
  --md-path <mdPath> \
  --page-id <pageId> | --space-id <spaceId> \
  --title <title, if named> \
  --root "$HARNESS_REPO_PATH" \
  --out <path to a final-ADF output file>
```

One call does the rest: strips `<!-- confluence:ignore:start/end -->` spans, extracts ```mermaid fences into markers, converts the Markdown to ADF (shelling out to `/map-markdown-adf`'s CLI, never importing its code), and — depending on what's configured — either publishes directly via REST v2 or hands back an ADF ready for the MCP publish tools:

- Diagrams present and a token is configured → forces REST end to end: ensures the page exists (creating a placeholder when none was named), renders each diagram, uploads it as an attachment, substitutes every marker (at any nesting depth) for its media node, and publishes the final body.
- No diagrams, token configured → REST when the ADF body is over `--threshold-bytes` (default 50KB — the practical ceiling is what an agent can safely inline into an MCP tool argument, not Confluence/MCP transport), otherwise MCP handback.
- No token → substitutes every marker for a note naming `ATLASSIAN_API_TOKEN` as the missing prerequisite when diagrams are present, then always hands back to MCP (REST needs the same token, so it can't cover this case either).

Failure framing: `mmdc` missing on the REST/diagram path exits non-zero naming `mmdc`; a leftover marker after substitution exits non-zero naming it — fix and re-run rather than working around it.

Prints one JSON result to stdout:
- `{"method":"rest","pageId":...,"title":...,"sizeBytes":...,"diagrams":N,"attachments":N,"adfPath":...}` — already published; nothing left to do but report.
- `{"method":"mcp","adfPath":...,"sizeBytes":...,"pageId":...,"spaceId":...,"title":...,"diagramsRendered":0,"missingPrerequisite":"ATLASSIAN_API_TOKEN"}` (the `missingPrerequisite` key is present only when diagrams were substituted for notes) — proceed to Step 5.

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

## Other subcommands

`extract`, `render-attach`, `substitute-media`, `publish-adf`, and `combine` are the pipeline steps `run` chains together; each stays independently invokable for the MCP/degraded fallback above or ad-hoc use — see `python3 scripts/publish_page_diagrams.py --help` and each subcommand's own `--help`. `replace-markers` is a legacy, top-level-only back-compat alias for `substitute-media`.

## Verification

`python3 -m pytest plugins/atl/skills/publish-page/` (from the repo root) — the full pipeline: extraction, conversion hand-off, attachment upload, marker substitution, and REST/MCP branching, all mocked. Conversion itself is covered at its own seam, `python3 -m pytest plugins/atl/skills/map-markdown-adf/`. When verifying a live publish via `getConfluencePage`, request `body-format: atlas_doc_format` and check the returned body for `"type": "media"` node occurrences matching the diagram count — confirm the actual response shape empirically before asserting specific top-level keys (e.g. `title`/`version`) you haven't verified against the live MCP tool. The MCP-only publish path and token-free degradation are verified manually against this skill's acceptance criteria — MCP transport and this prose are deliberately untested.

