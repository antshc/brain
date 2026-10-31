---
name: init-atl
description: 'First-run setup for this repository''s Atlassian configuration (`.atlassian.json.user`), plus optional generation of repository-level Jira wrapper skills named `pub-<issue-type>`.'
disable-model-invocation: true
---

# Init Atl

Sets up `atl` in the current repo (= CWD): copies `preflight-atlassian` skill from assets, creates/updates its config, offers `pub-<issue-type>` Jira wrapper skills. **MUST NOT** install binaries, edit shell profiles, set system/user env vars, or run `twg login`/`setup`; `.atlassian.json.user` is the only config surface. twg and the REST scripts share its `email`/`apiToken`.

## Workflow

**1 — Install deps.** From this skill's base directory: `pip install -r requirements.txt`. Covers every `atl` skill (`atlassian-python-api`).

**2 — Copy preflight skill.** `skillDir :=` parent of this `SKILL.md`'s absolute path from context. Copy every file under `<skillDir>/assets/preflight-atlassian/` (`SKILL.md`, `scripts/twg.py`) → CWD `.github/skills/preflight-atlassian/`, keeping relative paths, always overwriting; never touch `.atlassian.json.user`.

```bash
python3 -c "
import shutil
shutil.copytree('<skillDir>/assets/preflight-atlassian', '.github/skills/preflight-atlassian', dirs_exist_ok=True)
"
```

**3 — Read config.** `configPath := .github/skills/preflight-atlassian/.atlassian.json.user` (CWD). Exists → `presentKeys :=` its top-level keys; else `{}`. From the copied `SKILL.md`'s `| Key | Meaning | API | Default |` Configuration table: `tableKeys :=` Key column in row order; `tableDefault(key) :=` Default cell, empty when `—`. Table is the schema source of truth.

**4 — Ask missing keys only.** Per key below not in `presentKeys`, ask. Declined → write `""` (`[]` for arrays). Never re-ask present keys.

| Key | Prompt |
|---|---|
| `email` | "Enter your Atlassian account email:" |
| `cloudId` | "Enter your Atlassian site URL (e.g. `https://<organization>.atlassian.net`):" |
| `jiraProjectKeys` | "Enter your Jira project key(s), comma-separated, first = default:" → trimmed JSON array |
| `confluenceSpaceIds` | "Enter your Confluence space id(s), comma-separated, first = default:" → trimmed JSON array |
| `apiToken` | "Enter an Atlassian API token (required — twg and every REST fetch/publish use it), from https://id.atlassian.com/manage-profile/security/api-tokens:" |
| `diagramRenderer` | "How should `/publish-page` render mermaid diagrams — `png` (default, a static image), `drawio` (editable Draw.io diagram), or `mermaid` (live Mermaid macro)?" |
| `drawioExtensionKey` | "Only for `drawio` — enter the Draw.io macro's extension key, `<appId>/<envId>/static/drawio`. Find it by fetching a page that already holds a Draw.io diagram as ADF and copying the diagram node's `attrs.extensionKey`:" |

`drawio`/`mermaid` need their Confluence app installed; `drawio` also needs `drawioExtensionKey` (ids differ per site). `mermaid` not yet usable — `publish-page` skill refuses it. `png` → leave both empty.

**5 — Write.** Per `tableKeys`: Step 4 value (asked or present) → else `tableDefault` (e.g. `maxResults`/`limit` → `10`, `diagramRenderer` → `png`) → else omit (e.g. `swimlaneDrawio`). New file → create one JSON object; existing → add missing keys only, never change existing values. `accountId`/`displayName` seeded empty, never asked; Step 7 fills them. **MUST NOT** print/log `apiToken`.

**6 — Gitignore config file only.**
```bash
git check-ignore -q "$configPath" || echo "NOT IGNORED"
```
`NOT IGNORED` → append `.atlassian.json.user` line, commented as holding a credential, to CWD `.gitignore` (create if needed). Never ignore the folder — its `SKILL.md` and `scripts/` are checked in.

**7 — Check twg, cache identity.** *Run `preflight-atlassian` skill to resolve site, credentialed twg command, and token availability from `.atlassian.json.user` config* **Action: Resolve**, forcing the live identity check (ignore its cache-skip rule; this populates the cache). `<twg>` exit `127` → report missing "twg CLI" (user installs it), skip to Step 9. Auth failure → report missing "valid `email`/`apiToken`", skip to Step 9. Success and `accountId`/`displayName` not in `presentKeys` → merge live values, missing keys only.

**8 — Offer `pub-<issue-type>` wrappers.** All lookups through Preflight's `twg`, `-o json --output-file`.
1. `projectKey :=` Preflight `defaultProjectKey`; empty → `<twg> jira space query --limit 25`: one → use; many → ask; zero → report missing "a visible Jira project", skip to Step 9.
2. `<twg> jira space issue-types --id-or-key <projectKey>` → `data.issueTypes`.
3. Per type ask: "Generate a repository-level skill for creating a `<issueType.name>` in `<projectKey>`? (yes/no)".
4. Per accepted type:
   - `<twg> jira workitem field create-metadata --space <projectKey> --type <issueType.name>` → keep required fields only.
   - `skillName := pub-<issueType.name lowercased, spaces → hyphens>` (`Bug` → `pub-bug`).
   - Folder exists → ask before overwriting.
   - Write CWD `.github/skills/<skillName>/SKILL.md` containing:
     - Frontmatter `name: <skillName>`, `description: Create a <issueType.name> in <projectKey> with this repository's required fields pre-filled. Use when asked to create/open/file a <issueType.name>.`
     - Required-fields table: field key, field name.
     - Step: gather each required field (developer or mirrored issue), then *run `publish-work` skill to create the Jira work item from a summary and Markdown description* with `summary`, `issueType: <issueType.name>`, `description`, `projectKey: <projectKey>`, `additionalFields`; never create the issue directly through twg or REST.
     - Description-fidelity step: mirror source headings verbatim, add no heading, keep `<details>` blocks; `publish-work` skill converts via `map-markdown-adf` skill and verifies the live issue.

**9 — Report.** Preflight copied; config created/updated + keys added (no values; only whether token supplied); generated wrapper paths; skipped capabilities + missing prerequisite each; `plugins/atl/` untouched.

## Rules

- Generated skills only under CWD `.github/skills/`, never a plugin folder — required fields are per-repo.
- Preflight `SKILL.md` and `scripts/` always overwritten; `pub-*` never overwritten without asking.
- Name every missing prerequisite; never skip silently.
- No Confluence wrapper skill — *use `publish-page` skill directly to create or update a Confluence page from a local Markdown file*.
- Discover required fields live; never hardcode.

## Gotchas

- **MUST NOT** `find`/`grep`/`ls -R` for this skill's directory or assets; derive from this `SKILL.md`'s absolute path in context.
- Resolve `.github/` from CWD, never an env var (`$HARNESS_REPO_PATH` removed); run from repo root.

## Completion criteria

- CWD `.github/skills/preflight-atlassian/SKILL.md` and `scripts/twg.py` byte-identical to `assets/preflight-atlassian/`.
- Config has every table key; each value is the asked value, else the table default (`maxResults`/`limit` → `10`, `diagramRenderer` → `png`), else omitted (`swimlaneDrawio`); existing values unchanged.
- `plugins/atl/` unchanged; shell profile and env unchanged.
