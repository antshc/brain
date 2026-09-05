---
name: init-atl
description: 'First-run setup for this repository''s Atlassian configuration (`.atlassian`), plus optional generation of repository-level Jira wrapper skills named `pub-<issue-type>`. Touches nothing outside the repository — no shell profile, no system environment, no extra binary. Use when `.atlassian` is missing or incomplete, or when asked to "setup atl", "init atl", "setup atlassian", or generate a per-repo Jira skill.'
---

# Init Atl

Setup skill for the `atl` plugin. Creates or updates `.atlassian` (per `/preflight-atl`'s Configuration table), then offers repository-level skills pinning this repo's Jira required fields. Never installs a binary, edits a shell profile, or sets a system/user environment variable.

## Workflow

**1 — Locate `.atlassian`.** Search bounded to `$HARNESS_REPO_PATH` (never above it):
```bash
find "$HARNESS_REPO_PATH" -name .atlassian
```
Zero results → `configPath := $HARNESS_REPO_PATH/.atlassian`, not yet created. One → `configPath := <that path>`. More → ask which.

**2 — Read existing keys.** `configPath` exists → read every line unchanged; a line's key is the text before its first `=`; blank lines and `#` comments carry no key. `presentKeys := <keys found>`. Otherwise `presentKeys := {}`.

**3 — Collect values for missing keys only.** For each key below **not** in `presentKeys`, ask for a value; the developer may decline — write the key with an empty value rather than omitting it. A key in `presentKeys` is never re-asked, so edited values survive a second run.

| Key | Prompt |
|---|---|
| `ATLASSIAN_EMAIL` | "Enter your Atlassian account email:" |
| `ATLASSIAN_SITE` | "Enter your Atlassian site (e.g. `<organization>.atlassian.net`):" |
| `ATLASSIAN_JIRA_PROJECT_KEYS` | "Enter your Jira project key(s), comma-separated, first = default:" |
| `ATLASSIAN_CONFLUENCE_SPACE_IDS` | "Enter your Confluence space id(s), comma-separated, first = default:" |
| `ATLASSIAN_API_TOKEN` | "Enter an API token (optional — only needed for `/publish-page`'s mermaid-diagram upload), from https://id.atlassian.com/manage-profile/security/api-tokens:" |

**4 — Write.**
- Not yet created → create `$HARNESS_REPO_PATH/.atlassian` with all five keys, one `KEY=VALUE` line each (empty value when declined).
- Already exists → append only the keys missing from `presentKeys`, one `KEY=VALUE` line each, at the end; every existing line stays untouched and in place.
- Never print, log, or echo `ATLASSIAN_API_TOKEN`'s value.

**5 — Confirm the config file is gitignored.**
```bash
git -C "$HARNESS_REPO_PATH" check-ignore -q "$configPath" || echo "NOT IGNORED"
```
Nothing printed → continue. `NOT IGNORED` → append a `.atlassian` line (with a short comment noting it holds a credential) to `$HARNESS_REPO_PATH/.gitignore`, creating that file if needed. Never leave it un-ignored.

**6 — Resolve the MCP connection.** Run `/preflight-atl` skill **Action: Resolve**. `mcpConnected` false → name "an Atlassian MCP connection" as the missing prerequisite, skip Step 7, go to Step 8.

**7 — Offer a wrapper skill per Jira work item type.**
1. Resolve `projectKey`: Preflight's `defaultProjectKey` if non-empty. Else `getVisibleJiraProjects` — exactly one → use it; more → ask; zero → name "a visible Jira project" as the missing prerequisite, skip to Step 8.
2. Call `getJiraProjectIssueTypesMetadata` with `projectIdOrKey: <projectKey>` — this repo's work item types.
3. Per type, ask: "Generate a repository-level skill for creating a `<issueType.name>` in `<projectKey>`? (yes/no)".
4. Per accepted type:
   - `getJiraIssueTypeMetaWithFields` with `projectIdOrKey`, `issueTypeId`, `requiredFieldsOnly: true`.
   - `skillName := pub-<issueType.name, lowercased, spaces → hyphens>` (e.g. `Bug` → `pub-bug`, `Story` → `pub-story`).
   - `$HARNESS_REPO_PATH/.github/skills/<skillName>/` exists → ask before overwriting; never overwrite silently.
   - Create `$HARNESS_REPO_PATH/.github/skills/<skillName>/SKILL.md` — never under `plugins/atl/` or any other plugin folder — with:
     - Frontmatter `name: <skillName>`, `description: Create a <issueType.name> in <projectKey> with this repository's required fields pre-filled. Use when asked to create/open/file a <issueType.name>.`
     - A table of the discovered required fields: field key, field name.
     - A workflow step gathering a value per required field (from the developer, or by mirroring an existing issue), then running `/publish-work` with `summary`, `issueType: <issueType.name>`, `description`, `projectKey: <projectKey>`, `additional_fields`. The generated skill never calls `createJiraIssue` itself.

**8 — Report.** Whether `.atlassian` was created or updated and which keys were added (never a value — only whether a token was supplied); which wrapper skills were generated and their `.github/skills/` paths; which capabilities were skipped and the missing prerequisite for each; and that `plugins/atl/` was not touched.

## Rules

- Generated skills always land under `$HARNESS_REPO_PATH/.github/skills/`, never under any plugin folder — one team's required fields never reach another repository.
- A missing prerequisite (no MCP connection, no visible project) is named explicitly — never a silent skip that looks like success.
- Never offer or generate a Confluence-page-defaults wrapper skill — Confluence publishing goes through `/publish-page` directly.
- Required fields are always discovered live via `getJiraIssueTypeMetaWithFields`, never hardcoded.
- No binary installed, no shell profile or system/user environment variable touched — `.atlassian` is the only configuration surface.

## Degraded mode

No MCP connection → Steps 1-5 complete in full; Step 7 is skipped, naming "an Atlassian MCP connection" as the missing prerequisite.

## Verification

Config creation and value preservation share the file shape parsed by `/preflight-atl`: `python3 -m pytest plugins/atl/skills/preflight-atl/`. Generated wrapper content and developer prompts are deliberately untested — asserting on generated prose locks in wording; verify manually against a repo with no `.atlassian`, and again against one already carrying values, confirming `plugins/atl/` is byte-identical before and after and that the shell profile and system environment are unchanged.
