---
name: init-atl
description: 'First-run setup for this repository''s Atlassian configuration (`.atlassian.json.user`), plus optional generation of repository-level Jira wrapper skills named `pub-<issue-type>`.'
disable-model-invocation: true
---

# Init Atl

Sets up `atl` in the current repo (= CWD): copies `preflight-atlassian` from template, creates/updates its config, offers `pub-<issue-type>` Jira wrapper skills. **MUST NOT** install binaries, edit shell profiles, or set system/user env vars; `.atlassian.json.user` is the only config surface.

## Workflow

**1 — Install deps.** From this skill's base directory: `pip install -r requirements.txt`. Covers every `atl` skill (`atlassian-python-api`, `pytest`).

**2 — Copy preflight template.** `skillDir :=` parent of this `SKILL.md`'s absolute path from context. Copy `<skillDir>/preflight-atlassian.SKILL.template.md` → CWD `.github/skills/preflight-atlassian/SKILL.md`, always overwriting.

```bash
python3 -c "
from pathlib import Path
import shutil
dest = Path('.github/skills/preflight-atlassian/SKILL.md')
dest.parent.mkdir(parents=True, exist_ok=True)
shutil.copy('<skillDir>/preflight-atlassian.SKILL.template.md', dest)
"
```

**3 — Read config.** `configPath := .github/skills/preflight-atlassian/.atlassian.json.user` (CWD). Exists → `presentKeys :=` its top-level keys; else `{}`. From the copied `SKILL.md`'s `| Key | Meaning | API | Default |` Configuration table: `tableKeys :=` Key column in row order; `tableDefault(key) :=` Default cell, empty when `—`. Table is the schema source of truth.

**4 — Ask missing keys only.** Per key below not in `presentKeys`, ask. Declined → write `""` (`[]` for arrays). Never re-ask present keys.

| Key | Prompt |
|---|---|
| `email` | "Enter your Atlassian account email:" |
| `cloudId` | "Enter your Atlassian site (e.g. `<organization>.atlassian.net`):" |
| `jiraProjectKeys` | "Enter your Jira project key(s), comma-separated, first = default:" → trimmed JSON array |
| `confluenceSpaceIds` | "Enter your Confluence space id(s), comma-separated, first = default:" → trimmed JSON array |
| `apiToken` | "Enter an API token (optional — only needed for `/publish-page`'s mermaid-diagram upload), from https://id.atlassian.com/manage-profile/security/api-tokens:" |
| `diagramRenderer` | "How should `/publish-page` render mermaid diagrams — `png` (default, a static image), `drawio` (editable Draw.io diagram), or `mermaid` (live Mermaid macro)?" |
| `drawioExtensionKey` | "Only for `drawio` — enter the Draw.io macro's extension key, `<appId>/<envId>/static/drawio`. Find it by reading a page that already holds a Draw.io diagram with `contentFormat: "adf"` and copying the diagram node's `attrs.extensionKey`:" |

`drawio`/`mermaid` need their Confluence app installed; `drawio` also needs `drawioExtensionKey` (ids differ per site). `mermaid` not yet usable — `publish-page` refuses it. `png` → leave both empty.

**5 — Write.** Per `tableKeys`: Step 4 value (asked or present) → else `tableDefault` (e.g. `maxResults`/`limit` → `10`, `diagramRenderer` → `png`) → else omit (e.g. `swimlaneDrawio`). New file → create one JSON object; existing → add missing keys only, never change existing values. `accountId`/`displayName` seeded empty, never asked; Step 7 fills them. **MUST NOT** print/log `apiToken`.

**6 — Gitignore config file only.**
```bash
git check-ignore -q "$configPath" || echo "NOT IGNORED"
```
`NOT IGNORED` → append `.atlassian.json.user` line, commented as holding a credential, to CWD `.gitignore` (create if needed). Never ignore the folder — its `SKILL.md` is checked in.

**7 — Resolve MCP, cache identity.** Run `preflight-atlassian` **Action: Resolve**, forcing the live identity check (ignore its cache-skip rule; this populates the cache). `mcpConnected` false → report missing "an Atlassian MCP connection", skip to Step 9. True and `accountId`/`displayName` not in `presentKeys` → merge live values, missing keys only.

**8 — Offer `pub-<issue-type>` wrappers.**
1. `projectKey :=` Preflight `defaultProjectKey`; empty → `getVisibleJiraProjects`: one → use; many → ask; zero → report missing "a visible Jira project", skip to Step 9.
2. `getJiraProjectIssueTypesMetadata(projectIdOrKey: projectKey)`.
3. Per type ask: "Generate a repository-level skill for creating a `<issueType.name>` in `<projectKey>`? (yes/no)".
4. Per accepted type:
   - `getJiraIssueTypeMetaWithFields(projectIdOrKey, issueTypeId, requiredFieldsOnly: true)`.
   - `skillName := pub-<issueType.name lowercased, spaces → hyphens>` (`Bug` → `pub-bug`).
   - Folder exists → ask before overwriting.
   - Write CWD `.github/skills/<skillName>/SKILL.md` containing:
     - Frontmatter `name: <skillName>`, `description: Create a <issueType.name> in <projectKey> with this repository's required fields pre-filled. Use when asked to create/open/file a <issueType.name>.`
     - Required-fields table: field key, field name.
     - Step: gather each required field (developer or mirrored issue), then run `publish-work` with `summary`, `issueType: <issueType.name>`, `description`, `projectKey: <projectKey>`, `additional_fields`; never call `createJiraIssue` directly.
     - Description-fidelity step: before drafting, run `map-markdown-adf` **Action: Detect ADF-only constructs** on the source; mirror source headings verbatim, add no heading, keep `<details>` blocks; after ADF publish, verify via `getJiraIssue`, not the publish response.

**9 — Report.** Preflight copied; config created/updated + keys added (no values; only whether token supplied); generated wrapper paths; skipped capabilities + missing prerequisite each; `plugins/atl/` untouched.

## Rules

- Generated skills only under CWD `.github/skills/`, never a plugin folder — required fields are per-repo.
- Preflight `SKILL.md` always overwritten; `pub-*` never overwritten without asking.
- Name every missing prerequisite; never skip silently.
- No Confluence wrapper skill — use `publish-page` directly.
- Discover required fields live; never hardcode.

## Gotchas

- **MUST NOT** `find`/`grep`/`ls -R` for this skill's directory or template; derive from this `SKILL.md`'s absolute path in context.
- Resolve `.github/` from CWD, never an env var (`$HARNESS_REPO_PATH` removed); run from repo root.

## Verification

No test suite. Verify manually on a repo with no config and one with values: preflight `SKILL.md` byte-identical to template; config has every table key with correct asked/default value (`maxResults`/`limit`/`diagramRenderer` defaults, no `swimlaneDrawio`); `plugins/atl/` unchanged; shell profile and env unchanged.
