---
name: to-jira
description: Create a Jira story (or Task, Bug, or Epic child) from user-provided context using the Atlassian MCP. Use when the user says "create a jira ticket/story/task/bug", "open a jira issue", "file this in jira", or wants context turned into a Jira issue, optionally under a parent epic.
---

The `cloudId`, `projectKey`, and `spaceId` should have been loaded from `.atlmcp.env` — run `/atlm:setup-atl-mcp` if not.

# Create Jira Work item

Turn user-provided context into a Jira issue via the Atlassian MCP.

## Inputs (infer from context; ask only if missing)
- **projectKey** — e.g. `PROJ`. Required.
- **issueType** — Story | Task | Bug | Epic. Default `Story`.
- **summary** — Title, one line, terse.
- **description** — body; may include tables, code blocks.
- **parent** — epic key (e.g. `PROJ-1234`) when the issue belongs under an epic.

## Output template (description body)
Provide by user as .template.md file, or infer from context.

## Steps

1. Build the description from the **Output template** if available.
2. If the work item has a **Blocked by** section, create those blocking work items first (recurse), then create this one.
3. Create with `createJiraIssue` — pass `cloudId`, `projectKey`, `issueTypeName`, `summary`, `description`, and `parent` (epic key) when given.
4. Link blockers (see **Blocked by** rule).
5. Return the created key and `webUrl`.

## Blocked by
- When a work item lists `Blocked by: <work item>`, create the blocker(s) first, then this work item.
- **If the blocker already exists, do NOT recreate or update it — only create the link.** Search for an existing work item by summary/key first; reuse it and skip creation.
- Link with `createIssueLink` using the "has to be done after" relation: this work item is `inward`, the blocker is `outward` (this work item "has to be done after" the blocker).
- Verify the exact link-type name via `getIssueLinkTypes` before linking; skip linking when `Blocked by: None`.

## Rules
- **Do not rephrase.** Carry the source wording verbatim into the ticket — do not reword, summarize, or "improve" requirements, acceptance criteria, implementation decisions, or contract changes. Only restructure into the template sections.
- **Only add a table when the source has one.** If the story's Contract changes (or any section) contains no table, do NOT invent one — keep the source's prose as-is. Never add empty or placeholder tables.
- **Tables → always ADF.** When the source does contain a table, markdown/wiki tables do NOT render: set `contentFormat: "adf"` and pass a `doc` with `table`/`tableRow`/`tableHeader`/`tableCell` nodes. Plain prose can stay markdown.
- **Fenced code → always ADF.** When the source contains a fenced code block (```...```), map it to an ADF `codeBlock` node (set `contentFormat: "adf"`); do not leave it as a markdown fence. Preserve the content verbatim, newlines included.
- **Bullet lists → always ADF.** Map GFM `-`, `*`, and `+` list markers to nested ADF `bulletList` nodes. Preserve nesting up to level 3. Each `bulletList` contains `listItem` nodes; nested lists belong inside the parent `listItem`, after its paragraph.
- **Block quotes → always ADF.** Map GFM `>` block quotes to an ADF `blockquote` node. Preserve the quoted content verbatim; do not emit a literal `>` in ADF.
- Set `parent` to the epic key to attach under an epic (works for company-managed projects).
- Wrap endpoint paths / identifiers in inline `code` marks in ADF.
- Do not invent fields, assignees, or priorities — only set what the user provides (use `additional_fields` for labels/priority/components/custom fields).
- Keep summary terse; mirror the user's wording.
- Confirm briefly with key + URL; do not restate the whole description.

## ADF table skeleton
```json
{ "type": "table", "attrs": { "isNumberColumnEnabled": false, "layout": "default" },
  "content": [
    { "type": "tableRow", "content": [
      { "type": "tableHeader", "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Col" }] }] }
    ]},
    { "type": "tableRow", "content": [
      { "type": "tableCell", "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "val" }] }] }
    ]}
  ]
}
```

## ADF code block skeleton
```json
{ "type": "codeBlock", "attrs": { "language": "text" },
  "content": [{ "type": "text", "text": "line1\nline2" }]
}
```

## ADF bullet list skeleton

GFM input:
```markdown
- Level 1
  - Level 2
    - Level 3
```

ADF:
```json
{
  "type": "bulletList",
  "content": [
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [{ "type": "text", "text": "Level 1" }]
        },
        {
          "type": "bulletList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{ "type": "text", "text": "Level 2" }]
                },
                {
                  "type": "bulletList",
                  "content": [
                    {
                      "type": "listItem",
                      "content": [
                        {
                          "type": "paragraph",
                          "content": [{ "type": "text", "text": "Level 3" }]
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## ADF blockquote skeleton

GFM input:
```markdown
> Quote
>
> Second paragraph
```

ADF:
```json
{
  "type": "blockquote",
  "content": [
    {
      "type": "paragraph",
      "content": [{ "type": "text", "text": "Quote" }]
    },
    {
      "type": "paragraph",
      "content": [{ "type": "text", "text": "Second paragraph" }]
    }
  ]
}
```
