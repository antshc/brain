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

Returns `site`, `cloudId`, `defaultProjectKey`, `defaultSpaceId`, `tokenAvailable`, `mcpConnected`, `accountId`, `displayName`. Never echo `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN`, or the `email` the identity call returns — not in output, logs, or errors.

**1 — Config-derived facts (offline).** Resolve `$HARNESS_REPO_PATH` first: non-empty → use it as-is. Empty → resolve the repository root instead (e.g. `git rev-parse --show-toplevel`, falling back to cwd only if that fails) — **never** substitute `/` or leave the value blank, which would walk the whole filesystem. `cd` to the directory holding the `preflight-atl/SKILL.md` file you loaded to read this skill — never guess or reconstruct that path from a different skill's location — then run:

```bash
python scripts/preflight.py --root "<resolved repo root>"
```

This is the entire CLI — no subcommand (e.g. no `resolve` argument), just `--root`. Prints JSON with `site`, `cloudId`, `defaultProjectKey`, `defaultSpaceId`, `tokenAvailable`. `mcpConnected` is always `false` here and `accountId`/`displayName` are absent — the script never touches the network; Step 3 sets all three. An empty or filesystem-root `--root` exits non-zero naming the problem rather than searching — resolve a real root and re-run.

**2 — Discover `cloudId` only when the config supplies none.** `cloudId` empty and an operation needs it → call `getAccessibleAtlassianResources` once, then treat it as cached for the session. Exactly one accessible resource → use it; more than one → ask the developer which site. Once `cloudId` is known, never call it again. Step 1's `cloudId` is `https://<site>`, not a UUID — that's expected, not a sign of a missing discovery step: every Atlassian MCP tool's `cloudId` parameter accepts "UUID or site URL", so the site-URL form is valid as-is.

**3 — MCP connection status and identity.** Call `atlassianUserInfo` once. `mcpConnected := true` on success, `false` on any failure — never raise. On success the same response also settles identity: `accountId := account_id`, `displayName := name`, both cached for the session. Resolve them here and nowhere else — never from a file, a prior report, or by asking the developer. On failure both come back empty.

**4 — Report** the eight fields before the caller's operation runs. Never restate `ATLASSIAN_EMAIL`, the raw token, or the identity response's `email`.

## Standing MCP usage rules

Apply in every `atl` skill:

- Every JQL/CQL search uses `maxResults: 10` / `limit: 10`, unless the calling skill bundles its own extraction script and declares a higher cap in its own text — `/brief-daily` declares 25 on that basis. A skill reading results by hand stays at 10.
- Save a large tool result to `content.json` and read fields out of it with Python — `read_file` truncates a long line at roughly 2000 characters and loses the rest silently. `cd` to the file's directory first, then:

  ```bash
  python3 -c "import json;d=json.load(open('content.json'));print(d['fields']['description'])"
  ```

  Swap the key path for the field you want; `print(json.dumps(d, indent=2)[:2000])` when the shape is still unknown.
- `getAccessibleAtlassianResources` at most once per session, only while `cloudId` is unknown (Step 2).
- Never search for `.atlassian` (or anything else) from `/` or any other unbounded root — an empty `$HARNESS_REPO_PATH` is resolved to the repository root first (Step 1), never widened into a filesystem-wide search.

## Gotchas

**A long absolute path inside `python3 -c "..."` or a heredoc gets corrupted by terminal line-wrapping**, and the command then fails on a path that looks correct in the transcript. `cd` into the directory and use a relative filename; anything longer than one short statement goes into a temp `.py` file that gets run by name.

**`python scripts/preflight.py` resolves against the current directory.** Run from anywhere else it fails with `No such file or directory` naming the script — Step 1's `cd` to the directory holding `preflight-atl/SKILL.md` is the fix, not a formality.

## Ambiguity

More than one configured project key or space id could apply → ask the developer which. Never choose silently. Same rule for more than one accessible site in Step 2.
