---
name: fetch-work
description: >-
  Fetch a Jira work item as Markdown with attachments and a linked comments file. Use when asked to fetch, read, show, or summarize a Jira work item or issue, or get its attachments or comments. Use fetch-page for Confluence pages.
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

Fetches `summary`, `status`, `issuetype`, `assignee`, ADF `description` over REST v3; converts via *`map-markdown-adf` skill to convert Atlassian Document Format (ADF) back to Markdown, preserving source wording verbatim* **Action: Convert ADF to Markdown** (media nodes → placeholders); applies Attachment rules. Writes `work.md`: `# <key> — <summary>`, then `**Status:** · **Type:** · **Assignee:**`, then body, then `## Attachments` when any. `--assets-dir <dir>` overrides cache dir (default `work.md.tmp`, beside `work.md`).

**4 — Fetch comments.** *Run `twg` skill for Jira workitem comments via CLI*, using Preflight's credentialed `twg` command and the same site as the work item:

```bash
twg jira workitem get <key> --comments --site https://<site> -o json > work.comments.json
```

Save complete command output unchanged beside `work.md`; no parser or extraction. For another Markdown filename, use `<stem>.comments.json` beside it. Confirm command success and no comment-retrieval error in the output, then append `## Comments` with `[Comments](work.comments.json)` to `work.md` (relative link matching the saved filename). Keep the file and link even when no comments exist. On failure, report it and append a comments-retrieval failure note instead of a success link; keep the fetched work item.

**5 — Return** `work.md` contents unchanged, including its comments reference or failure note, plus the assets dir path when `## Attachments` or body links point into it. Read the linked comments, image, or log file when the task needs it.

## Attachment rules

- Always download every issue attachment to assets dir (gitignored via `*.tmp`); no attachments → no assets dir.
- `.zip` → also extract to `<assets dir>/<file>.zip.extracted/` (absolute and `..` member paths stripped). Invalid zip → kept, not extracted.
- Resolve each body placeholder by `alt` (original filename) against `fields.attachment[].filename`, never `media-id` (REST doesn't expose it).
  - Image → `![<filename>](work.md.tmp/<file>)`; if `width`/`height`, `display-width`, or `layout` known, next line `<!-- media-size: [width=<w> height=<h>] [display-width=<n>[%]] [layout=<layout>] -->`.
  - Other → `[<filename>](work.md.tmp/<file>)`.
- `## Attachments` (after body) lists each attachment the body doesn't embed, plus every `.zip` with its extracted files as nested links: image → `- ![<filename>](...)`, zip → `- [<file>.zip](...) · extracted to ...` then `  - [<member>](...)`, invalid zip → `· not a valid zip, not extracted`, other → `- [<filename>](...)`. Nothing to list → no section.
- Links percent-encoded, relative to `work.md`'s directory. No Draw.io/mermaid-sidecar rule (unlike `fetch-page` skill).

## Degraded mode

- No **Atlassian config** → Preflight asks for `site`; credentials still required.
- Attachment named in the body but no longer attached → one-line note replaces it; rest of the body returned.

## Gotchas

- **MUST NOT `find`/`grep`/`ls -R` to locate this skill's directory.** Use the parent of the `SKILL.md` path you were given.
- Keep comment output in the linked sidecar; only its reference or retrieval failure note goes into `work.md`. Other fields beyond the header → *follow `twg` skill for Jira workitems via CLI* with Preflight's credentialed command.
