---
name: init-atl
description: 'First-run setup for this repository''s Atlassian configuration (`atl` + `credentials.atl` in `.harness.json.user`), plus optional generation of repository-level Jira wrapper skills named `pub-<issue-type>`. Touches nothing outside the harness — no shell profile, no system environment, no extra binary. Use when the `atl` section is missing or incomplete, or when asked to "setup atl", "init atl", "setup atlassian", or generate a per-repo Jira skill.'
---

# Init Atl

Setup skill for the `atl` plugin. Creates or updates the `atl` + `credentials.atl` sections of `.harness.json.user` (per `/preflight-atl`'s Configuration table), then offers repository-level skills pinning this repo's Jira required fields. Never installs a binary, edits a shell profile, or sets a system/user environment variable.

## Workflow

**1 — Install Python dependencies.** Run once, from this skill's directory: `pip install -r requirements.txt`. Covers every `atl` skill's Python needs (`atlassian-python-api` for `fetch-page`/`publish-page`, `pytest` for tests across the plugin) — no other `atl` skill installs its own.

**2 — Resolve the settings file.** Run `/resolve-harness` skill; retain its `harnessRepoPath`. Empty → stop and report: run `/init-harness` first, this skill only writes into an existing `.harness.json.user`, never creates the harness. Otherwise `configPath := $harnessRepoPath/.harness.json.user`.

**3 — Read existing keys.** Parse `configPath` as JSON. `atl := data.atl` (or `{}`); `credentialsAtl := data.credentials.atl` (or `{}`). `presentKeys := ` every key already set in either section (a key present with an empty string still counts as present — it was already asked once).

**4 — Collect values for missing keys only.** For each key below **not** in `presentKeys`, ask for a value; the developer may decline — record the key with an empty value rather than omitting it. A key in `presentKeys` is never re-asked, so edited values survive a second run.

| Key | Section | Prompt |
|---|---|---|
| `email` | `credentials.atl` | "Enter your Atlassian account email:" |
| `site` | `atl` | "Enter your Atlassian site (e.g. `<organization>.atlassian.net`):" |
| `jira_project_keys` | `atl` | "Enter your Jira project key(s), comma-separated, first = default:" (store as a JSON array) |
| `confluence_space_ids` | `atl` | "Enter your Confluence space id(s), comma-separated, first = default:" (store as a JSON array) |
| `api_token` | `credentials.atl` | "Enter an API token (optional — only needed for `/publish-page`'s mermaid-diagram upload), from https://id.atlassian.com/manage-profile/security/api-tokens:" |
| `diagram_renderer` | `atl` | "How should `/publish-page` render mermaid diagrams — `png` (default, a static image), `drawio` (editable Draw.io diagram), or `mermaid` (live Mermaid macro)?" |
| `drawio_extension_key` | `atl` | "Only for `drawio` — enter the Draw.io macro's extension key, `<appId>/<envId>/static/drawio`. Find it by reading a page that already holds a Draw.io diagram with `contentFormat: "adf"` and copying the diagram node's `attrs.extensionKey`:" |

`drawio` and `mermaid` each need their Confluence app installed. `drawio` additionally needs `drawio_extension_key`, since the app and environment ids differ per site. `mermaid` is declared but not yet usable — `/publish-page` refuses it until its macro shape is captured. Leave both keys empty for `png`.

**5 — Write.** Merge only the newly-collected keys into `atl` and `credentials.atl` — every other key in either section, and every other top-level section (`harness`, other plugins' sections), stays byte-for-byte as it was. Never print, log, or echo `api_token`'s value.

`account_id`/`display_name` are never part of this step — they're auto-populated from a live call in Step 6, never asked of the developer here.

**6 — Resolve the MCP connection and cache identity.** Run `/preflight-atl` skill **Action: Resolve**, forcing the live identity/connectivity check — this step is what populates the cache Preflight's Step 3 later reads instead of calling `atlassianUserInfo` again, so its own cache-skip rule does not apply here. `mcpConnected` false → name "an Atlassian MCP connection" as the missing prerequisite, skip Step 7, go to Step 8. `mcpConnected` true and `account_id`/`display_name` missing from `presentKeys` → merge them into `atl` with Preflight's live `accountId`/`displayName`, mirroring Step 5's merge-only-missing-keys behavior.

**7 — Offer a wrapper skill per Jira work item type.**
1. Resolve `projectKey`: Preflight's `defaultProjectKey` if non-empty. Else `getVisibleJiraProjects` — exactly one → use it; more → ask; zero → name "a visible Jira project" as the missing prerequisite, skip to Step 8.
2. Call `getJiraProjectIssueTypesMetadata` with `projectIdOrKey: <projectKey>` — this repo's work item types.
3. Per type, ask: "Generate a repository-level skill for creating a `<issueType.name>` in `<projectKey>`? (yes/no)".
4. Per accepted type:
   - `getJiraIssueTypeMetaWithFields` with `projectIdOrKey`, `issueTypeId`, `requiredFieldsOnly: true`.
   - `skillName := pub-<issueType.name, lowercased, spaces → hyphens>` (e.g. `Bug` → `pub-bug`, `Story` → `pub-story`).
   - `$harnessRepoPath/.github/skills/<skillName>/` exists → ask before overwriting; never overwrite silently.
   - Create `$harnessRepoPath/.github/skills/<skillName>/SKILL.md` — never under `plugins/atl/`, `plugins/atl/skills/`, or any other plugin folder — with:
     - Frontmatter `name: <skillName>`, `description: Create a <issueType.name> in <projectKey> with this repository's required fields pre-filled. Use when asked to create/open/file a <issueType.name>.`
     - A table of the discovered required fields: field key, field name.
     - A workflow step gathering a value per required field (from the developer, or by mirroring an existing issue), then running `/publish-work` with `summary`, `issueType: <issueType.name>`, `description`, `projectKey: <projectKey>`, `additional_fields`. The generated skill never calls `createJiraIssue` itself.
     - A description-fidelity step, because the wrapper is what drafts the description: run `/map-markdown-adf` skill **Action: Detect ADF-only constructs** over the source **before** drafting; mirror the source's headings verbatim, adding no wrapper heading of its own and flattening no `<details>` block; and after an ADF publish, confirm the result by fetching the issue back with `getJiraIssue` rather than trusting the publish response.

**8 — Report.** Whether `atl`/`credentials.atl` were created or updated and which keys were added (never a value — only whether a token was supplied); which wrapper skills were generated and their `.github/skills/` paths; which capabilities were skipped and the missing prerequisite for each; and that `plugins/atl/` and `plugins/atl/skills/` were not touched.

## Rules

- Generated skills always land under `$harnessRepoPath/.github/skills/`, never under any plugin folder — one team's required fields never reach another repository.
- A missing prerequisite (no MCP connection, no visible project) is named explicitly — never a silent skip that looks like success.
- Never offer or generate a Confluence-page-defaults wrapper skill — Confluence publishing goes through `/publish-page` directly.
- Required fields are always discovered live via `getJiraIssueTypeMetaWithFields`, never hardcoded.
- No binary installed, no shell profile or system/user environment variable touched — `atl` + `credentials.atl` in `.harness.json.user` is the only configuration surface, and `/init-harness` owns its gitignore status.

## Degraded mode

No MCP connection → Steps 1-5 complete in full; Step 7 is skipped, naming "an Atlassian MCP connection" as the missing prerequisite.

## Gotchas

**Never `find`/`grep`/`ls -R` the filesystem to locate this skill's own directory.** The tool/system context that told you this skill exists already gave you `init-atl/SKILL.md`'s absolute path verbatim (it's how you're reading this). Take that literal path's parent directory directly (e.g. strip the trailing `/SKILL.md` yourself) — never rediscover it with a search rooted at `/`, `$HOME`, or any other unbounded root, even bounded by `-maxdepth`.

## Verification

Config merging and value preservation share the file shape parsed by `/preflight-atl`: `python3 -m pytest plugins/atl/skills/preflight-atl/`. Generated wrapper content and developer prompts are deliberately untested — asserting on generated prose locks in wording; verify manually against a harness whose `.harness.json.user` carries no `atl` section, and again against one already carrying `atl` values, confirming `plugins/atl/` and `plugins/atl/skills/` are byte-identical before and after and that the shell profile and system environment are unchanged.
