# Fetch page

Return a Confluence **Page** as Markdown from a page ID, tiny ID, URL, or selected search hit. REST v2 reads the real ADF body, attachments, and comments; `atl.py` converts ADF back to Markdown verbatim. Not twg: its Markdown export drops ADF-only constructs and comment anchors. Use for every page body read; twg only finds pages.

## Contents

- Steps
- Attachments
- Attachment modes
- Comments
- Degraded mode

## Steps

1. **Parse input.** URL `<site>` differing from Preflight `site` → pass `--site https://<site>`.
   - `https://<site>/wiki/spaces/<space>/pages/<page_id>/<title>` → `<page_id>`.
   - Bare numeric ID or search hit ID → `<page_id>` as-is.
   - Tiny link `https://<site>/wiki/x/<tiny_id>`, or bare tiny ID → URL `<site>/wiki/x/<tiny_id>`; resolve with `<twg> confluence content get <url> --detail summary -o json --output-file tiny.json` → `<page_id> := data.id`.
2. **Fetch and assemble.**
   ```bash
   python3 <skillDir>/scripts/atl.py fetch-page --page-id <page_id> --config "<configPath>" --md-path page.md [--site https://<site>] [--assets-dir <dir>] [--attachments auto|skip|required] [--comments auto|skip]
   ```
   Fetches title + ADF over REST v2 (`body-format=atlas_doc_format`), converts to Markdown (Draw.io, TOC, smart links, media → placeholders/links), caches attachments, resolves placeholders; writes `# <title>\n\n<body>`. Assets default to `page.md.assets/`.
   - Unsupported ADF → non-zero exit, `ADF conversion failed: <reason>` on stderr, no `page.md`.
   - REST failure → `Page fetch failed: <category>`, no `page.md`; category = exception class + HTTP status, plus a hint for 404 (`check site URL and page id; wrong API base?`) and 401/403 (`check email/apiToken`).
3. **Return** `page.md` unchanged.

Non-zero exit → report stderr; **MUST NOT** run `wc`/`cat` on the missing `page.md` or retry with edited ADF.

## Attachments

**Detection:** offline recursive scan of raw ADF; no match → no attachment call regardless of mode. Matches:
- `media` with `attrs.type == "file"`;
- `media` with `attrs.alt` ending `.png|.jpg|.jpeg|.gif|.svg|.webp|.bmp`;
- `extension` with `attrs.extensionKey` containing `drawio`.

**Caching:** on match, list and download all page attachments once; stage in a sibling dir, then atomically replace the assets dir; failure never leaves a partial cache or damages a prior one. TLS verification always on.

**Placeholder resolution:**
1. `{stem}.source.mmd` sidecar attached → verbatim ```` ```mermaid ```` fence only, no image (Publish page re-renders).
2. Image, no sidecar → `![<alt or filename>](page.md.assets/<file>)`; if the placeholder has `width`/`height`, `display-width`, or `layout`, add `<!-- media-size: [width=<w> height=<h>] [display-width=<n>[%]] [layout=<layout>] -->` on the next line (Publish page restores display size and position from it).
3. Other file → `[<filename>](page.md.assets/<file>)`.

Links percent-encoded, relative to `page.md`'s dir. Publish page re-uploads rule 2/3 references on republish.

## Attachment modes

- **`auto`** (default) — retrieve. Listing/download/publish failure (TLS, timeout, HTTP, disk) → keep title/body; note with safe category only, e.g. `attachment retrieval failed (SSLError)` or `(HTTPError 403: check email/apiToken)`. **MUST NOT** include exception text (may hold a signed URL or token).
- **`skip`** — no attachment REST call; note `attachment retrieval skipped (--attachments skip)`.
- **`required`** — failure or unresolvable placeholder → non-zero exit, `Attachment retrieval failed: <reason>` on stderr, no `page.md`.

## Comments

- Body inline comments arrive as `<!-- adf:comment id="<id>" -->text<!-- /adf:comment -->` spans; they keep comments attached when Publish page republishes.
- **`--comments auto`** (default): appends `## Comments` inside `<!-- adf:ignore:start/end -->`: each inline/footer thread with author, date, plain-text body, replies, Confluence link; inline threads say whether their id is anchored in the body.
- Shared anchor: one comment over several blocks (e.g. two bullets) fetches as the same id on each → `## Comments` notes `id X spans N blocks; edit or remove all together`.
- REST failure → note with safe category only, e.g. `comment retrieval failed (ConnectionError)`; `page.md` still written.
- **`--comments skip`** — no lookup.
- Read-only: fetching never resolves, replies to, or edits comments.

## Degraded mode

- Diagram published before sidecars existed → note naming missing `{name}.source.mmd`; republish with Publish page, then refetch.
- `atl.py` unavailable or failing for a non-auth reason → `<twg> confluence content get <id-or-url> --detail full --format md -o json --output-file page.json`; warn the user it is lossy (diagrams, media, attachments, comments may be missing). Auth or policy denial → stop and report; no fallback.
