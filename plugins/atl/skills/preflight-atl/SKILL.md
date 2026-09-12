---
name: preflight-atl
description: Resolve Atlassian connection facts (site, cloudId, default project key, default space id, token availability, MCP connection status) before any Jira or Confluence operation. Run first, from every other `atl` skill, before creating, searching, reading, or updating a Jira issue or Confluence page.
---

# Preflight

The resolution gate every other `atl` skill runs first. Never fails — an unresolved fact comes back empty and the caller degrades to what the MCP alone can do.

## Configuration

`.atlassian` — a single gitignored dotfile, found by a search bounded to `$HARNESS_REPO_PATH` (never above it, and never the filesystem root `/`). Plain `KEY=VALUE` lines; blank lines and `#` comments ignored.

| Key | Meaning |
|---|---|
| `ATLASSIAN_SITE` | Site host, e.g. `example.atlassian.net` |
| `ATLASSIAN_EMAIL` | Atlassian account email |
| `ATLASSIAN_API_TOKEN` | Optional — only for what the MCP can't do (e.g. attachment upload) |
| `ATLASSIAN_JIRA_PROJECT_KEYS` | Comma-separated Jira project keys, first = default |
| `ATLASSIAN_CONFLUENCE_SPACE_IDS` | Comma-separated Confluence space ids, first = default |
| `ATLASSIAN_DIAGRAM_RENDERER` | Optional — how `/publish-page` renders mermaid diagrams: `png` (default), `drawio`, or `mermaid` |
| `ATLASSIAN_DRAWIO_EXTENSION_KEY` | Required only by `ATLASSIAN_DIAGRAM_RENDERER=drawio` — the Draw.io macro's `<appId>/<envId>/static/drawio` key |

## Action: Resolve

Returns `site`, `cloudId`, `defaultProjectKey`, `defaultSpaceId`, `tokenAvailable`, `mcpConnected`. Never echo `ATLASSIAN_EMAIL` or `ATLASSIAN_API_TOKEN` — not in output, logs, or errors.

**1 — Config-derived facts (offline).** Resolve `$HARNESS_REPO_PATH` first: non-empty → use it as-is. Empty → resolve the repository root instead (e.g. `git rev-parse --show-toplevel`, falling back to cwd only if that fails) — **never** substitute `/` or leave the value blank, which would walk the whole filesystem. `cd` to the directory holding the `preflight-atl/SKILL.md` file you loaded to read this skill — never guess or reconstruct that path from a different skill's location — then run:

```bash
python scripts/preflight.py --root "<resolved repo root>"
```

Prints JSON with `site`, `cloudId`, `defaultProjectKey`, `defaultSpaceId`, `tokenAvailable`. `mcpConnected` is always `false` here — the script never touches the network; Step 3 sets the live value. An empty or filesystem-root `--root` exits non-zero naming the problem rather than searching — resolve a real root and re-run.

**2 — Discover `cloudId` only when the config supplies none.** `cloudId` empty and an operation needs it → call `getAccessibleAtlassianResources` once, then treat it as cached for the session. Once `cloudId` is known, never call it again. Step 1's `cloudId` is `https://<site>`, not a UUID — that's expected, not a sign of a missing discovery step: every Atlassian MCP tool's `cloudId` parameter accepts "UUID or site URL", so the site-URL form is valid as-is.

**3 — MCP connection status.** Call a lightweight tool (e.g. `atlassianUserInfo`). `mcpConnected := true` on success, `false` on any failure — never raise.

**4 — Report** the six fields before the caller's operation runs. Never restate `ATLASSIAN_EMAIL` or the raw token.

## Standing MCP usage rules

Apply in every `atl` skill:

- Every JQL/CQL search MUST use `maxResults: 10` / `limit: 10` — never more.
- Save large tool results to `content.json` and parse with Python, never `read_file` — long fields get silently truncated otherwise.
- `getAccessibleAtlassianResources` at most once per session, only while `cloudId` is unknown (Step 2).
- Never search for `.atlassian` (or anything else) from `/` or any other unbounded root — an empty `$HARNESS_REPO_PATH` is resolved to the repository root first (Step 1), never widened into a filesystem-wide search.

## Ambiguity

More than one configured project key or space id could apply → ask the developer which. Never choose silently.
