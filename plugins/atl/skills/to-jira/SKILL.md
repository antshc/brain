---
name: to-jira
description: Create a Jira ticket (Story, Task, Bug, or Epic child) from user-provided context using the Atlassian MCP. Use when the user says "create a jira ticket/story/task/bug", "open a jira issue", "file this in jira", or wants context turned into a Jira issue, optionally under a parent epic.
---

# Create Jira Ticket

Turn user-provided context into a Jira issue via the Atlassian MCP.

## Atlassian Rovo MCP

When connected to `atlassian-rovo-mcp`, read settings from `.agent.env` in the repo root to avoid discovery calls and reduce token usage.

- If `.agent.env` does not exist, create it in the repo root with the keys below, then ask the user to fill in their values before continuing.
- Load these values and reuse them for every Atlassian MCP call:
  - **MUST** use Jira project key from `ATLASSIAN_JIRA_PROJECT_KEY` (e.g. `YOURPROJ`).
  - **MUST** use Confluence spaceId from `ATLASSIAN_CONFLUENCE_SPACE_ID` (e.g. `123456`).
  - **MUST** use cloudId from `ATLASSIAN_CLOUD_ID` (e.g. `https://yoursite.atlassian.net`) — do NOT call `getAccessibleAtlassianResources`.
  - **MUST** use `maxResults: 10` or `limit: 10` for ALL Jira JQL and Confluence CQL search operations.

`.agent.env` template:
```env
ATLASSIAN_JIRA_PROJECT_KEY=YOURPROJ
ATLASSIAN_CONFLUENCE_SPACE_ID=123456
ATLASSIAN_CLOUD_ID=https://yoursite.atlassian.net
```

## Inputs (infer from context; ask only if missing)
- **projectKey** — e.g. `PROJ`. Required.
- **issueType** — Story | Task | Bug | Epic. Default `Story`.
- **summary** — Title, one line, terse.
- **description** — body; may include tables, code blocks.
- **parent** — epic key (e.g. `PROJ-1234`) when the issue belongs under an epic.

## Steps
1. Resolve `cloudId`: when connected to `atlassian-rovo-mcp`, use `ATLASSIAN_CLOUD_ID` from `.agent.env` (see **Atlassian Rovo MCP**) and skip discovery; otherwise try the site host (`<site>.atlassian.net`) first, else call `getAccessibleAtlassianResources`.
2. Build the description from the **Output template** below.
3. If the story has a **Blocked by** section, create those blocking stories first (recurse), then create this one.
4. Create with `createJiraIssue` — pass `cloudId`, `projectKey`, `issueTypeName`, `summary`, `description`, and `parent` (epic key) when given.
5. Link blockers (see **Blocked by** rule).
6. Return the created key and `webUrl`.

## Blocked by
- When a story lists `Blocked by: <story>`, create the blocker(s) first, then this story.
- **If the blocker already exists, do NOT recreate or update it — only create the link.** Search for an existing issue by summary/key first; reuse it and skip creation.
- Link with `createIssueLink` using the "has to be done after" relation: this issue is `inward`, the blocker is `outward` (this issue "has to be done after" the blocker).
- Verify the exact link-type name via `getIssueLinkTypes` before linking; skip linking when `Blocked by: None`.

## Output template (description body, in order)
- **User story** — single line: `As a user, I want <goal>, so that <benefit>.`
- **Requirements** — bullet list (source "Capabilities" maps here).
- **Acceptance Criteria** — bullet list.
- **Implementation decisions** — bullet list (omit if none).
- **Contract changes** — prose + ADF tables (omit if none).

### Source → template mapping
| Source section        | Template section        |
| --------------------- | ----------------------- |
| Capabilities          | Requirements            |
| (derived from goal)   | User story              |
| Acceptance Criteria   | Acceptance Criteria     |
| Implementation decisions | Implementation decisions |
| Contract changes      | Contract changes        |

## Rules
- **Do not rephrase.** Carry the source wording verbatim into the ticket — do not reword, summarize, or "improve" requirements, acceptance criteria, implementation decisions, or contract changes. Only restructure into the template sections.
- **Only add a table when the source has one.** If the story's Contract changes (or any section) contains no table, do NOT invent one — keep the source's prose as-is. Never add empty or placeholder tables.
- **Tables → always ADF.** When the source does contain a table, markdown/wiki tables do NOT render: set `contentFormat: "adf"` and pass a `doc` with `table`/`tableRow`/`tableHeader`/`tableCell` nodes. Plain prose can stay markdown.
- **Fenced code → always ADF.** When the source contains a fenced code block (```...```), map it to an ADF `codeBlock` node (set `contentFormat: "adf"`); do not leave it as a markdown fence. Preserve the content verbatim, newlines included.
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
