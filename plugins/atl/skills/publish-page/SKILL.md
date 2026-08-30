---
name: publish-page
description: Create or update a Confluence page from a local Markdown file, over the MCP — with mermaid diagrams rendered and attached when an API token is configured, degrading to a text-only publish (naming the missing prerequisite) when it isn't. Use when asked to publish, create, or update a Confluence page from a markdown file.
argument-hint: '<md_file_path>, [pageId], [spaceId]'
---

# Publish Page

Create or update a Confluence **page** from a local Markdown file. Text always publishes over the MCP alone — no API token. When the source has ```mermaid fences, an `ATLASSIAN_API_TOKEN` unlocks `atlassian-python-api` for the one thing the MCP does not expose: attachment upload.

## Prerequisites (diagram branch only)

Needed only for ```mermaid fences with a token configured; every other publish needs none of this.

- `pip install -r requirements.txt` (relative to this skill's directory).
- `mmdc` on PATH: `npm install -g @mermaid-js/mermaid-cli` (npm, not pip); verify `mmdc --version`.
- `mmdc` renders via headless Chrome (puppeteer), needing these shared libraries on Debian/Ubuntu (names shown for Ubuntu 24.04; older releases drop `t64`): `sudo apt-get update && sudo apt-get install -y libnspr4 libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2t64`.

## Confidentiality

Never print, log, quote, or publish `ATLASSIAN_SITE`, `ATLASSIAN_EMAIL`, or `ATLASSIAN_API_TOKEN` — not in page content, tool arguments, or output. The diagram scripts read credentials from `.atlassian` themselves; never pass them as CLI arguments.

## Inputs

- **mdPath** — required, path to the local Markdown file.
- **pageId** — optional; when named, update that page instead of creating one.
- **spaceId** — optional; resolved per Step 5 when omitted.
- **title** — optional; defaults to the Markdown's first `#` heading.

## Workflow

**1 — Preflight.** Run `/preflight-atl` **Action: Resolve**.

**2 — Resolve `cloudId`.** Preflight's `cloudId`; still empty → `getAccessibleAtlassianResources` once, per Preflight's standing rule.

**3 — Extract diagrams.** From the directory holding this `SKILL.md`:

```bash
python3 scripts/publish_page_diagrams.py extract < <mdPath>
```

Prints `{"processedMarkdown": ..., "diagrams": [...]}`. `processedMarkdown` replaces every ```mermaid fence with a `\x00MEDIA:<index>\x00` marker paragraph — feed *this*, not the raw file, into Step 4. `hasDiagrams := len(diagrams) > 0`.

**4 — Convert.** Pipe `processedMarkdown` into `/map-markdown-adf` **Action: Convert Markdown to ADF**. The result is `baseAdf`.

**5 — Resolve the publish target.**

`pageId` named → **update**, never create a second page (Step 7 uses `updateConfluencePage`).

Else → **create**; resolve `spaceId`: supplied → use it. Else Preflight's `defaultSpaceId` if non-empty, reported as resolved. Else `getConfluenceSpaces` with `limit: 10` — exactly one → use it and report it; more than one → ask, never choose silently (Preflight's Ambiguity rule).

**6 — Diagram branch** (skip entirely when `hasDiagrams` is false — `finalAdf := baseAdf`)

- **No token** (`tokenAvailable` false): replace every `\x00MEDIA:<n>\x00` marker in `baseAdf` with a paragraph noting that diagram was not rendered because `ATLASSIAN_API_TOKEN` is not configured; `finalAdf := baseAdf` with those substitutions. After publishing, name the skipped diagrams and the API token as the missing prerequisite.
- **Token available**: a page must exist before an attachment can be uploaded to it.
  1. `pageId` known (update case) → use it. Else create the page now via `createConfluencePage` (`cloudId`, `spaceId`, `title`, `body`: `baseAdf` JSON-stringified with markers swapped for the no-token note above, `contentFormat: "adf"`) — a placeholder write Step 7 replaces; capture the returned `pageId`.
  2. Write `{"diagrams": [...]}` (Step 3's `diagrams`) to a temp file — never inline it into the terminal command via a heredoc, which mangles on long or special-character JSON. Then run:
     ```bash
     python3 scripts/publish_page_diagrams.py render-attach \
       --assets-dir <sibling-to-mdPath>/<mdPath-stem>.artifacts \
       --page-id <pageId> \
       --root "$HARNESS_REPO_PATH" \
       < <path to the temp file>
     ```
     - Exits non-zero naming `mmdc` as the missing prerequisite when the renderer isn't on PATH — report that exact prerequisite, not a generic failure.
     - On success prints `{"mediaIdsByIndex": {"<index>": "<fileId>", ...}}`.
  3. Write `{"adf": <baseAdf>, "mediaIdsByIndex": <Step 6.2's output>}` to a temp file — never construct this substitution with an inline Python heredoc in the terminal, which mangles on long or special-character JSON. Then run:
     ```bash
     python3 scripts/publish_page_diagrams.py replace-markers \
       --page-id <pageId> \
       < <path to the temp file>
     ```
     Prints `{"adf": ..., "replaced": <count>}` — `finalAdf := adf` from that output.

**7 — Publish.**
- Update case → `updateConfluencePage` with `cloudId`, `pageId`, `body`: `finalAdf` JSON-stringified, `contentFormat: "adf"`, `title` (if changed).
- Create case, no diagrams → `createConfluencePage` with `cloudId`, `spaceId`, `title`, `body`: `finalAdf` JSON-stringified, `contentFormat: "adf"`.
- Create case, diagrams present → the page exists from Step 6; `updateConfluencePage` with `cloudId`, `pageId`, `body`: `finalAdf` JSON-stringified, `contentFormat: "adf"`, `title`.

Report the page URL from the tool result and, when diagrams were rendered, confirm both the page and its attachment list show every image.

## Rules

- Never rephrase Markdown content — `map-markdown-adf` handles structure.
- A named `pageId` is always updated in place; a page is created only when none is named.
- Never choose a space silently.
- Non-```mermaid diagram formats and bulk publishing are out of scope.

## Degraded mode

- No **Atlassian config** → `cloudId`/`defaultSpaceId` empty; Step 2's `getAccessibleAtlassianResources` resolves `cloudId`, Step 5's space-visibility lookup resolves `spaceId` (asking when ambiguous). A diagram-free source publishes identically to full configuration.
- No **API token** with diagrams present → Step 6's no-token branch runs; text still publishes and the developer is told which diagrams were unrendered and that an API token is the missing prerequisite.
- Token configured but `mmdc` missing → `render-attach` fails naming `mmdc`; the Step 6.1 placeholder page is left as the published state (re-run once `mmdc` is installed).

## Verification

`python3 -m pytest plugins/atl/skills/publish-page/` (from the repo root) — the diagram CLI's test seam: source → image → attachment payload, token branch only. Conversion is covered at its own seam, `python3 -m pytest plugins/atl/skills/map-markdown-adf/`. The MCP-only publish path and token-free degradation are verified manually against this skill's acceptance criteria — MCP transport and this prose are deliberately untested.
