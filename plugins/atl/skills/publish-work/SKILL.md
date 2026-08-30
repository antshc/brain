---
name: publish-work
description: Create or update a Jira work item from a summary and a Markdown description, over the MCP alone. Use when asked to create, open, file, or update a Jira work item/issue/story/task/bug/epic. No Atlassian config required.
argument-hint: '<summary>, <issueType>, <description-markdown>, [workItemKey], [projectKey], [parent]'
---

# Publish Work

Create or update a Jira **Work item** from a summary and a Markdown description. MCP only — no API token.

## Inputs

Infer from context; ask only when required information is missing.

- **summary** — required, terse one-line title.
- **issueType** — required, e.g. `Story`, `Task`, `Bug`, `Epic`.
- **description** — required, Markdown; preserved verbatim.
- **workItemKey** — optional; when named, update that item instead of creating one.
- **projectKey** — optional; resolved per Step 4 when omitted.
- **parent** — optional parent/epic key.
- **additional fields** — only labels, priority, components, or custom fields explicitly supplied.

## Workflow

**1 — Preflight.** Run `/preflight-atl` **Action: Resolve**.

**2 — Resolve `cloudId`.** Preflight's `cloudId`; still empty → `getAccessibleAtlassianResources` once, per Preflight's standing rule.

**3 — Convert.** Pipe `description` into `/map-markdown-adf` **Action: Convert Markdown to ADF**. Use the resulting ADF as `description` and set `contentFormat: "adf"` on every downstream call.

**4 — Update or create.**

`workItemKey` named → **update**, never create a second item:
- `editJiraIssue` with `cloudId`, `issueIdOrKey: workItemKey`, `contentFormat: "adf"`, `fields: {summary (if changed), description}`.
- Report the key and `webUrl`; stop.

Else → **create**:
1. Resolve `projectKey`: supplied → use it. Else Preflight's `defaultProjectKey` if non-empty. Else `getVisibleJiraProjects` — exactly one → use it and report it as resolved; more than one → ask, never choose silently (Preflight's Ambiguity rule).
2. `createJiraIssue` with `cloudId`, `projectKey`, `issueTypeName: issueType`, `summary`, `description`, `contentFormat: "adf"`, `parent` (when named), `additional_fields` (supplied values only).
3. Report only `issueKey` and `webUrl`.

## Rules

- **Do not rephrase.** Preserve the description's wording, structure, tables, code, and quotes verbatim — `map-markdown-adf` handles structure.
- Never invent fields, assignees, priorities, labels, components, or custom-field values.
- Set `additional_fields` and `parent` only from explicitly supplied values.
- Confirm completion with the key and `webUrl`; do not repeat the description.

## Degraded mode

No **Atlassian config** → `cloudId`/`defaultProjectKey` empty; Step 2's `getAccessibleAtlassianResources` resolves `cloudId`, Step 4's project-visibility lookup resolves `projectKey` (asking when ambiguous). All other steps unchanged.
