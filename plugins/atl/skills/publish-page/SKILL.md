---
name: publish-page
description: Create or update a Confluence page from a local Markdown file, over the MCP — with mermaid diagrams rendered and attached when an API token is configured, degrading to a text-only publish (naming the missing prerequisite) when it isn't. Use when asked to publish, create, or update a Confluence page from a markdown file. Absorbs `create-conf` and `pub-zdesign`.
argument-hint: '<md_file_path>, [pageId], [spaceId]'
---

# Publish Page

Create or update a Confluence **page** from a local Markdown file. The page's text always publishes over the MCP alone — no `acli`, no API token. When the source contains ```mermaid diagrams, an `ATLASSIAN_API_TOKEN` unlocks a second backend, `atlassian-python-api`, for the one thing the MCP does not expose: attachment upload. Absorbs `create-conf` and `pub-zdesign` — one document-publishing operation, not a rendering-backend-shaped skill split (see [ADR 0005](../../../../docs/adr/0005-atl-is-mcp-first.md)).

## Prerequisites (diagram branch only)

Needed only when the source has ```mermaid fences and an API token is configured; every other publish needs none of this.

- `pip install -r requirements.txt` (relative to this skill's directory).
- `mmdc` on PATH: `npm install -g @mermaid-js/mermaid-cli` (npm, not pip); verify `mmdc --version`.
- `mmdc` renders via headless Chrome (puppeteer), which needs these shared libraries on Debian/Ubuntu (package names shown are for Ubuntu 24.04; older releases use the non-`t64` names): `sudo apt-get update && sudo apt-get install -y libnspr4 libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2t64`.

## Confidentiality

Never print, log, quote, or publish `ATLASSIAN_SITE`, `ATLASSIAN_EMAIL`, or `ATLASSIAN_API_TOKEN`'s value — not in page content, tool arguments, or output. The diagram scripts read credentials from `.atlassian` themselves; never pass them as CLI arguments.

## Inputs

- **mdPath** — required, path to the local Markdown file.
- **pageId** — optional; when named, update that page instead of creating one.
- **spaceId** — optional; when omitted, resolved per Step 5.
- **title** — optional; defaults to the Markdown's first `#` heading.

## Workflow

**Step 1 — Preflight**
Run `/preflight-atl`' skill **Action: Resolve**.

**Step 2 — Resolve `cloudId`**
Use Preflight's `cloudId`. Still empty → call `getAccessibleAtlassianResources` once and use the matching resource's `cloudId`, per Preflight's standing rule.

**Step 3 — Extract diagrams**
Run, from the directory holding this `SKILL.md`:

```bash
python3 scripts/publish_page_diagrams.py extract < <mdPath>
```

