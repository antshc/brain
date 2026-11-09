# Publish work

Create or update a Jira **Work item** over REST v3 with an ADF description. Not twg: only `atl.py`'s Markdown → ADF conversion carries `<details>`, panels, status lozenges, TOC, and wide tables intact. Repeated publishes (one per story, wrapper call, or batch row) reuse the same Preflight result and run this tactic once per item.

## Inputs

Infer from context; ask only when required input is missing.

- **summary** — required; terse one-line title.
- **issueType** — required for create; e.g. `Story`, `Task`, `Bug`, `Epic`.
- **description** — required for create; Markdown, verbatim.
- **workItemKey** — optional; named → update, never create.
- **projectKey** — optional; resolved in Step 4.
- **parent** — optional parent/epic key.
- **additionalFields** — only explicitly supplied labels, priority, components, custom fields, as a Jira REST `fields` object.
- **attachments** — optional local file paths.

## Steps

**1 — Re-read source.** Description from a file → read it again now, even if already read this session; else a mid-session edit is missed and stale content published.

**2 — Detect ADF-only constructs** on the re-read source as-is, before composing or re-levelling anything: `python3 <skillDir>/scripts/atl.py map-markdown detect-adf-only < <source.md>` → `constructs` for Step 6.

**3 — Prepare.** Mirror the source (see Rules) into `<source>.tmp/description.md` (gitignored via `*.tmp`). `additionalFields` supplied → write `<source>.tmp/fields.json`.

**4 — Update or create.**

`workItemKey` named → **update**; pass `--summary` only when changed:
```bash
python3 <skillDir>/scripts/atl.py publish-work update --config "<configPath>" --key <workItemKey> --markdown <description.md> [--summary "<summary>"] [--fields-json <fields.json>] [--attach <path> ...]
```

Else → **create**:
1. `projectKey`: supplied → use. Else Preflight `defaultProjectKey` if non-empty. Else `<twg> jira space query --action create --limit 25`: one → use, report as resolved; several → ask, never choose silently.
2. Run:
```bash
python3 <skillDir>/scripts/atl.py publish-work create --config "<configPath>" --project <projectKey> --issue-type "<issueType>" --summary "<summary>" --markdown <description.md> [--parent <KEY>] [--fields-json <fields.json>] [--attach <path> ...]
```

`--adf <description.json>` replaces `--markdown` when a caller already holds ADF.

Stdout `{"key":..., "url":..., "attached":[...], "attachFailed":[{"file","error"}]}` (attachment keys only with `--attach`).

| Failure | Meaning | Do |
|---|---|---|
| `error: Jira rejected the request: <message>` | Jira refused; nothing created or changed | Required-field error → `<twg> jira workitem field create-metadata --space <projectKey> --type "<issueType>"`, ask for the missing values, re-run |
| `error: Jira request outcome unknown (...)` | Connection dropped or timed out; the item may exist | **MUST NOT** re-run `create`. Search `<twg> jira workitem query --jql 'project = <projectKey> AND summary ~ "<summary>" AND created >= -1d'`; found → continue with `update --key`; not found → report and ask before creating |
| `error: Markdown conversion failed: <reason>` | Source rejected before any call | Fix the Markdown, re-run |
| `attachFailed` entries | Item exists; those files did not attach | Keep the `key`; retry only them: `atl.py publish-work update --config "<configPath>" --key <key> --attach <path> ...` (fields untouched) |

**5 — Report** `key` and `url`; `attached` filenames; each `attachFailed` file with its error. Never fail the call for an attachment; never drop a created key from the report.

**6 — Verify live issue.** Only when Step 2 found constructs: `python3 <skillDir>/scripts/atl.py publish-work read-adf --config "<configPath>" --key <key> --out <source>.tmp/live.json`; confirm each construct is its ADF node (`expand`, `panel`, `status`) and combined marks merged, not literal `` ` ``. Missing → fix `description.md`, re-run Step 4 as update. Read-only: **MUST NOT** re-run `create`/`update` with probe or placeholder content; it overwrites the real publish.

## Rules

- **Do not rephrase.** Preserve wording, structure, tables, code, quotes verbatim; only encoding changes.
- **Mirror source headings**: exact text, level, order. Add none (e.g. `### Story` wrapper, `<summary>` promoted to heading).
- **Keep ADF-only constructs whole**: never flatten `<details>`, panels, lozenges into headings or paragraphs. Source of truth: Step 2's `constructs`; do not re-derive.
- One physical line per bullet or paragraph.
- Never invent fields, assignees, priorities, labels, components, custom-field values; `--fields-json`/`--parent` only from supplied values.
- Confirm with key and `url`; do not repeat the description.

## Degraded mode

No Atlassian config → Preflight asks for `site`; Step 4 project lookup resolves `projectKey` (ask when ambiguous). No token → nothing published; report missing `apiToken`.

## Gotchas

- Echoed key proves acceptance, not rendering; Step 6 reads the live issue.
- REST v3 rejects a Markdown `description`; `atl.py` always sends ADF.
