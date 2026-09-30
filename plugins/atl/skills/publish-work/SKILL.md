---
name: publish-work
description: Create or update a Jira work item from a summary and a Markdown description, over the MCP alone; falls back to the Jira REST API for attachments, which the MCP can't upload. Use when asked to create, open, file, or update a Jira work item/issue/story/task/bug/epic. No Atlassian config required.
argument-hint: '<summary>, <issueType>, <description-markdown>, [workItemKey], [projectKey], [parent], [attachments]'
---

# Publish Work

Create/update a Jira **Work item** over MCP. API token needed only for attachments.

## Inputs

Infer from context; ask only when required input missing.

- **summary** — required; terse one-line title.
- **issueType** — required; e.g. `Story`, `Task`, `Bug`, `Epic`.
- **description** — required; Markdown, verbatim.
- **workItemKey** — optional; named → update, not create.
- **projectKey** — optional; resolved in Step 5.
- **parent** — optional parent/epic key.
- **additional fields** — only explicitly supplied labels, priority, components, custom fields.
- **attachments** — optional local file paths.

## Workflow

**1 — Preflight.** Run `preflight-atlassian` (resolves cloudId, default project key, default space id, token availability, `.atlassian.json.user` config) **Action: Resolve**; use returned `cloudId`.

**2 — Re-read source.** Description from file → `read_file` it again now, even if already read this session; else a mid-session edit is missed and stale content published.

**3 — Detect ADF-only constructs.** Run `map-markdown-adf` **Action: Detect ADF-only constructs** on the re-read source as-is, before composing, trimming, or re-levelling anything. Detecting on drafted text misses constructs lost while drafting.

**4 — Assemble description; choose format.** Mirror source (see Rules).

- `adfOnly: false` → `contentFormat := "markdown"`; send `description` verbatim.
- `adfOnly: true` → run `map-markdown-adf` **Action: Convert Markdown to ADF**; `contentFormat := "adf"`; `description :=` result. Name reported construct kinds at completion.
- **Guard, always:** re-run Detect on final description as sent. Anything reported under `markdown` → convert, publish as `adf`, report construct kinds and lines that forced it. Only signal — Jira accepts it silently (see Gotchas).

**5 — Update or create.**

`workItemKey` named → **update**; never create a second item:
- `editJiraIssue` with `cloudId`, `issueIdOrKey: workItemKey`, `contentFormat`, `fields: {summary (if changed), description}`.
- Report key and `webUrl`; `attachments` → Step 6, else Step 7.

Else → **create**:
1. `projectKey`: supplied → use. Else Preflight `defaultProjectKey` if non-empty. Else `getVisibleJiraProjects`: one → use, report as resolved; several → ask, never choose silently.
2. `createJiraIssue` with `cloudId`, `projectKey`, `issueTypeName: issueType`, `summary`, `description`, `contentFormat`, `parent` (if named), `additional_fields` (supplied only).
3. Report only `issueKey` and `webUrl`.

No matching MCP tool for `editJiraIssue`/`createJiraIssue`/`getVisibleJiraProjects` → REST fallback per Preflight (`PUT`/`POST /rest/api/3/issue`, `GET /rest/api/3/project/search`).

**6 — Attach files.** Only when `attachments` supplied. MCP has no Jira upload tool → REST: `POST /rest/api/3/issue/{issueIdOrKey}/attachments`, header `X-Atlassian-Token: no-check`, multipart, auth `.atlassian.json.user` `site`/`email`/`apiToken` (see `preflight-atlassian`).

- `tokenAvailable: true` → upload each file to the issue key; report attached filenames with key and `webUrl`.
- `tokenAvailable: false` → keep create/update; report attachments not uploaded, `apiToken` missing. Never fail the call.

**7 — Verify live issue.** Only after `adf` publish. `getJiraIssue` with `cloudId`, `issueIdOrKey`, `fields: ["description"]`, `contentFormat: "adf"`; confirm each Step 3 construct is its ADF node (`expand`, `panel`, `status`) and combined marks merged, not literal `` ` ``. Missing → fix description, re-publish via Step 5. Read-only: **MUST NOT** re-run `editJiraIssue`/`createJiraIssue` with probe/placeholder content — overwrites the real publish.

## Gotchas

- `createJiraIssue`/`editJiraIssue` accept `<details>` under `markdown` silently; Jira renders it as literal text. Step 4 guard catches it.
- Echoed JSON proves acceptance, not rendering; `expand` or merged `code`+`link` marks can come back wrong. Step 7 reads the live issue.

## Markdown conversion

- Jira renders plain CommonMark natively under `markdown`: headings, lists, tables, fenced code, blockquotes, links, `**strong**`, `*em*`, `` `code` ``, `~~strike~~`, `---`.
- ADF-only constructs (e.g. `<details>`, `> [!INFO]`, `[STATUS:text|color]`) arrive as literal text under `markdown`. Source of truth: rows marked **ADF-only** in `map-markdown-adf`'s Supported structure table; don't re-derive.
- One physical line per bullet/paragraph.

## Rules

- **Do not rephrase.** Preserve wording, structure, tables, code, quotes verbatim; only encoding changes.
- **Mirror source headings** — exact text, level, order. Add none (e.g. `### Story` wrapper, `<summary>` promoted to heading).
- **Keep ADF-only constructs whole** — never flatten `<details>`, panels, lozenges into headings or paragraphs.
- Never invent fields, assignees, priorities, labels, components, custom-field values; set `additional_fields`/`parent` only from supplied values.
- Confirm with key and `webUrl`; don't repeat description.

## Degraded mode

No **Atlassian config** → `cloudId`/`defaultProjectKey` empty; Preflight Step 2 resolves `cloudId`, Step 5 project lookup resolves `projectKey` (ask when ambiguous). No token → see Step 6.
