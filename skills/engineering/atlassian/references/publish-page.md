# Publish page

Publish local Markdown to a Confluence page in one `run` command: extract → convert → attach → substitute → publish, always over REST. Not twg: only `atl.py`'s Markdown → ADF conversion carries `<details>`, panels, status, TOC, wide tables, inline-comment anchors, and diagrams intact.

## Contents

- Prerequisites
- Inputs
- Steps
- Edit a fetched page
- Inline comments
- Diagram renderer
- Diagram ids
- Rules
- Degraded mode
- Other subcommands
- Completion criteria

## Prerequisites

- Diagram present → **MUST** have `mmdc` on PATH: `npm install -g @mermaid-js/mermaid-cli`; verify `mmdc --version`. Headless Chrome libs (Ubuntu 24.04; older releases drop `t64`): `sudo apt-get update && sudo apt-get install -y libnspr4 libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2t64`. Diagram-free source → no `mmdc`.
- **MUST NOT** print, log, quote, or publish `site`, `email`, `apiToken` in page content, tool args, or output. `run` reads `.atlassian.json.user` itself; never pass credentials as CLI args.

## Inputs

- **mdPath** — required; local Markdown path.
- **pageId** — optional; update that page instead of creating.
- **spaceId** — optional; numeric Confluence space id, resolved in Step 1.
- **title** — optional; defaults to the first `#` heading. Update writes the title too → a differing heading **renames** the page; pass the existing title to keep it. A leading level-1 heading is never published in the body; Confluence shows the title itself (Fetch page re-adds `# <title>`).

## Steps

**1 — Resolve target.** `pageId` → update, `--page-id`. Else create, `--space-id` from the first hit: supplied `spaceId` → Preflight `defaultSpaceId` (report) → `<twg> confluence space list --limit <limit>`: one → use, report; several → ask, never choose silently. Space key instead of numeric id (e.g. `ZIC`, `~<accountId>`) → `<twg> confluence space list --keys <key> -o json --output-file space.json` → `data[0].id`; REST v2 create rejects keys.

**2 — Run.**

```bash
python3 <skillDir>/scripts/atl.py publish-page run --md-path <mdPath> (--page-id <pageId> | --space-id <spaceId>) [--title "<title>"] --config "<configPath>"
```

