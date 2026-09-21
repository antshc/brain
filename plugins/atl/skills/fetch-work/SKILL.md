---
name: fetch-work
description: Fetch a Jira work item as Markdown from its key or URL, returning every long field in full. Use when asked to fetch, read, show, or summarize a Jira work item/issue by key or URL. No Atlassian config required; a description whose body embeds images or files caches them to a `.tmp` folder alongside the Markdown and references them in it when `ATLASSIAN_API_TOKEN` is configured.
argument-hint: '<work_item_key_or_url> (e.g. "PROJ-123" or "https://<site>.atlassian.net/browse/PROJ-123")'
---

# Fetch Work

Return a Jira **Work item** as Markdown from its key or URL. MCP only for summary/status/etc. — no API token required unless the description embeds an image or file, in which case resolving it needs one.

## Prerequisites

- `atlassian-python-api` is installed once by `/init-atl` for the whole `atl` plugin — run that first if you haven't; this skill installs nothing of its own.
- Resolving an embedded image or file needs `ATLASSIAN_API_TOKEN` (in `.atlassian`) — the Atlassian MCP's `getJiraIssue` tool never returns real ADF for `description` (see Gotchas), only a lossy Markdown-ish string with every embedded image's `alt` text empty, so restoring the real file needs a direct REST call. Without the token, nothing is downloaded and each embedded image comes back as a placeholder note instead.

## Workflow

**1 — Preflight.** Run `/preflight-atl` skill **Action: Resolve**.

**2 — Parse `{{input}}`.**
- `https://<site>/browse/<key>` → `<site>`, `<key>`; `<site>` wins as `cloudId` over Preflight's.
- Bare `<key>` → use Preflight's `cloudId`.

**3 — Fetch.** `getJiraIssue` with `cloudId`, `issueIdOrKey: <key>`. Omit `fields` — the default set already covers summary, description, status, issuetype, priority, labels, components, assignee, reporter, created, updated, resolution, project.

**4 — Guard truncation.** Save the tool result to `content.json` and read it with Python, per Preflight's standing rule.

**5 — Assemble.** One call does header formatting, conversion, attachment caching, and placeholder resolution together:

```bash
python scripts/assemble_work.py --issue-key <key> --root "$HARNESS_REPO_PATH" --md-path work.md < content.json
```

from this skill's directory. Writes `work.md` directly (add `--assets-dir <dir>` to override where attachments are cached; defaults to `work.md.tmp`, next to `work.md`). Internally: no token configured → the MCP result's already Markdown-ish `fields.description` is used as-is, with each embedded `![](blob:...)` image reference swapped for a note naming `ATLASSIAN_API_TOKEN`; token configured → fetches the issue's real ADF description directly over REST, converts it via `/map-markdown-adf` **Action: Convert ADF to Markdown** (a `media`/`mediaSingle`/`mediaGroup` node becomes a placeholder, never a raw error), then, only when a pure offline scan of the raw ADF body finds a node referencing an attached file, downloads every attachment on the issue to the assets dir and resolves each placeholder per the rendering rules below. `work.md` already reads `# <key> — <summary>\n**Status:** ... · **Type:** ... · **Assignee:** ...\n\n<body Markdown>`.

**6 — Return** the contents of `work.md` unchanged.

## Attachment cache and rendering rules

Detection is a pure, offline, recursive scan of the real ADF description body — no REST call at all when it finds nothing, regardless of whether a token is configured — for any `media` node shaped like:
- `attrs.type == "file"` (a generic attached file),
- `attrs.alt` ends in an image extension (`.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.bmp`).

Only when the scan matches does every attachment on the issue get downloaded and cached under the assets dir (`work.md.tmp/` by default — already covered by this repo's `*.tmp` gitignore pattern). Each placeholder then resolves by matching its `alt` — Jira's own `media.attrs.alt` holds the attachment's exact original filename — against `fields.attachment[].filename`, never the placeholder's `media-id`, which classic REST never exposes (only the media-services UUID `/map-markdown-adf` embeds):
1. The matched filename is an image → `![<filename>](work.md.tmp/<file>)`. When the placeholder also carries Jira's own reported `width`/`height`, a `<!-- media-size: width=<w> height=<h> -->` comment follows on its own line right after.
2. Not an image → a plain link `[<filename>](work.md.tmp/<file>)`.

The relative link is percent-encoded (spaces etc.) and always relative to `work.md`'s own directory. Unlike `/fetch-page`, there is no Draw.io/mermaid-sidecar rule at all — Jira issues never carry those.

## Degraded mode

No **Atlassian config** → `site`/`cloudId` empty; Preflight's Step 2 supplies `cloudId`. All other steps unchanged.

No **API token** with an embedded image or file present → Step 5's no-token branch runs; the issue's text and structure still return in full, with a note in place of each embedded image and no `.tmp` folder created.

A description with no embedded image or file never touches the Jira REST/attachment path at all, regardless of whether a token is configured.

## Gotchas

**The Atlassian MCP's `getJiraIssue` tool never returns real ADF for `description`**, even with `responseContentFormat: "adf"` — verified live: it returns an already-flattened Markdown-ish string with each embedded image as `![](blob:https://media.staging.atl-paas.net/?...&id=<media-uuid>&...)`, alt text always empty. That string is not valid JSON, so piping it into `/map-markdown-adf`'s `adf-to-md` raises `JSONDecodeError`. `assemble_work.py` fetches the real ADF separately over REST whenever a token is configured, and only falls back to this lossy string when it isn't.

## Verification

`python -m pytest plugins/atl/skills/fetch-work/tests/` (from the repo root) — header formatting, the conversion handoff, offline attachment-reference detection, attachment caching, filename-matched image/file resolution, the no-match and no-token notes, and the no-credentials degraded path (including the blob-image-reference swap), all mocked. The ADF-to-placeholder seam is covered at its own home, `python -m pytest plugins/atl/skills/map-markdown-adf/`.
