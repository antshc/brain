---
name: preflight-atlassian
description: Resolve Atlassian connection facts (cloudId, default project key, default space id, token availability) and parse this repo's `.atlassian.json.user` config. Run first from every `atl` skill before creating, searching, reading, or updating a Jira issue or Confluence page.
compatibility: Requires the Atlassian Rovo MCP server (`atlassianUserInfo`, `getAccessibleAtlassianResources`, plus each caller's Jira/Confluence search or content tools) for live identity and cloudId discovery; degrades to config-only facts without one.
---

# Preflight

Resolution gate every `atl` skill runs first. Never fails — unresolved facts return empty; caller degrades to MCP-only. Sole owner of locating and parsing `.atlassian.json.user` (gitignored, sibling of this `SKILL.md`); other skills MUST NOT re-implement it.

**MUST NOT echo** config `email`/`apiToken` or identity-response `email` — not in output, logs, or errors.

## Resolve

1. **Locate config.** From this skill's base directory run `python3 -c "from pathlib import Path; print(Path('.atlassian.json.user').resolve())"` → `configPath` (absolute; printed even when the file is absent).
2. **Read config.** From this skill's base directory run `python3 -c "from pathlib import Path; print(Path('.atlassian.json.user').read_text())"`.
   - Not found → keys take table Default; keys without Default resolve empty (`cloudId` → step 3, identity → step 4, project key/space id → ask per Ambiguity).
   - Found → file value wins; absent keys take Default. `email` and `apiToken` mandatory, never defaulted.
3. **cloudId.** Empty and needed → call `getAccessibleAtlassianResources` once per session; one resource → use it; several → ask developer. Local `https://<host>` is valid as-is — MCP `cloudId` accepts UUID or site URL.
4. **Identity.** `accountId` and `displayName` both set → skip. Either empty → call `atlassianUserInfo` once: success → `accountId := account_id`, `displayName := name`; failure → leave empty, never raise. Exception: `init-atl`'s connectivity gate always calls live, ignoring cache.
5. **Report** `configPath`, `cloudId`, `defaultProjectKey`, `defaultSpaceId`, `tokenAvailable`, `accountId`, `displayName`, `maxResults`, `limit` before the caller's operation.

**Config handoff:** `atl` scripts read the config themselves — pass `--config "<configPath>"`; never rebuild the path.

| Key | Meaning | API | Default |
|---|---|---|---|
| `cloudId` | MCP `cloudId` param; local value `https://<host>` (scheme required, e.g. brief-daily `webUrl`); else step 2 | Yes | — |
| `email` | Account email; mandatory when file exists | Yes | — |
| `apiToken` | Mandatory when file exists; only for non-MCP ops (e.g. attachment upload) | Yes | — |
| `jiraProjectKeys` | Project keys; first = default | Yes | — |
| `confluenceSpaceIds` | Space ids; first = default | Yes | — |
| `accountId` | Cached by `init-atl` from `atlassianUserInfo`; never hand-entered | Yes | — |
| `displayName` | Same origin as `accountId`; never hand-entered | No | — |
| `diagramRenderer` | `publish-page` mermaid rendering: `png` \| `drawio` \| `mermaid` | No | `png` |
| `drawioExtensionKey` | Required when `diagramRenderer: drawio`; `<appId>/<envId>/static/drawio` | Yes | — |
| `swimlaneDrawio` | `publish-page` only; routes `swimlane-beta` diagrams to native Mermaid-to-draw.io converter | No | — |
| `maxResults` | JQL page size | Yes | `10` |
| `limit` | CQL page size | Yes | `10` |

## Standing MCP usage rules

Apply in every `atl` skill:

- JQL/CQL searches use resolved `maxResults`/`limit`, unless the caller bundles its own extraction script and declares a higher cap.
- Large tool result → save to `content.json`, `cd` there, extract with Python (`read_file` silently truncates lines at ~2000 chars): `python3 -c "import json;d=json.load(open('content.json'));print(d['fields']['description'])"`. Unknown shape → `print(json.dumps(d, indent=2)[:2000])`.
- `getAccessibleAtlassianResources` at most once per session, only while `cloudId` unknown.
- No MCP tool found for the needed call (e.g. subagent session lacks the MCP connection) + `tokenAvailable` → REST fallback via `atlassian-python-api`, using `site` (from `cloudId`), `email`, `apiToken`; report `mcp` vs `rest` per call. Neither MCP nor token → surface the missing-MCP error, name the tool.

## Gotchas

- **MUST NOT search the filesystem** (`find`/`grep`/`ls -R`/`os.walk`) for this skill's directory or `.atlassian.json.user`. Base dir = parent of the `SKILL.md` path given in context; config is its sibling.
- **Long absolute paths in `python3 -c` or heredocs get corrupted by terminal line-wrapping.** `cd` to the directory and use relative filenames; multi-statement code → temp `.py` file run by name.