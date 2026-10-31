---
name: publish-work
description: >-
  Create or update a Jira work item from a summary and a Markdown description, converting via map-markdown-adf and publishing ADF over Jira REST with one script, attachments included. Use when asked to create, open, file, or update a Jira work item/issue/story/task/bug/epic. Needs `apiToken` in `.atlassian.json.user`.
argument-hint: '<summary>, <issueType>, <description-markdown>, [workItemKey], [projectKey], [parent], [attachments]'
---

# Publish Work

Create/update a Jira **Work item** over REST v3 with an ADF description. Not twg: only *`map-markdown-adf` skill* carries `<details>`, panels, status lozenges, TOC, and wide tables intact.

## Inputs

Infer from context; ask only when required input missing.

- **summary** — required; terse one-line title.
- **issueType** — required; e.g. `Story`, `Task`, `Bug`, `Epic`.
- **description** — required; Markdown, verbatim.
- **workItemKey** — optional; named → update, not create.
- **projectKey** — optional; resolved in Step 5.
- **parent** — optional parent/epic key.
- **additionalFields** — only explicitly supplied labels, priority, components, custom fields, as a Jira REST `fields` object.
- **attachments** — optional local file paths.

## Prerequisites

- `atlassian-python-api` installed by `init-atl` skill; if missing, *run `init-atl` skill for first-run setup of `.atlassian.json.user` and Atlassian dependencies* first.
- `cloudId`, `email`, `apiToken` in `.atlassian.json.user`; script exits non-zero naming them.

## Workflow

**1 — Preflight.** *Run `preflight-atlassian` skill to resolve site, default project key, credentialed twg command, and token availability from `.atlassian.json.user` config* **Action: Resolve**; keep `configPath`, `twg`. `tokenAvailable` false → report missing `apiToken`, stop.

**2 — Re-read source.** Description from file → `read_file` it again now, even if already read this session; else a mid-session edit is missed and stale content published.

**3 — Detect ADF-only constructs.** *Run `map-markdown-adf` skill to detect the constructs only ADF can express, preserving source wording verbatim* **Action: Detect ADF-only constructs** on the re-read source as-is, before composing, trimming, or re-levelling anything → `constructs` for Step 7.

**4 — Convert.** Mirror source (see Rules) into `description.md`, then *run `map-markdown-adf` skill to convert Markdown to Atlassian Document Format, preserving source wording verbatim* **Action: Convert Markdown to ADF** → `description.json`. `additionalFields` supplied → write `fields.json`. Keep both beside the source in `<source>.tmp/` (gitignored via `*.tmp`).

**5 — Update or create.** From this skill's directory (see Gotchas):

`workItemKey` named → **update**; never create a second item:
```bash
python3 scripts/publish_work.py update --config "<configPath>" --key <workItemKey> --adf <description.json> [--summary "<summary>"] [--fields-json <fields.json>] [--attach <path> ...]
```
Pass `--summary` only when changed.

Else → **create**:
1. `projectKey`: supplied → use. Else Preflight `defaultProjectKey` if non-empty. Else `<twg> jira space query --action create --limit 25`: one → use, report as resolved; several → ask, never choose silently.
2. Run:
```bash
python3 scripts/publish_work.py create --config "<configPath>" --project <projectKey> --issue-type "<issueType>" --summary "<summary>" --adf <description.json> [--parent <KEY>] [--fields-json <fields.json>] [--attach <path> ...]
```

Stdout `{"key":..., "url":..., "attached":[...], "attachFailed":[{"file","error"}]}` (attachment keys only with `--attach`). Non-zero exit → report stderr (`Jira rejected the request: <Jira message>`); nothing created. Required-field error → *follow `twg` skill for Jira field metadata* with `<twg> jira workitem field create-metadata --space <projectKey> --type "<issueType>"`, ask for the missing values, re-run.

**6 — Report** `key` and `url`; `attached` filenames; each `attachFailed` file with its error. Never fail the call for an attachment.

**7 — Verify live issue.** Only when Step 3 found constructs. `python3 scripts/publish_work.py read-adf --config "<configPath>" --key <key> --out <live.json>`; confirm each construct is its ADF node (`expand`, `panel`, `status`) and combined marks merged, not literal `` ` ``. Missing → fix `description.md`, re-run Step 4–5 as update. Read-only: **MUST NOT** re-run `create`/`update` with probe/placeholder content — overwrites the real publish.

## Rules

- **Do not rephrase.** Preserve wording, structure, tables, code, quotes verbatim; only encoding changes.
- **Mirror source headings** — exact text, level, order. Add none (e.g. `### Story` wrapper, `<summary>` promoted to heading).
- **Keep ADF-only constructs whole** — never flatten `<details>`, panels, lozenges into headings or paragraphs. Source of truth: rows marked **ADF-only** in `map-markdown-adf` skill's Supported structure table; don't re-derive.
- One physical line per bullet/paragraph.
- Never invent fields, assignees, priorities, labels, components, custom-field values; `--fields-json`/`--parent` only from supplied values.
- Confirm with key and `url`; don't repeat description.

## Degraded mode

No **Atlassian config** → Preflight asks for `site`; Step 5 project lookup resolves `projectKey` (ask when ambiguous). No token → nothing published; report missing `apiToken`.

## Gotchas

- **MUST NOT `find`/`grep`/`ls -R` to locate this skill's directory.** Use the parent of the `SKILL.md` path you were given.
- Echoed key proves acceptance, not rendering; Step 7 reads the live issue.
- REST v3 rejects a Markdown `description`; always send Step 4's ADF.
