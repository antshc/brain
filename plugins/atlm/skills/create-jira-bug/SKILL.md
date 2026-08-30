---
name: create-jira-bug
description: Create a new ZIC Bug issue in Jira with all mandatory fields pre-filled from a known-good template. Use when the user asks to create/open a bug, file a bug, or "mirror"/clone a bug's required fields into a new empty ZIC bug.
---

# Create Jira Bug (ZIC)

Requires the `configure-atlassian-mcp` skill's setup (cloudId, project keys, confidentiality rules). Load it first if not already active.

## When to use

Use when the user wants a new **Bug** issue type created in the ZIC project without necessarily copying the summary/description content of another issue — only the mandatory field scaffolding needs to match so `createJiraIssue` doesn't fail validation.

## Why this is needed

`createJiraIssue` for ZIC Bugs fails with a long list of "is required" errors unless additional project-specific mandatory custom fields are populated (see below). These fields are not standard Jira fields and their required IDs/values must be supplied via `additional_fields`.

## Required fields for a ZIC Bug

Discovered via `getJiraIssueTypeMetaWithFields` (issueTypeId `10004`, project `ZIC`) and by inspecting an existing bug (e.g. ZIC-5824). Values below are simply reasonable/neutral defaults — swap the option `id`s if the user specifies different values (verify options via `getJiraIssueTypeMetaWithFields` if unsure).

| Field key | Name | Default value used | id |
| --- | --- | --- | --- |
| `components` | Components | e.g. "ZIC infra" | (component name) |
| `priority` | Priority | P2 | (priority name) |
| `versions` | Affects versions | current in-progress release, e.g. "10.10" | `14448` |
| `customfield_10050` | Found in Build | "1" | `10089` |
| `customfield_10051` | Found in Automation? | "No" | `10105` |
| `customfield_10055` | Bug source | "Internal" (required, no default id — pass `{"value": "Internal"}`) | — |
| `customfield_10069` | User Impact | ADF doc, free text | — |
| `customfield_10081` | Regression? | "No" | `10066` |
| `customfield_10082` | Severity | "Normal" | `10067` |
| `customfield_10091` | QA Bug Reviewer | user account, only if bug source is Internal | e.g. `70121:cd24a88a-03fe-4e08-bce6-d0831bd12c8b` |
| `customfield_10276` | Initiative | "ZIC" | `13020` |
| `customfield_10347` | To Platform | "---" | `16323` |
| `customfield_10348` | From Platform | "---" | `16320` |
| `customfield_12389` | Frequency of Use | "Low < 5%" | `34664` |
| `customfield_12390` | Likelihood | "Rare < 1%" | `34667` |
| `customfield_10014` | Epic Link | set only if the user gives/mirrors an epic (e.g. "ZIC-5488") | plain issue key string |

`customfield_10069` (User Impact) must be valid ADF, e.g.:
```json
{"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": "support team"}]}]}
```

Internal bugs additionally require both `customfield_10014` (Epic Link) and `customfield_10091` (QA Bug Reviewer) — omitting either causes:
`"Epic link is mandatory on internal bugs"` / `"QA Bug Reviewer is needed when bug source is internal"`.

## Steps

1. Ensure `.env/.atlmcp.env` is read for cloudId/project key (per `configure-atlassian-mcp`).
2. If mirroring an existing issue's field values, fetch it with `getJiraIssue` (`fields: ["*all"]`) and reuse its component/priority/version/custom-field option ids instead of the defaults above.
3. Call `createJiraIssue` with:
   - `projectKey`: from `ATLASSIAN_JIRA_PROJECT_KEYS` (default "ZIC")
   - `issueTypeName`: "Bug"
   - `summary`: user-provided or mirrored summary
   - `additional_fields`: the required-field map above (leave `description` unset/empty for an "empty" bug)
4. If Jira responds with more "`X` is required" or ADF-format errors, look up the missing field's key/options via `getJiraIssueTypeMetaWithFields` and retry — do not guess field ids blindly.
5. Return the new issue key and web URL to the user.
