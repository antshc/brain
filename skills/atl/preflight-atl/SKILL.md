---
name: preflight-atl
description: Resolve Atlassian connection facts (site, cloudId, default project key, default space id, token availability, MCP connection status) before any Jira or Confluence operation. Run first, from every other `atl` skill, before creating, searching, reading, or updating a Jira issue or Confluence page.
---

# Preflight

The resolution gate every other `atl` skill runs first. Never fails — an unresolved fact comes back empty and the caller degrades to what the MCP alone can do.

## Configuration

`.atlassian` — a single gitignored dotfile, found by a search bounded to `$HARNESS_REPO_PATH` (never above it). Plain `KEY=VALUE` lines; blank lines and `#` comments ignored.

| Key | Meaning |
|---|---|
| `ATLASSIAN_SITE` | Site host, e.g. `example.atlassian.net` |
| `ATLASSIAN_EMAIL` | Atlassian account email |
| `ATLASSIAN_API_TOKEN` | Optional — only for what the MCP can't do (e.g. attachment upload) |
| `ATLASSIAN_JIRA_PROJECT_KEYS` | Comma-separated Jira project keys, first = default |
| `ATLASSIAN_CONFLUENCE_SPACE_IDS` | Comma-separated Confluence space ids, first = default |

## Action: Resolve

Returns `site`, `cloudId`, `defaultProjectKey`, `defaultSpaceId`, `tokenAvailable`, `mcpConnected`. Never echo `ATLASSIAN_EMAIL` or `ATLASSIAN_API_TOKEN` — not in output, logs, or errors.

**1 — Config-derived facts (offline).** From the directory holding this `SKILL.md`:

```bash
python3 scripts/preflight.py --root "$HARNESS_REPO_PATH"
```

Prints JSON with `site`, `cloudId`, `defaultProjectKey`, `defaultSpaceId`, `tokenAvailable`. `mcpConnected` is always `false` here — the script never touches the network; Step 3 sets the live value.

**2 — Discover `cloudId` only when the config supplies none.** `cloudId` empty and an operation needs it → call `getAccessibleAtlassianResources` once, then treat it as cached for the session. Once `cloudId` is known, never call it again.

**3 — MCP connection status.** Call a lightweight tool (e.g. `atlassianUserInfo`). `mcpConnected := true` on success, `false` on any failure — never raise.

**4 — Report** the six fields before the caller's operation runs. Never restate `ATLASSIAN_EMAIL` or the raw token.

## Standing MCP usage rules

Apply in every `atl` skill:

- Every JQL/CQL search MUST use `maxResults: 10` / `limit: 10` — never more.
- Save large tool results to `content.json` and parse with Python, never `read_file` — long fields get silently truncated otherwise.
- `getAccessibleAtlassianResources` at most once per session, only while `cloudId` is unknown (Step 2).

## Ambiguity

More than one configured project key or space id could apply → ask the developer which. Never choose silently.
