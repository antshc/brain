---
name: preflight-atlassian
description: >-
  Resolve Atlassian connection facts (site, default project key, default space id, token availability, credentialed twg command) from this repo's `.atlassian.json.user` config. Internal gate invoked by other `atl` skills, not a user entry point. Publish a Confluence page via `publish-page`; create or update a Jira work item via `publish-work`.
compatibility: Requires the `twg` CLI and an Atlassian API token (`email` + `apiToken`); twg and the REST scripts share those credentials.
---

# Preflight

Resolution gate every `atl` skill runs first. Never fails — unresolved facts return empty; caller names the missing prerequisite. Sole owner of locating and parsing `.atlassian.json.user` (gitignored, sibling of this `SKILL.md`); other skills MUST NOT re-implement it.

**MUST NOT echo** config `email`/`apiToken` or identity-response `email` — not in output, logs, errors, or command lines.

## Routing

Preflight resolves facts only; never creates/updates content. Request is the operation itself → hand off to the owning skill, which runs Preflight as its Step 1:

- Publish/create/update a Confluence page from a Markdown file → *run `publish-page` skill to create or update a Confluence page from a local Markdown file, converting to ADF and uploading mermaid diagrams*.
- Create/update a Jira work item/issue/story/task/bug/epic → *run `publish-work` skill to create or update a Jira work item from a summary and Markdown description*.
- Fetch a Confluence page as Markdown → *run `fetch-page` skill to fetch a Confluence page as Markdown from its ID, tiny ID, or URL*.
- Fetch a Jira work item as Markdown → *run `fetch-work` skill to fetch a Jira work item as Markdown from its key or URL*.

## Resolve

1. **Locate config.** From this skill's base directory run `python3 -c "from pathlib import Path; print(Path('.atlassian.json.user').resolve())"` → `configPath` (absolute; printed even when the file is absent).
2. **Read config.** From this skill's base directory run `python3 -c "import json;from pathlib import Path;p=Path('.atlassian.json.user');d=json.loads(p.read_text()) if p.exists() else {};print(json.dumps({k:(bool(v) if k in ('email','apiToken') else v) for k,v in d.items()}))"` (credentials print as presence booleans).
   - Not found → keys take table Default; keys without Default resolve empty (`site` → step 3, identity → step 5, project key/space id → ask per caller).
   - Found → file value wins; absent keys take Default. `tokenAvailable := email and apiToken both true`.
3. **site.** `site :=` config `cloudId` (`https://<host>`). Empty and needed → ask developer for `<organization>.atlassian.net`; never guess.
4. **twg.** `twg := python3 <base>/scripts/twg.py`, `<base>` = this skill's absolute base directory. Runs the `twg` CLI with config `email`/`apiToken`/`cloudId` injected and redacted from output.
5. **Identity.** `accountId` and `displayName` both set → skip. Either empty → `<twg> whoami -o json --output-file whoami.json` once, then print only `data.accountId` and `data.name` with Python: success → `accountId`, `displayName`; failure → leave empty, never raise. Exception: `init-atl`'s connectivity gate always calls live, ignoring cache.
6. **Report** `configPath`, `site`, `twg`, `defaultProjectKey`, `defaultSpaceId`, `tokenAvailable`, `accountId`, `displayName`, `maxResults`, `limit` before the caller's operation.

**Config handoff:** `atl` scripts read the config themselves — pass `--config "<configPath>"`; never rebuild the path.

| Key | Meaning | API | Default |
|---|---|---|---|
| `cloudId` | Site URL `https://<host>` (scheme required); reported as `site`; else step 3 | Yes | — |
| `email` | Account email; REST and twg user | Yes | — |
| `apiToken` | API token; REST and twg credential | Yes | — |
| `jiraProjectKeys` | Project keys; first = default | Yes | — |
| `confluenceSpaceIds` | Space ids; first = default | Yes | — |
| `accountId` | Cached by `init-atl` from `twg whoami`; never hand-entered | Yes | — |
| `displayName` | Same origin as `accountId`; never hand-entered | No | — |
| `diagramRenderer` | `publish-page` mermaid rendering: `png` \| `drawio` \| `mermaid` | No | `png` |
| `drawioExtensionKey` | Required when `diagramRenderer: drawio`; `<appId>/<envId>/static/drawio` | Yes | — |
| `swimlaneDrawio` | `publish-page` only; routes `swimlane-beta` diagrams to native Mermaid-to-draw.io converter | No | — |
| `maxResults` | JQL page size | Yes | `10` |
| `limit` | CQL page size | Yes | `10` |

## Standing usage rules

Apply in every `atl` skill:

- **twg first.** Search, retrieval, and every other Jira/Confluence operation → *follow `twg` skill for Jira workitems, JQL, Confluence pages, CQL, spaces, and people*, running Preflight's `twg` in place of bare `twg`. Never call the Atlassian MCP.
- **Markdown, not HTML.** Confluence reads `--format md`; Jira/Confluence writes `--description-format markdown` / markdown body format. Never request or send `html`.
- **REST + ADF exceptions.** Page/work-item bodies that must round-trip `map-markdown-adf` constructs (`<details>`, panels, status, TOC, wide tables, inline-comment anchors, diagrams, attachments) → `fetch-page`, `publish-page`, `fetch-work`, `publish-work` skills only; their scripts move ADF over REST. Never read or write those bodies through twg.
- JQL/CQL searches use resolved `maxResults`/`limit` as `--limit`, unless the caller bundles its own extraction script and declares a higher cap.
- Large twg result → `-o json --output-file <file>.json`, `cd` there, extract with Python (`read_file` silently truncates lines at ~2000 chars). Unknown shape → `print(json.dumps(d, indent=2)[:2000])`.
- `<twg>` exits `127` → report missing "twg CLI". Auth error → report `email`/`apiToken` in `.atlassian.json.user` as the prerequisite. **MUST NOT** run `twg login`, `setup`, or any interactive command.

## Gotchas

- **MUST NOT search the filesystem** (`find`/`grep`/`ls -R`/`os.walk`) for this skill's directory or `.atlassian.json.user`. Base dir = parent of the `SKILL.md` path given in context; config is its sibling.
- **Long absolute paths in `python3 -c` or heredocs get corrupted by terminal line-wrapping.** `cd` to the directory and use relative filenames; multi-statement code → temp `.py` file run by name.
- twg run by an agent prints a YAML envelope pointing at spilled files, not the payload; `-o json --output-file <path>` writes the full JSON to a known path.
- `<twg>` redacts stdout/stderr only; a file written by `--output-file` is unredacted (whoami holds `email`). Extract needed fields; never print the whole file.
