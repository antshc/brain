---
name: publish-work
description: Create or update a Jira work item from a summary and a Markdown description, over the MCP alone; falls back to the Jira REST API for attachments, which the MCP can't upload. Use when asked to create, open, file, or update a Jira work item/issue/story/task/bug/epic. No Atlassian config required.
argument-hint: '<summary>, <issueType>, <description-markdown>, [workItemKey], [projectKey], [parent], [attachments]'
---

# Publish Work

Create or update a Jira **Work item** from a summary and a Markdown description. MCP only for create/update — no API token needed unless attachments are requested.

## Inputs

Infer from context; ask only when required information is missing.

- **summary** — required, terse one-line title.
- **issueType** — required, e.g. `Story`, `Task`, `Bug`, `Epic`.
- **description** — required, Markdown; preserved verbatim.
- **workItemKey** — optional; when named, update that item instead of creating one.
- **projectKey** — optional; resolved per Step 5 when omitted.
- **parent** — optional parent/epic key.
- **additional fields** — only labels, priority, components, or custom fields explicitly supplied.
- **attachments** — optional, local file paths to attach to the work item.

## Workflow

**1 — Preflight.** Run `/preflight-atl` skill **Action: Resolve**.

**2 — Resolve `cloudId`.** Preflight's `cloudId`; still empty → `getAccessibleAtlassianResources` once, per Preflight's standing rule.

**3 — Re-read the source.** `description` read from a file → `read_file` that file again now, immediately before extracting the content, even when this session already read it. An edit landing between the two reads is invisible otherwise, and the stale copy is what gets published.

**4 — Choose the content format.** Run `/map-markdown-adf` skill **Action: Detect ADF-only constructs** over `description`.

- `adfOnly: false` → `contentFormat := "markdown"`, and `description` goes out verbatim, unconverted.
- `adfOnly: true` → run `/map-markdown-adf` skill **Action: Convert Markdown to ADF**, `contentFormat := "adf"`, and `description := ` the resulting ADF. Name the reported construct kinds when confirming completion, so the extra conversion is visible.

**5 — Update or create.**

`workItemKey` named → **update**, never create a second item:
- `editJiraIssue` with `cloudId`, `issueIdOrKey: workItemKey`, `contentFormat`, `fields: {summary (if changed), description}`.
- Report the key and `webUrl`; proceed to Step 6 when `attachments` is supplied, otherwise stop.

Else → **create**:
1. Resolve `projectKey`: supplied → use it. Else Preflight's `defaultProjectKey` if non-empty. Else `getVisibleJiraProjects` — exactly one → use it and report it as resolved; more than one → ask, never choose silently (Preflight's Ambiguity rule).
2. `createJiraIssue` with `cloudId`, `projectKey`, `issueTypeName: issueType`, `summary`, `description`, `contentFormat`, `parent` (when named), `additional_fields` (supplied values only).
3. Report only `issueKey` and `webUrl`.

**6 — Attach files.** Only when `attachments` is supplied. The Atlassian MCP has no Jira attachment-upload tool — fall back to the REST API: `POST /rest/api/3/issue/{issueIdOrKey}/attachments` with header `X-Atlassian-Token: no-check`, multipart file upload, authenticated with `.atlassian`'s `ATLASSIAN_SITE`/`ATLASSIAN_EMAIL`/`ATLASSIAN_API_TOKEN` (same credential trio `publish-page` uses for its own REST fallback).

- Preflight's `tokenAvailable` is `true` → upload each file against the created/updated issue key; report the attached filenames alongside the key and `webUrl`.
- `tokenAvailable` is `false` → soft-degrade: the issue is still created/updated; report that attachments were not uploaded, naming `ATLASSIAN_API_TOKEN` as the missing prerequisite. Never fail the whole call over a missing token.

## Markdown conversion rules

Jira renders plain CommonMark natively under `contentFormat: "markdown"` — headings, bullet and ordered lists, tables, fenced code, blockquotes, links, `**strong**`, `*em*`, `` `code` ``, `~~strike~~`, and `---` all survive without a conversion step.

The rows `map-markdown-adf` marks **ADF-only** in its Supported structure table — `<details>` expands, `> [!INFO]` panels, `[STATUS:text|color]` lozenges, `<!-- confluence:toc -->`, `<!-- confluence:wide-table -->` — have no Markdown equivalent and arrive as literal text. Step 4's detection gate exists to catch exactly those; it is the single source of truth for the list, so read it there rather than re-deriving it here.

One physical line per bullet and paragraph keeps the two paths identical — `map-markdown-adf` folds soft-wrapped continuations, and Jira's own Markdown parser folds them too, but an unwrapped source removes the question.

## Rules

- **Do not rephrase.** Preserve the description's wording, structure, tables, code, and quotes verbatim; only the encoding changes between the two paths, never the content.
- Never invent fields, assignees, priorities, labels, components, or custom-field values.
- Set `additional_fields` and `parent` only from explicitly supplied values.
- Confirm completion with the key and `webUrl`; do not repeat the description.

## Degraded mode

No **Atlassian config** → `cloudId`/`defaultProjectKey` empty; Step 2's `getAccessibleAtlassianResources` resolves `cloudId`, Step 5's project-visibility lookup resolves `projectKey` (asking when ambiguous). All other steps unchanged.

No `ATLASSIAN_API_TOKEN` → Step 6 is skipped and reported as unresolved; create/update in Step 5 is unaffected either way.