Prints `{"processedMarkdown": ..., "diagrams": [...]}`. `processedMarkdown` has every ```mermaid fence replaced with a `\x00MEDIA:<index>\x00` marker paragraph — feed *this*, not the raw file, into Step 4. `hasDiagrams := len(diagrams) > 0`.

**Step 4 — Convert**
Run `/map-markdown-adf`' skill **Action: Convert Markdown to ADF**, piping `processedMarkdown` in. This is the page's ADF `content` array before any diagram is wired in — call it `baseAdf`.

**Step 5 — Resolve the publish target**

`pageId` named → **update**, never create a second page (Step 7 uses `updateConfluencePage`).

`pageId` not named → **create**; resolve `spaceId` first:
- Developer supplied one → use it.
- Else Preflight's `defaultSpaceId` is non-empty → use it, reporting it as the resolved default.
- Else call `getConfluenceSpaces` with `limit: 10`. Exactly one space → use it, reporting it as the resolved default. More than one → ask the developer which space to use — never choose one silently, per Preflight's Ambiguity rule.

**Step 6 — Diagram branch** (skip entirely when `hasDiagrams` is false — `finalAdf := baseAdf`)

- **No token** (`tokenAvailable` false): replace every `\x00MEDIA:<n>\x00` marker paragraph in `baseAdf` with a plain paragraph noting that diagram was not rendered because `ATLASSIAN_API_TOKEN` is not configured. `finalAdf := baseAdf` with those substitutions. Tell the developer, after publishing, which diagrams were skipped and that an API token is the missing prerequisite.
- **Token available**: a page must exist before an attachment can be uploaded to it.
  1. `pageId` already known (update case) → use it. Otherwise create the page now via `createConfluencePage` (`cloudId`, `spaceId`, `title`, `body`: `baseAdf` JSON-stringified with every marker already swapped for the "not yet rendered" note from the no-token branch above, `contentFormat: "adf"`) — this is a placeholder write Step 7 replaces; capture the returned `pageId`.
  2. Run:
     ```bash
     python3 scripts/publish_page_diagrams.py render-attach \
       --assets-dir <sibling-to-mdPath>/<mdPath-stem>.artifacts \
       --page-id <pageId> \
       --root "$HARNESS_REPO_PATH" \
       < <diagrams JSON from Step 3, as {"diagrams": [...]}>
     ```
     - Exits non-zero naming `mmdc` as the missing prerequisite (installed via the Prerequisites section) when the renderer isn't on PATH — report that exact prerequisite to the developer, do not treat it as a generic failure.
     - On success, prints `{"mediaIdsByIndex": {"<index>": "<fileId>", ...}}`.
  3. For each diagram, replace its `\x00MEDIA:<index>\x00` marker paragraph in `baseAdf` with:
     ```json
     {
       "type": "mediaSingle",
       "attrs": { "layout": "center", "width": 768, "widthType": "pixel" },
       "content": [
         { "type": "media", "attrs": { "id": "<mediaIdsByIndex[index]>", "type": "file", "collection": "contentId-<pageId>" } }
       ]
     }
     ```
     `finalAdf := baseAdf` with every marker replaced this way.

**Step 7 — Publish**
- Update case → call `updateConfluencePage` with `cloudId`, `pageId`, `body`: `finalAdf` JSON-stringified, `contentFormat: "adf"`, `title` (if changed).
- Create case, no diagrams → call `createConfluencePage` with `cloudId`, `spaceId`, `title`, `body`: `finalAdf` JSON-stringified, `contentFormat: "adf"`.
- Create case, diagrams present → the page already exists from Step 6; call `updateConfluencePage` with `cloudId`, `pageId`, `body`: `finalAdf` JSON-stringified, `contentFormat: "adf"`, `title`.

Report the page's URL from the tool result and, when diagrams were rendered, confirm both the page and its attachment list show every image.

## Rules

- Never rephrase Markdown content — `map-markdown-adf` handles structure; content itself is never rewritten.
- A named `pageId` is always updated in place; a fresh page is created only when none is named.
- Never choose a space silently when more than one is configured and no default resolves.
- Diagram formats other than ```mermaid are out of scope. Bulk/batch publishing is out of scope.

## Degraded mode

- No **Atlassian config** file → Preflight's `cloudId`/`defaultSpaceId` come back empty; Step 2's `getAccessibleAtlassianResources` fallback resolves `cloudId`, and Step 5's space-visibility lookup resolves `spaceId` (asking the developer when ambiguous). A source with no diagrams publishes exactly the same as with full configuration.
- No **API token** (`tokenAvailable` false) and the source has diagrams → Step 6's no-token branch runs; the page's text still publishes, and the developer is told which diagrams were unrendered and that an API token is the missing prerequisite.
- Token configured but `mmdc` not installed → Step 6's `render-attach` call fails naming `mmdc` as the missing prerequisite; the page created in Step 6.1 with the "not yet rendered" placeholder is left as the final published state (re-run once `mmdc` is installed to render and attach the diagrams).

## Verification

Run `python3 -m pytest plugins/atl/skills/publish-page/` (from the repo root) — the diagram CLI's test seam: diagram source → image → attachment payload, token branch only. Conversion behaviour is covered at its own seam, `python3 -m pytest plugins/atl/skills/map-markdown-adf/`. The MCP-only publish path and the graceful degradation without a token are verified by this skill's acceptance criteria manually — MCP transport and this prose are deliberately untested.
