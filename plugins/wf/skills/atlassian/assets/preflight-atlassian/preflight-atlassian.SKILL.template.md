---
name: preflight-atlassian
description: >-
  Resolve Atlassian connection facts (site, default project key, default space id, token availability, credentialed twg command) from this repo's `.atlassian.json.user` config. Internal gate for `atlassian`, not a user entry point. Not for Jira or Confluence operations → `atlassian`.
compatibility: Requires the `twg` CLI and an Atlassian API token (`email` + `apiToken`); twg and the REST scripts share those credentials.
---

# Preflight

Resolution gate the `atlassian` and `daily-briefing` skills run first. Never fails — unresolved facts return empty; caller names the missing prerequisite. Sole owner of locating and parsing `.atlassian.json.user` (gitignored, sibling of this `SKILL.md`); other skills MUST NOT re-implement it.

**MUST NOT echo** config `email`/`apiToken` or identity-response `email` — not in output, logs, errors, or command lines.

## Routing

Preflight resolves facts only; never creates/updates content. Request is the operation itself → hand off to the owning skill, which runs Preflight first:

- Fetch, publish, convert, search, or operate on Jira or Confluence content, or address page review comments → *run `atlassian` skill to fetch, publish, convert, and query Jira and Confluence content and address page comments (Fetch work, Publish work, Fetch page, Publish page, Address page comments, Map Markdown, TWG)*.
- Daily blocked items and @mentions → *run `daily-briefing` skill for the daily briefing, standup update, and unanswered mentions*.

## Resolve

1. **Locate config.** From this skill's base directory run `python3 -c "from pathlib import Path; print(Path('.atlassian.json.user').resolve())"` → `configPath` (absolute; printed even when the file is absent).
2. **Read config.** From this skill's base directory run `python3 -c "import json;from pathlib import Path;p=Path('.atlassian.json.user');d=json.loads(p.read_text()) if p.exists() else {};print(json.dumps({k:(bool(v) if k in ('email','apiToken') else v) for k,v in d.items()}))"` (credentials print as presence booleans).
   - Not found → keys take table Default; keys without Default resolve empty (`site` → step 3, identity → step 5, project key/space id → ask per caller).
   - Found → file value wins; absent keys take Default. `tokenAvailable := email and apiToken both true`.
3. **site.** `site :=` config `cloudId` (`https://<host>`). Empty and needed → ask developer for `<organization>.atlassian.net`; never guess.
4. **twg.** `twg := python3 <base>/scripts/twg_cred.py`, `<base>` = this skill's absolute base directory; works from any cwd. Optional leading `--config <configPath>`; default is this skill's `.atlassian.json.user`. Injects config `email`/`apiToken`/`cloudId` into the twg child only and redacts email and token from its output. `atlassian` and `daily-briefing` use this one launcher; never rebuild it inline. Malformed config → exit 1, `error: unreadable or malformed Atlassian config`.
5. **Identity.** `accountId` and `displayName` both set → skip. Either empty → `<twg> whoami -o json --output-file whoami.json` once, then print only `data.accountId` and `data.name` with Python: success → `accountId`, `displayName`; failure → leave empty, never raise. Exception: the ATL installer's connectivity gate always calls live, ignoring cache.
6. **Report** `configPath`, `site`, `twg`, `defaultProjectKey`, `defaultSpaceId`, `tokenAvailable`, `accountId`, `displayName`, `maxResults`, `limit` before the caller's operation.

**Config handoff:** `atl.py` and the other ATL scripts read the config themselves; pass `--config "<configPath>"`, never rebuild the path.

| Key | Meaning | API | Default |
|---|---|---|---|
| `cloudId` | Site URL `https://<host>` (scheme required); reported as `site`; else step 3 | Yes | — |
| `email` | Account email; REST and twg user | Yes | — |
| `apiToken` | API token; REST and twg credential | Yes | — |
| `jiraProjectKeys` | Project keys; first = default | Yes | — |
| `confluenceSpaceIds` | Space ids; first = default | Yes | — |
| `accountId` | Cached by the ATL installer from `twg whoami`; never hand-entered | Yes | — |
| `displayName` | Same origin as `accountId`; never hand-entered | No | — |
| `diagramRenderer` | Publish page mermaid rendering: `png` \| `drawio` \| `mermaid` | No | `png` |
| `drawioExtensionKey` | Required when `diagramRenderer: drawio`; `<appId>/<envId>/static/drawio` | Yes | — |
| `swimlaneDrawio` | Publish page only; routes `swimlane-beta` diagrams to native Mermaid-to-draw.io converter | No | — |
| `maxResults` | JQL page size | Yes | `10` |
| `limit` | CQL page size | Yes | `10` |

## Standing usage rules

Apply in every skill that runs Preflight:

- **twg first.** Search and every non-body Jira/Confluence operation → *follow `atlassian` skill's TWG tactic for Jira workitems, JQL, Confluence pages, CQL, spaces, and people*, running Preflight's `twg` in place of bare `twg`. Never call the Atlassian MCP.
- **REST + ADF for bodies.** For full Jira descriptions and Confluence page bodies (`<details>`, panels, status, TOC, wide tables, inline-comment anchors, diagrams, attachments), *run `atlassian` skill to fetch and publish Jira and Confluence content* using Fetch work, Publish work, Fetch page, or Publish page (`atl.py` over REST). Never read or write those bodies through twg, except each tactic's documented lossy fallback.
- **Markdown, not HTML.** twg fallback reads use `--format md` and warn they are lossy; twg writes use markdown body formats. Never request or send `html`, except the `atlassian` Address page comments tactic's targeted edits.
- JQL/CQL searches use resolved `maxResults`/`limit` as `--limit`, unless the caller bundles its own extraction script and declares a higher cap.
- Large twg result → `-o json --output-file <file>.json`, `cd` there, extract with Python (`read_file` silently truncates lines at ~2000 chars). Unknown shape → `print(json.dumps(d, indent=2)[:2000])`.
- `<twg>` exits `127` → report missing "twg CLI". Auth error → report `email`/`apiToken` in `.atlassian.json.user` as the prerequisite. **MUST NOT** run `twg login`, `setup`, or any interactive command.

## Gotchas

- **MUST NOT search the filesystem** (`find`/`grep`/`ls -R`/`os.walk`) for this skill's directory or `.atlassian.json.user`. Base dir = parent of the `SKILL.md` path given in context; config is its sibling.
- **Long absolute paths in `python3 -c` or heredocs get corrupted by terminal line-wrapping.** `cd` to the directory and use relative filenames; multi-statement code → temp `.py` file run by name.
- `twg -o json` without `--output-file` prints a pointer line (`stdout=<path>`), not JSON. Always pass `--output-file <path>` and parse that file.
- `<twg>` redacts stdout/stderr only; a file written by `--output-file` is unredacted (whoami holds `email`). Extract needed fields; never print the whole file.
