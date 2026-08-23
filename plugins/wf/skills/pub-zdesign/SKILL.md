---
name: pub-zdesign
description: Publish or update a `to-zdesign` design Markdown file (under `docs/designs/`) to Confluence as an ADF page, rendering every ```mermaid fenced diagram to a PNG and embedding it inline. Use when the user asks to publish, sync, or push a zdesign document to Confluence. Every run re-renders all diagrams and updates the same target page (idempotent — never creates a duplicate page or duplicate attachments).
---

# Publish zDesign to Confluence

Publishes a zdesign Markdown doc as a Confluence page in **ADF** (`atlas_doc_format`), not storage
format. Node mapping: [references/adf-mapping.md](references/adf-mapping.md).

## Preconditions

- `ACLI_SITE`, `ACLI_EMAIL`, `ACLI_API_TOKEN` in `.env/.atlmcp.env`, relative to the repo being
  published from, not this skill's directory (see `setup-atlm`).
- `pip install -r requirements.txt` (relative to this skill's directory).
- `mmdc` on PATH: `npm install -g @mermaid-js/mermaid-cli` (npm, not pip); verify `mmdc --version`.
- `mmdc` renders via headless Chrome (puppeteer), which needs these shared libraries on Debian/
  Ubuntu (package names shown are for Ubuntu 24.04; older releases use the non-`t64` names, e.g.
  `libasound2` instead of `libasound2t64`):
  `sudo apt-get update && sudo apt-get install -y libnspr4 libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2t64`.

## Confidentiality

- Never print, log, quote, or commit `ACLI_API_TOKEN` or any other `.atlmcp.env` value.
- Credentials are read from the env file inside the script; never pass them as CLI args or literals.

## Every run

0. Strips every `<!-- confluence:ignore:start -->`/`<!-- confluence:ignore:end -->` span (tags
   included) from the source before any other processing — that content, and any diagram inside
   it, never reaches Confluence.
1. Extracts every ` ```mermaid ` fence in source order.
2. Recolors each diagram's dark-theme hex codes (the palette documented in
   `docs/designs-styles.md`) to the `style1-github-light` palette before rendering — a source-only
   transform (`zdesign_publisher/theme.py`); the markdown file on disk is never modified. Renders
   each to PNG via `mmdc` (`-w 1040 -s 2`, white background; override with `--mermaid-bg`), with
   `--cssFile` pointing at a `_light_theme.css` written into the assets dir (from
   `theme.LIGHT_THEME_CSS`) to also recolor `namespace`/`subgraph` boxes, which mermaid renders via
   a hardcoded CSS rule that `themeVariables` can't reach.
3. Writes `.mmd` + `.png` to a folder named after the markdown stem, sibling to it
   (`docs/designs/my-design.md` → `docs/designs/my-design.artifacts/`). Deterministic filenames
   (`<index>-<nearest-heading-slug>.png`) → re-runs overwrite.
4. Uploads each PNG (same filename → Confluence versions, does not duplicate), then re-reads
   `extensions.fileId`. That id is not the attachment content id and is not version-stable, so it
   must be re-read every run (see references/adf-mapping.md).
5. Converts remaining markdown to ADF, substituting each fence with a `mediaSingle`/`media` node.
6. Publishes with `update_page(..., representation="atlas_doc_format", always_update=True)`.
   `always_update=True` is required — Confluence's content-equality check compares against the
   `storage` body, which never matches an ADF payload.
7. Re-fetches the body and asserts every fileId is present before reporting success.

## Usage

Update an existing page:

```bash
python scripts/publish_zdesign.py \
  --md docs/designs/<design>.md \
  --page-id <confluence pageId>
```

Create a page (first run only — record the returned `page_id` so later runs pass `--page-id`):

```bash
python scripts/publish_zdesign.py \
  --md docs/designs/<design>.md \
  --space-key <spaceKey> \
  --title "<page title>"
```

`scripts/publish_zdesign.py` is relative to this skill's directory, not the invoking repo's root — resolve it from wherever this SKILL.md is installed. `--md` and `--env` remain relative to the repo being published from.

Flags:

| Flag | Required | Notes |
| --- | --- | --- |
| `--md` | yes | Path to the zdesign markdown file. |
| `--page-id` | one of `--page-id` / `--space-key`+`--title` | Page to update. |
| `--space-key` | only when creating | Space to create the page in. |
| `--title` | no | Defaults to the markdown's first `#` heading. |
| `--env` | no | Defaults to `.env/.atlmcp.env`. |
| `--mermaid-bg` | no | `mmdc` background color; defaults to `white`. |
| `--image-width` | no | Diagram display width in px; defaults to `768`. |

## Verification

The script verifies media ids landed in the published body and exits non-zero on failure.
Optionally open the printed `url=` and confirm every diagram renders and every `<details>` appears
as a collapsible expand.

## Known limitations

See [references/adf-mapping.md](references/adf-mapping.md): nested inline marks (e.g. link inside
bold) unsupported; unknown code-fence languages publish with `attrs.language` omitted.