Pipeline: strip `<!-- adf:ignore:start/end -->` spans; replace ```` ```mermaid ```` fences and standalone local image/file refs (as Fetch page writes them) with markers; convert Markdown to ADF; then:

- Diagrams/local attachments → ensure page (placeholder when creating), render, upload, substitute markers at any depth (image → `mediaSingle`, filename as `alt`, `media-size`: `width`/`height` on the media node, `display-width` and `layout` on the `mediaSingle`; other file → `mediaGroup`), publish.
- Neither → publish the converted ADF directly.

Exits non-zero naming the cause on: missing `cloudId`/`email`/`apiToken`; missing `mmdc` (diagram path) or `drawio` (`drawio` mode); unsupported/unusable `diagramRenderer`; missing `drawioExtensionKey`; duplicate `%% diagram-id`; leftover marker after substitution. All but the last fail before any page is touched. Fix and re-run; do not work around. A create that fails after the placeholder page exists names the new page id in the error → re-run with `--page-id <id>`, never a second create.

Outputs default to `<mdPath>.tmp/` (e.g. `docs/design.md.tmp/final-adf.json`); override with `--assets-dir`, `--out`.

Stdout JSON:
- `{"method":"rest","pageId":...,"title":...,"sizeBytes":...,"diagrams":N,"attachments":N,"renderer":...,"adfPath":...}` → published.
- Update only, comment guard keys (see Inline comments): `orphanedComments` `[{id,markerRef,selection}]`, `orphanNoticeCommentId`, `unknownCommentIds`, `partialCommentRemovals` `[{id,before,after}]`, `commentGuard` (`failed (<category>)`, `notice failed (<category>)`).

**3 — Verify.** Re-fetch into a separate dir and assert:

```bash
python3 <skillDir>/scripts/atl.py publish-page verify --page-id <pageId> --config "<configPath>" --expect-anchors <n> [--present <file>] [--absent <file>] --verify-dir <workingDir>/verify
```

`<n>` = expected `adf:comment id` span count in the published Markdown; `--present`/`--absent` = one phrase per line (edited / removed phrases). Prints each check `PASS|FAIL <name>`; exit 1 = failed check, 2 = re-fetch failed. Deletes nothing.

**4 — Report** page URL; with diagrams, confirm the page and attachment list show every image. Report `orphanedComments` (selection + id), `unknownCommentIds`, `partialCommentRemovals` when present.

## Edit a fetched page

Ordinary edits of an existing page without thread replies. Review-thread replies belong to the Address page comments tactic; never switch to it from here.

1. Fetch with the **Fetch page** tactic into `tmp/<pageId>/page.md`; copy it to `tmp/<pageId>/original.md`. Done when both exist.
2. Edit `page.md`. Text kept → keep its `adf:comment` span and id unchanged; the span moves with the text. Text removed on purpose → delete the span with it. Ambiguous intent → ask once, batched, before editing.
3. Compare anchors offline: `python3 <skillDir>/scripts/atl.py publish-page check-anchors --original tmp/<pageId>/original.md --md-path tmp/<pageId>/page.md` → `{"sharedIds","kept","removed","partialCommentRemovals"}`. Exit 1 → a shared id keeps only some spans: keep all spans for that id or remove all, then re-run. Done when exit 0 and `removed` lists only intended detachments.
4. Record `expected-anchors` (span count), `present.txt` (edited phrases), `absent.txt` (removed phrases) in `tmp/<pageId>/`.
5. Publish (Step 2) with the page id and the existing title. Publish posts at most one detached-comment notice.
6. Verify (Step 3) with those files and `--verify-dir tmp/<pageId>/verify`. Pass → delete `tmp/<pageId>/`. Fail → keep it, report the failing check name, stop.
7. Report kept, removed, and ambiguous comments, `orphanedComments`, and the verification result. Never resolve or reply to threads.

## Inline comments

- A Confluence inline comment stays highlighted only while the published body keeps its anchor: `<!-- adf:comment id="<id>" -->text<!-- /adf:comment -->`.
- Body without the anchor → Confluence keeps the comment open but detached from any text. Never deleted.
- **MUST** keep anchors and ids unchanged when editing; delete one only when its text is removed on purpose. Keep or remove every span of a shared id together.
- Update: before publishing, `run` compares the live body's anchors with the new body's. Publish always proceeds.
- Open comments anchored now but missing after → one page (footer) comment: table of highlighted text, author, excerpt, link, anchor id, plus how to reattach (re-add the span, republish) or resolve.
- Already-detached comments are never re-reported, so republishing posts no duplicate notice.
- Anchor id matching no page comment → `unknownCommentIds`; Confluence ignores it. Fix the id or remove the span.
- Shared id kept on fewer blocks than live, but not zero → stderr `warning: comment anchor <id> spanned N blocks, now M; ...` and `partialCommentRemovals`. Publish proceeds.
- Create path → no guard. Guard read failure → publish proceeds, `commentGuard: "failed (<category>)"`.
- Markdown fetched without anchors (older fetch, or a twg Markdown export) → refetch with Fetch page before editing, else every comment detaches.

## Diagram renderer

`diagramRenderer` in `.atlassian.json.user`. Absent/empty → `png`.

| Value | Page output | Extra prerequisite | Status |
|---|---|---|---|
| `png` | Static image attached to the page | none beyond `mmdc` | Usable |
| `drawio` | Editable Confluence Draw.io diagram | Draw.io app, `drawio` CLI on PATH, `drawioExtensionKey` | Usable |
| `mermaid` | Live Confluence Mermaid macro | Confluence Mermaid app | Refused; macro shape not yet captured |

`mmdc` required for every value: renders `png`, validates source for others. Unknown or uncaptured value fails before any page is touched.

- **`drawioExtensionKey`** (`drawio` only): `<appId>/<envId>/static/drawio`; per site/install, no default. Find it in the raw ADF (REST v2 `body-format=atlas_doc_format`) of a page already holding a Draw.io diagram: the node's `attrs.extensionKey`.
- Per diagram `drawio` publishes a `.drawio` attachment, a `.drawio.png` preview, an app custom content record, and an ADF extension node. Republish finds the record by page + diagram name and bumps it.
- Draw.io's bundled Mermaid rejects some types (e.g. `swimlane-beta`). Failed or empty-canvas import → that diagram alone falls back to `png` with a stderr warning.
- Error `Could not create content with type ac:com.mxgraph.confluence.plugins.diagramly:drawio-diagram` → payload lacks the page space, not a missing app. Check the app via `/rest/api/content/<pageId>/child` → type in `_expandable`.
- **Draw.io CLI install** (`drawio --version` fails): `python3 <skillDir>/scripts/install_drawio.py [version] [--prefix ...] [--bindir ...]`. Installs to `~/.local/opt/drawio` + wrapper `~/.local/bin/drawio`; no root/FUSE; idempotent. No `DISPLAY` → wrapper uses `xvfb-run` (`apt-get install -y xvfb`).

## Diagram ids

`%% diagram-id: <id>` gives a mermaid fence stable identity: `[a-z0-9-]`, unique per file, after any `---` frontmatter or `%%{init: …}%%`, directly above the diagram-type line. Id = attachment filename + Draw.io record title → republish replaces in place despite reorders or heading edits. `run` strips the line before rendering.

- No id → `{index}-{nearest-heading-slug}` naming; reorder or heading rewording → next publish adds a duplicate.
- Ids are permanent: rename/delete orphans the attachment and record (`run` never deletes). Prune manually in Confluence.
- `png`/`drawio` also attach `{name}.source.mmd` (fence verbatim); Fetch page uses it to restore the mermaid block. `mermaid` mode skips it. Never read on publish.

## Rules

- Never rephrase Markdown; the converter preserves source wording verbatim.
- Named `pageId` → update in place; create only when none named.
- Never choose a space silently.
- Out of scope: non-mermaid diagram formats, bulk publishing.
- Verify read-only (Step 3); **MUST NOT** re-run `run`/`publish-adf` with test content; it overwrites the real publish.
- **Order:** publish → verify into `<workingDir>/verify/` → only on pass delete working files. Working dir default `<mdPath>.tmp/`. Failed check → keep every file, report the failing check name.

## Degraded mode

- No Atlassian config or no token → nothing published; report missing `cloudId`/`email`/`apiToken`.
- Any Step 2 failure → nothing published unless the error names a created page id; fix and re-run. `diagramRenderer=mermaid` → switch to `png` or `drawio` to publish now.

## Other subcommands

`extract`, `render-attach`, `substitute-media`, `publish-adf`, `combine` = steps `run` chains; each invokable alone for ad-hoc use (`--help`). `replace-markers` = legacy top-level-only alias for `substitute-media`. `render-attach` supports `png` only.

## Completion criteria

- Live: REST v2 `GET <site>/wiki/api/v2/pages/<pageId>?body-format=atlas_doc_format`. `png` → `"type": "media"` count = diagram count; 2 attachments per diagram (`.png`, `.source.mmd`). `drawio` → `"type": "extension"` with `static/drawio`; 3 attachments per diagram.
- `publish-page verify` exits 0: anchor count, every edited phrase present, every removed phrase absent.
- Raw REST probes **MUST** use `<site>/wiki/...` (else 404 `No endpoint POST /rest/api/content`).
