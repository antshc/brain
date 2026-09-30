---
name: fetch-work
description: Fetch a Jira work item as Markdown from its key or URL, returning every long field in full. Use when asked to fetch, read, show, or summarize a Jira work item/issue by key or URL. No Atlassian config required; with `apiToken` configured, embedded images/files are cached to a `.tmp` folder beside the Markdown and linked.
argument-hint: '<work_item_key_or_url> (e.g. "PROJ-123" or "https://<site>.atlassian.net/browse/PROJ-123")'
---

# Fetch Work

Return a Jira **Work item** as Markdown from key or URL. MCP only; API token needed only to resolve embedded images/files.

## Prerequisites

- `atlassian-python-api` installed by `init-atl` (plugin-wide); run it first if missing. This skill installs nothing.
- Embedded image/file resolution needs `apiToken` in `.atlassian.json.user` (see `preflight-atlassian` skill) — MCP returns no real ADF (see Gotchas). No token → no download; each embedded image becomes a placeholder note.

## Workflow

**1 — Preflight.** Run `preflight-atlassian` (resolves cloudId, default project key, default space id, token availability, `.atlassian.json.user` config) **Action: Resolve**; keep `configPath`.

**2 — Parse `{{input}}`.**
- `https://<site>/browse/<key>` → `<site>`, `<key>`; `<site>` overrides Preflight's `cloudId`.
- Bare `<key>` → Preflight's `cloudId`.

**3 — Fetch.** `getJiraIssue` with `cloudId`, `issueIdOrKey: <key>`. Omit `fields`; defaults suffice. No matching MCP tool → REST fallback per Preflight.

**4 — Guard truncation.** Save result to `content.json`; read with Python (Preflight rule).

**5 — Assemble.** From this skill's directory:

```bash
python3 scripts/assemble_work.py --issue-key <key> --config "<configPath>" --md-path work.md < content.json
```

Writes `work.md`: `# <key> — <summary>`, then `**Status:** · **Type:** · **Assignee:**`, then body. `--assets-dir <dir>` overrides cache dir (default `work.md.tmp`, beside `work.md`).
- No token → uses MCP `fields.description` as-is; each `![](blob:...)` → note naming `apiToken`.
- Token → fetches real ADF over REST, converts via `map-markdown-adf` **Action: Convert ADF to Markdown** (media nodes → placeholders), then applies Attachment rules.

**6 — Return** `work.md` contents unchanged.

## Attachment rules

- Detect: offline recursive scan of ADF for `media` with `attrs.type == "file"` or `attrs.alt` ending `.png|.jpg|.jpeg|.gif|.svg|.webp|.bmp`. No match → no REST/attachment call.
- Match → download all issue attachments to assets dir (gitignored via `*.tmp`).
- Resolve each placeholder by `alt` (original filename) against `fields.attachment[].filename`, never `media-id` (REST doesn't expose it).
  - Image → `![<filename>](work.md.tmp/<file>)`; if `width`/`height` known, next line `<!-- media-size: width=<w> height=<h> -->`.
  - Other → `[<filename>](work.md.tmp/<file>)`.
- Links percent-encoded, relative to `work.md`'s directory. No Draw.io/mermaid-sidecar rule (unlike `fetch-page`).

## Degraded mode

- No **Atlassian config** → Preflight Step 2 supplies `cloudId`; rest unchanged.
- No **API token** + embedded media → Step 5 no-token branch; full text returned, notes replace images, no `.tmp` folder.

## Gotchas

- **MUST NOT `find`/`grep`/`ls -R` to locate this skill's directory.** Use the parent of the `SKILL.md` path you were given.
- **MCP `getJiraIssue` never returns real ADF for `description`**, even with `responseContentFormat: "adf"` — returns flattened Markdown with empty-alt `![](blob:...&id=<media-uuid>...)` images. Not JSON; `map-markdown-adf` `adf-to-md` raises `JSONDecodeError` on it. Hence REST fetch when token present.

## Verification

`python3 -m pytest plugins/atl/skills/fetch-work/tests/` from repo root (all mocked). ADF→placeholder seam: `python3 -m pytest plugins/atl/skills/map-markdown-adf/`.
