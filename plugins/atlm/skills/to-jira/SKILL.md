---
name: to-jira
description: Create Jira work items from user-provided context using the Atlassian MCP. Use when the user asks to create, open, or file a Jira story, task, bug, epic, or child issue, optionally under a parent or with blockers.
---

The `cloudId`, `projectKey`, and `spaceId` should have been loaded from `.atlmcp.env` — run `/atlm:setup-atl-mcp` if not.

# Create Jira work item

Turn user-provided context into a Jira issue via the Atlassian MCP.

## Inputs

Infer from context; ask only when required information is missing.

- **projectKey** — required, for example `PROJ`.
- **issueType** — `Story`, `Task`, `Bug`, or `Epic`; default `Story`.
- **summary** — terse, one-line title.
- **description** — issue body; may contain Markdown.
- **parent** — parent or epic key, for example `PROJ-1234`.
- **additional fields** — labels, priority, components, or custom fields explicitly provided by the user.

## Description template

Use a user-provided `.template.md` file when available. Otherwise infer the structure from the source context.

## Workflow

1. Build the description using the supplied template when available.
2. Preserve the source wording; restructure only into template sections.
3. If the description contains Markdown that requires ADF, invoke the `markdown-to-adf` skill with the complete description. Use the returned ADF document as the description and set `contentFormat: "adf"`.
4. Resolve every item in **Blocked by** before creating the current issue:
   - Search by key or summary.
   - Reuse an existing issue without updating it.
   - Otherwise create the blocker recursively.
5. Create the issue with `createJiraIssue`, passing `cloudId`, `projectKey`, `issueTypeName`, `summary`, `description`, and `parent` when provided.
6. Link blockers using the verified Jira issue-link type.
7. Return only the created issue key and `webUrl`.

## Blocked by

- Skip linking when `Blocked by: None`.
- Call `getIssueLinkTypes` and verify the exact link-type name before linking.
- Use the **has to be done after** relationship:
  - current issue: `inward`
  - blocker: `outward`
- Never recreate or update an existing blocker solely to establish the link.

## Rules

- **Do not rephrase.** Preserve requirements, acceptance criteria, implementation decisions, contract changes, tables, code, and quotes verbatim.
- Do not invent sections, tables, fields, assignees, priorities, labels, components, or custom-field values.
- Add a table only when the source contains a table. Never add empty or placeholder tables.
- Set `parent` only when the user or source context identifies a parent.
- Use `additional_fields` only for values explicitly supplied by the user.
- Keep the summary terse and aligned with the user's wording.
- Confirm completion briefly with the issue key and URL; do not repeat the description.
