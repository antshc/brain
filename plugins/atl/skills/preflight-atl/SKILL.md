---
name: preflight-atl
description: Resolve Atlassian connection facts (site, cloudId, default project key, default space id, token availability, MCP connection status) before any Jira or Confluence operation. Run first, from every other `atl` skill, before creating, searching, reading, or updating a Jira issue or Confluence page.
---

# Preflight

The single resolution gate every other `atl` skill runs first. Never fails — an unresolved fact comes back empty and the caller degrades to what the MCP alone can do.

## Configuration

A single dotfile, `.atlassian`, gitignored, located by a search bounded to `$HARNESS_REPO_PATH` (never above it) per [Concept 0008](../../../../docs/concepts/0008-per-repo-config-resolution.md). Plain `KEY=VALUE` lines; blank lines and `#` comments are ignored.

| Key | Meaning |
|---|---|
| `ATLASSIAN_SITE` | Site host, e.g. `example.atlassian.net` |
| `ATLASSIAN_EMAIL` | Developer's Atlassian account email |
| `ATLASSIAN_API_TOKEN` | Optional API token — needed only for what the MCP can't do (e.g. attachment upload) |
| `ATLASSIAN_JIRA_PROJECT_KEYS` | Comma-separated Jira project keys, first = default |
| `ATLASSIAN_CONFLUENCE_SPACE_IDS` | Comma-separated Confluence space identifiers, first = default |

## Action: Resolve

Returns `site`, `cloudId`, `defaultProjectKey`, `defaultSpaceId`, `tokenAvailable`, `mcpConnected`. Never echoes `ATLASSIAN_EMAIL` or `ATLASSIAN_API_TOKEN`'s value anywhere — not in output, logs, or errors.

**Step 1 — Resolve config-derived facts (offline)**

Run, from the directory holding this `SKILL.md`:

```bash
python3 scripts/preflight.py --root "$HARNESS_REPO_PATH"
```

Prints a JSON object with `site`, `cloudId`, `defaultProjectKey`, `defaultSpaceId`, `tokenAvailable`. `mcpConnected` always comes back `false` from this script — it never touches the network; Step 3 sets the live value.

**Step 2 — Discover `cloudId` only when the config supplies none**

If `cloudId` is empty and an operation actually needs it, call `getAccessibleAtlassianResources` once, then treat the result as cached for the rest of this session. Once `cloudId` is known — config-supplied or discovered — never call `getAccessibleAtlassianResources` again this session.

**Step 3 — Check MCP connection status**

Call a lightweight Atlassian MCP tool (e.g. `atlassianUserInfo`). Set `mcpConnected` `true` on success, `false` on any failure — never raise; a failed connection check degrades the caller, it does not fail Preflight.

**Step 4 — Report**

State exactly the six fields above before the caller's Atlassian operation runs. Never restate `ATLASSIAN_EMAIL` or the raw token value.

## Standing MCP usage rules

Absorbed from the retired `configure-atlassian-mcp` skill — apply these in every `atl` skill, not just here:

- Every Jira JQL and Confluence CQL search MUST use `maxResults: 10` / `limit: 10` — never more than ten results.
- Large tool results are saved to `content.json`; parse it with Python, never `read_file` — long fields get silently truncated otherwise.
- `getAccessibleAtlassianResources` is forbidden once `cloudId` is resolved — call it at most once per session, only while `cloudId` is still unknown (see Step 2).

## Ambiguity

When an operation could apply to more than one configured Jira project key or Confluence space identifier, ask the developer which to use — never choose one silently.
