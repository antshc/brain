---
name: configure-atlassian-mcp
description: Configure and use the Atlassian Rovo MCP for Jira and Confluence work in this repo. Use when creating, searching, reading, or updating Jira issues or Confluence pages, or when resolving Atlassian cloudId, project keys, or space IDs.
---

# Atlassian Rovo MCP

Applies only when the Atlassian Rovo MCP is connected. Read configuration values from `.env/.atlmcp.env` (relative to the reporoot).

## Confidentiality

- You MUST NOT print, commit, quote, or include `.env` values in issues, logs, documentation, or responses.
- You MUST NOT search outside the reporoot for `.env/.atlmcp.env`.

## Required configuration

- You MUST use Jira project keys from `ATLASSIAN_JIRA_PROJECT_KEYS` (comma-separated; first = default).
- You MUST use cloudId from `ATLASSIAN_CLOUD_ID` (do not call `getAccessibleAtlassianResources`).
- You MUST use Confluence space IDs from `ATLASSIAN_CONFLUENCE_SPACE_IDS` (comma-separated; first = default, confirm if ambiguous).
- You MUST use `maxResults: 10` or `limit: 10` for ALL Jira JQL and Confluence CQL search operations.

## Reading large tool results

Large Jira/Confluence results are saved to `content.json`. You MUST ALWAYS parse it with Python, never `read_file` — long fields (e.g. `description`) get silently truncated at 2000 chars/line otherwise. Applies to reads and edit-verification alike.

```bash
python3 -c "
import json
with open('<path-to-content.json>') as f:
    d = json.load(f)
print(d['issues']['nodes'][0]['fields']['description'])  # adjust path as needed
"
```
