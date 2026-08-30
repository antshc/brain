---
name: publish-work
description: Create or update a Jira work item from a summary and a Markdown description, over the MCP alone. Use when asked to create, open, file, or update a Jira work item/issue/story/task/bug/epic. No Atlassian config required. Absorbs `to-jira` and `create-jira-bug`.
argument-hint: '<summary>, <issueType>, <description-markdown>, [workItemKey], [projectKey], [parent]'
---

# Publish Work

Create or update a Jira **Work item** from a summary and a Markdown description, over the MCP alone — no `acli`, no API token.

## Inputs

Infer from context; ask only when required information is missing.

- **summary** — required, terse one-line title.
- **issueType** — required, e.g. `Story`, `Task`, `Bug`, `Epic`.
- **description** — required, Markdown; preserved verbatim, never rephrased.
- **workItemKey** — optional; when named, update that work item instead of creating one.
- **projectKey** — optional; when omitted, resolved per Step 4.
- **parent** — optional parent/epic key.
- **additional fields** — only labels, priority, components, or custom fields the developer explicitly supplied.

## Workflow

**Step 1 — Preflight**
Run `/preflight-atl`' skill **Action: Resolve**.

**Step 2 — Resolve `cloudId`**
Use Preflight's `cloudId`. Still empty → call `getAccessibleAtlassianResources` once and use the matching resource's `cloudId`. Never call it again this session once resolved.

**Step 3 — Convert**
Run `/map-markdown-adf`' skill **Action: Convert Markdown to ADF**, piping `description` in. Use the resulting ADF document as `description` and set `contentFormat: "adf"` on every downstream call.

**Step 4 — Update or create**

`workItemKey` named → **update**, never create a second work item:
- Call `editJiraIssue` with `cloudId`, `issueIdOrKey: workItemKey`, `contentFormat: "adf"`, `fields: {summary (if changed), description}`.
- Report the updated key and `webUrl`; stop here.

`workItemKey` not named → **create**:
1. Resolve `projectKey`:
   - Developer supplied one → use it.
   - Else Preflight's `defaultProjectKey` is non-empty → use it.
   - Else call `getVisibleJiraProjects`. Exactly one visible project → use it, reporting it as the resolved default. More than one → ask the developer which project to use — never choose one silently, per Preflight's Ambiguity rule.
2. Call `createJiraIssue` with `cloudId`, `projectKey`, `issueTypeName: issueType`, `summary`, `description`, `contentFormat: "adf"`, `parent` (when named), `additional_fields` (only developer-supplied values).
3. Report only the created `issueKey` and `webUrl`.

## Rules

- **Do not rephrase.** Preserve the description's wording, structure, and any tables/code/quotes verbatim — `map-markdown-adf` handles structure; content itself is never rewritten.
- Never invent fields, assignees, priorities, labels, components, or custom-field values.
- Set `additional_fields` only for values the developer explicitly supplied.
- Set `parent` only when the developer or source context names one.
- Confirm completion briefly with the work item key and `webUrl`; do not repeat the description.

## Degraded mode

No **Atlassian config** file → Preflight's `cloudId`/`defaultProjectKey` come back empty; Step 2's `getAccessibleAtlassianResources` fallback resolves `cloudId`, and Step 4's project-visibility lookup resolves `projectKey` (asking the developer when ambiguous). Every other step is unchanged.
