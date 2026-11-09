# Fetch work

Return a Jira **Work item** as Markdown from a key, URL, or selected Jira search result. REST v3 reads the real ADF description; `atl.py` converts ADF back to Markdown verbatim. Not twg: its body format drops ADF-only constructs. Comments come from twg into an unchanged sidecar.

## Steps

**1 — Parse input.**
- `https://<site>/browse/<key>` → `<site>`, `<key>`; `<site>` differs from Preflight `site` → pass `--site https://<site>`.
- Bare `<key>` or search hit key → Preflight `site`.

**2 — Fetch and assemble.**

```bash
python3 <skillDir>/scripts/atl.py fetch-work --issue-key <key> --config "<configPath>" --md-path work.md [--site https://<site>] [--assets-dir <dir>] [--attachments embedded|all]
```

Fetches `summary`, `status`, `issuetype`, `assignee`, ADF `description`; converts ADF to Markdown (media nodes → placeholders); applies Attachment rules. Writes `work.md`: `# <key> — <summary>`, then `**Status:** · **Type:** · **Assignee:**`, then body, then `## Attachments` when any. Assets default to `work.md.tmp/` beside `work.md`. Non-zero exit → report stderr (missing `cloudId`/`email`/`apiToken`, unsupported `atlassian-python-api`, or `error: ADF conversion failed: <reason>`); no `work.md` on conversion failure.

**3 — Fetch comments.** Same site as the work item:

```bash
<twg> jira workitem get <key> --comments --site https://<site> -o json --output-file work.comments.json
```

Keep the complete output unchanged beside `work.md`; no parser or extraction. Another Markdown filename → `<stem>.comments.json`. Command succeeded and output holds no comment-retrieval error → append `## Comments` with `[Comments](work.comments.json)` (relative link matching the saved filename), even when no comments exist. Failure → report it and append a comments-retrieval failure note instead of the link; keep the fetched work item.

**4 — Return** `work.md` unchanged, including its comments link or failure note, plus the assets dir path when `## Attachments` or body links point into it. Read the linked comments, image, or log file only when the task needs it.

## Attachment rules

- `--attachments embedded` (default) downloads attachments the description embeds and lists the rest; `all` downloads every attachment. Assets dir is gitignored via `*.tmp`; nothing downloaded → no assets dir.
- `.zip` → also extract to `<assets dir>/<file>.zip.extracted/` (absolute and `..` member paths stripped). Invalid zip → kept, not extracted.
- Body placeholders resolve by `alt` (original filename) against `fields.attachment[].filename`, never `media-id` (REST does not expose it).
  - Image → `![<filename>](work.md.tmp/<file>)`; if `width`/`height`, `display-width`, or `layout` known, next line `<!-- media-size: [width=<w> height=<h>] [display-width=<n>[%]] [layout=<layout>] -->`.
  - Other → `[<filename>](work.md.tmp/<file>)`.
- `## Attachments` (after body) lists each attachment the body does not embed, plus every `.zip` with its extracted files as nested links. Nothing to list → no section.
- Links percent-encoded, relative to `work.md`'s directory. No Draw.io or mermaid-sidecar rule (unlike Fetch page).

## Degraded mode

- Attachment named in the body but no longer attached → one-line note replaces it; rest of the body returned.
- `atl.py` unavailable or failing for a non-auth reason → `<twg> jira workitem get <key> --site https://<site> -o json --output-file work.json` and warn the description may lose ADF-only constructs. Auth or policy denial → stop and report; no fallback.
