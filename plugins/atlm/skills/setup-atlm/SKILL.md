---
name: setup-atlm
description: Initialize Atlassian Rovo MCP configuration from `.atlmcp.env`. Use when setting up MCP credentials for Jira or Confluence, when `.atlmcp.env` is missing, or before any MCP-based Atlassian skill that needs cloudId, projectKey, or spaceId.
---

# Setup Atlassian MCP

Resolve cloudId, projectKey, and spaceId from `.atlmcp.env` in the `.env` so MCP-based Atlassian skills can skip discovery calls.

## Steps

**Step 1 — Check for `.atlmcp.env`**

Look for `.atlmcp.env` in the repo root or it subdirectories recursively.

- If it does **not** exist, create it with the template below and stop — ask the user to fill in their values before continuing:

```env
# Comma-separated list of Jira project keys
ATLASSIAN_JIRA_PROJECT_KEYS=YOURPROJ,OTHERPROJ
# Comma-separated list of Confluence space IDs
ATLASSIAN_CONFLUENCE_SPACE_IDS=123456,789012
# Atlassian site URL used as cloudId
ATLASSIAN_CLOUD_ID=https://yoursite.atlassian.net
```

**Step 2 — Parse values**

Load `.atlmcp.env` and extract:

| Variable | Parsing |
|---|---|
| `ATLASSIAN_JIRA_PROJECT_KEYS` | Split on `,`, trim whitespace, drop empty entries → array of project keys |
| `ATLASSIAN_CONFLUENCE_SPACE_IDS` | Split on `,`, trim whitespace, drop empty entries → array of space IDs |
| `ATLASSIAN_CLOUD_ID` | Use as-is — do **NOT** call `getAccessibleAtlassianResources` |

**Step 3 — Resolve projectKey**

- One entry → use it directly.
- Multiple entries → pick the one matching the calling context (e.g., matches a key mentioned by the user). If none match, ask the user which to use.

**Step 4 — Resolve spaceId**

- One entry → use it directly.
- Multiple entries → pick the one matching the calling context. If none match, ask the user which to use.

**Step 5 — Expose resolved values**

Return (make available to the calling skill):
- `cloudId` — value of `ATLASSIAN_CLOUD_ID`
- `projectKey` — resolved Jira project key
- `spaceId` — resolved Confluence space ID

**Step 6 — Set up `.github/copilot-instructions.md`**

Ensure `.github/copilot-instructions.md` exists in the repo root (create it and the `.github/` directory if missing). Append the `## Atlassian Rovo MCP` section below if it is not already present; if a stale version exists, replace it:

```markdown
## Atlassian Rovo MCP

Look for `.atlmcp.env` in the repo root or it subdirectories recursively:
- **MUST** use Jira project keys from `ATLASSIAN_JIRA_PROJECT_KEYS` (comma-separated; first = default).
- **MUST** use cloudId from `ATLASSIAN_CLOUD_ID` (do NOT call getAccessibleAtlassianResources).
- **MUST** use Confluence space IDs from `ATLASSIAN_CONFLUENCE_SPACE_IDS` (comma-separated; first = default, confirm if ambiguous).
- **MUST** use `maxResults: 10` or `limit: 10` for ALL Jira JQL and Confluence CQL search operations.
```

## Constraints

- **Never** call `getAccessibleAtlassianResources` — `ATLASSIAN_CLOUD_ID` is the cloudId.
- Use `maxResults: 10` or `limit: 10` for **all** Jira JQL and Confluence CQL search operations.
