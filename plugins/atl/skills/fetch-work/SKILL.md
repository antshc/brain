---
name: fetch-work
description: >-
  Fetch a Jira work item as Markdown from its key or URL, with every long field in full and embedded images cached beside it. Use when asked to fetch, read, show, or summarize a Jira work item or issue. Use fetch-page for Confluence pages.
argument-hint: '<work_item_key_or_url> (e.g. "PROJ-123" or "https://<site>.atlassian.net/browse/PROJ-123")'
---

# Fetch Work

Return a Jira **Work item** as Markdown from key or URL. REST reads the real ADF description; *`map-markdown-adf` skill converts ADF back to Markdown, preserving source wording verbatim*. Not twg: its body format drops `map-markdown-adf` constructs.

## Prerequisites

- `atlassian-python-api>=5.0.5` installed by `init-atl` skill (plugin-wide); missing or other version (script exits `atlassian-python-api >=5.0.5 required, found <version>; run init-atl`), *run `init-atl` skill for first-run setup of `.atlassian.json.user` and Atlassian dependencies* first. This skill installs nothing.
- `cloudId`, `email`, `apiToken` in `.atlassian.json.user` (see `preflight-atlassian` skill). Missing → script exits non-zero naming them; report and stop.

## Workflow

**1 — Preflight.** *Run `preflight-atlassian` skill to resolve site, default project key, credentialed twg command, and token availability from `.atlassian.json.user` config* **Action: Resolve**; keep `configPath`.

**2 — Parse `{{input}}`.**
- `https://<site>/browse/<key>` → `<site>`, `<key>`; `<site>` differs from Preflight `site` → pass `--site https://<site>`.
- Bare `<key>` → Preflight `site`.

**3 — Fetch and assemble.** From this skill's directory:

```bash
python3 scripts/assemble_work.py --issue-key <key> --config "<configPath>" --md-path work.md [--site https://<site>]
```

Fetches `summary`, `status`, `issuetype`, `assignee`, ADF `description` over REST v3; converts via *`map-markdown-adf` skill to convert Atlassian Document Format (ADF) back to Markdown, preserving source wording verbatim* **Action: Convert ADF to Markdown** (media nodes → placeholders); applies Attachment rules. Writes `work.md`: `# <key> — <summary>`, then `**Status:** · **Type:** · **Assignee:**`, then body. `--assets-dir <dir>` overrides cache dir (default `work.md.tmp`, beside `work.md`).

**4 — Return** `work.md` contents unchanged.

## Attachment rules

- Detect: offline recursive scan of ADF for `media` with `attrs.type == "file"` or `attrs.alt` ending `.png|.jpg|.jpeg|.gif|.svg|.webp|.bmp`. No match → no attachment call.
- Match → download all issue attachments to assets dir (gitignored via `*.tmp`).
- Resolve each placeholder by `alt` (original filename) against `fields.attachment[].filename`, never `media-id` (REST doesn't expose it).
  - Image → `![<filename>](work.md.tmp/<file>)`; if `width`/`height`, `display-width`, or `layout` known, next line `<!-- media-size: [width=<w> height=<h>] [display-width=<n>[%]] [layout=<layout>] -->`.
  - Other → `[<filename>](work.md.tmp/<file>)`.
- Links percent-encoded, relative to `work.md`'s directory. No Draw.io/mermaid-sidecar rule (unlike `fetch-page` skill).

## Degraded mode

- No **Atlassian config** → Preflight asks for `site`; credentials still required.
- Attachment named in the body but no longer attached → one-line note replaces it; rest of the body returned.

## Gotchas

- **MUST NOT `find`/`grep`/`ls -R` to locate this skill's directory.** Use the parent of the `SKILL.md` path you were given.
- Comments, links, or other fields beyond the header → *follow `twg` skill for Jira workitems* with Preflight's `twg` (`jira workitem get <key> --comments`); never patch them into `work.md`.
