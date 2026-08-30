---
name: init-atl
description: 'First-run setup for this repository''s Atlassian configuration (`.atlassian`), plus optional generation of repository-level Jira/Confluence wrapper skills. Touches nothing outside the repository — no shell profile, no system environment, no extra binary. Replaces `setup-atl` and `setup-atlm`. Use when `.atlassian` is missing or incomplete, or when asked to "setup atl", "init atl", "setup atlassian", or generate a per-repo Jira/Confluence skill.'
---

# Init Atl

One setup skill for the `atl` plugin. Creates or updates `.atlassian` (per [preflight-atl](../preflight-atl/SKILL.md#configuration)'s Configuration table), then offers to generate repository-level skills that pin this repository's Jira required fields and Confluence defaults. Never installs a binary, never edits a shell profile, never sets a system or user environment variable.

## Workflow

**Step 1 — Locate `.atlassian`**

Search bounded to `$HARNESS_REPO_PATH` (never above it), per [Concept 0008](../../../../docs/concepts/0008-per-repo-config-resolution.md):
```bash
find "$HARNESS_REPO_PATH" -name .atlassian
```
Zero results → `configPath := $HARNESS_REPO_PATH/.atlassian`, not yet created. One result → `configPath := <that path>`. More than one → ask the developer which to use.

**Step 2 — Read existing keys, if any**

`configPath` exists → read every line unchanged. A line's key is the text before its first `=`; blank lines and `#` comments carry no key. `presentKeys := <the set of keys found>`. `configPath` does not exist yet → `presentKeys := {}`.

**Step 3 — Collect values for missing keys only**

For each of the five keys below **not** already in `presentKeys`, ask the developer for a value; the developer may decline any prompt — write that key with an empty value rather than omitting it. A key already in `presentKeys` is never re-asked, so an edited value survives a second run.

| Key | Prompt |
|---|---|
| `ATLASSIAN_EMAIL` | "Enter your Atlassian account email:" |
| `ATLASSIAN_SITE` | "Enter your Atlassian site (e.g. `<organization>.atlassian.net`):" |
| `ATLASSIAN_JIRA_PROJECT_KEYS` | "Enter your Jira project key(s), comma-separated, first = default:" |
| `ATLASSIAN_CONFLUENCE_SPACE_IDS` | "Enter your Confluence space id(s), comma-separated, first = default:" |
| `ATLASSIAN_API_TOKEN` | "Enter an API token (optional — only needed for `/publish-page`'s mermaid-diagram upload), from https://id.atlassian.com/manage-profile/security/api-tokens:" |

An existing `.env/.atlmcp.env` or `ACLI_*` environment is not read or migrated — move any value into `.atlassian` manually.

**Step 4 — Write**

- `configPath` not yet created → create it at `$HARNESS_REPO_PATH/.atlassian` with all five keys above, one `KEY=VALUE` line each (empty value for any the developer declined).
- `configPath` already exists → append only the keys missing from `presentKeys` (each `KEY=` with the value collected in Step 3, or empty), one per line, at the end of the file; every existing line is left untouched, in place, unchanged.
- Never print, log, or echo `ATLASSIAN_API_TOKEN`'s value anywhere.

**Step 5 — Confirm the config file is gitignored**

```bash
git -C "$HARNESS_REPO_PATH" check-ignore -q "$configPath" || echo "NOT IGNORED"
```
Prints nothing → already covered, continue. Prints `NOT IGNORED` → append a `.atlassian` line (with a short comment noting it holds a credential) to `$HARNESS_REPO_PATH/.gitignore`, creating that file if it does not exist. Never leave the config file un-ignored.

**Step 6 — Resolve the MCP connection**

Run `/preflight-atl`' skill **Action: Resolve**. `mcpConnected` false → Steps 7 and 8 need a live connection; tell the developer "an Atlassian MCP connection" is the missing prerequisite for wrapper-skill generation, skip both steps, and go straight to Step 9's report.

**Step 7 — Offer a wrapper skill per Jira work item type**

1. Resolve `projectKey`: Preflight's `defaultProjectKey` non-empty → use it. Else call `getVisibleJiraProjects`; exactly one visible project → use it; more than one → ask which; zero → tell the developer "a visible Jira project" is the missing prerequisite, skip this step, and continue to Step 8.
2. Call `getJiraProjectIssueTypesMetadata` with `projectIdOrKey: <projectKey>` — this is the set of Jira work item types this repository uses.
3. For each returned issue type, ask: "Generate a repository-level skill for creating a `<issueType.name>` in `<projectKey>`? (yes/no)".
4. For each accepted type:
   - Call `getJiraIssueTypeMetaWithFields` with `projectIdOrKey`, `issueTypeId`, `requiredFieldsOnly: true` — this repository's required fields for that type.
   - `skillName := create-jira-<issueType.name, lowercased, spaces replaced with hyphens>` (e.g. `Bug` → `create-jira-bug`).
   - `$HARNESS_REPO_PATH/.github/skills/<skillName>/` already exists → ask whether to overwrite before regenerating; never overwrite silently.
   - Create `$HARNESS_REPO_PATH/.github/skills/<skillName>/SKILL.md` — never under `plugins/atl/` or any other plugin folder — with:
     - Frontmatter `name: <skillName>`, `description: Create a <issueType.name> in <projectKey> with this repository's required fields pre-filled. Use when asked to create/open/file a <issueType.name>.`
     - A table of the required fields discovered above: field key, field name.
     - A workflow step that gathers a value for each required field from the developer (or by mirroring an existing issue's values), then runs `/publish-work`' skill with `summary`, `issueType: <issueType.name>`, `description`, `projectKey: <projectKey>`, `additional_fields`: the gathered required-field values. The generated skill never calls `createJiraIssue` itself — the work item is always created by `/publish-work`.

**Step 8 — Offer a Confluence-defaults wrapper skill**

1. Ask: "Generate a repository-level skill pinning this repository's Confluence defaults? (yes/no)". No → skip to Step 9.
2. Resolve `spaceId`: Preflight's `defaultSpaceId` non-empty → use it. Else call `getConfluenceSpaces` with `limit: 10`; exactly one → use it; more than one → ask which; zero → tell the developer "a visible Confluence space" is the missing prerequisite and skip this step.
3. `$HARNESS_REPO_PATH/.github/skills/publish-confluence-defaults/` already exists → ask whether to overwrite before regenerating; never overwrite silently.
4. Create `$HARNESS_REPO_PATH/.github/skills/publish-confluence-defaults/SKILL.md` — never under `plugins/atl/` — with:
   - Frontmatter `name: publish-confluence-defaults`, `description: Publish or update a Confluence page in this repository's default space. Use when asked to publish/create/update a Confluence page without naming a space.`
   - A line stating the pinned `spaceId`.
   - A workflow step that runs `/publish-page`' skill with `mdPath`, `pageId` (when named), and `spaceId: <pinned spaceId>`. The generated skill never calls `createConfluencePage`/`updateConfluencePage` itself — the page is always published by `/publish-page`.

**Step 9 — Report**

State: whether `.atlassian` was created or updated, and which keys were added (never a value besides confirming the token was or wasn't supplied); which wrapper skills were generated and their `.github/skills/` paths; which capabilities were skipped, naming the missing prerequisite for each; and confirm `plugins/atl/` was not touched.

## Rules

- Every generated skill is written under `$HARNESS_REPO_PATH/.github/skills/`, never under `plugins/atl/` or any other plugin folder — one team's required fields never reach another repository.
- A missing prerequisite (no MCP connection, no visible project, no visible space) is named explicitly — never a silent skip that looks like success.
- Required fields are always discovered live via `getJiraIssueTypeMetaWithFields`, never hardcoded.
- No binary is installed, no shell profile or system/user environment variable is touched — `.atlassian` is the only configuration surface.

## Degraded mode

No MCP connection → Steps 1-5 (`.atlassian`) still complete in full; Steps 7 and 8 (wrapper generation) are skipped, each naming "an Atlassian MCP connection" as the missing prerequisite.

## Verification

Config file creation and value preservation share the file shape parsed by `/preflight-atl`: `python3 -m pytest plugins/atl/skills/preflight-atl/`. Generated wrapper-skill content and this skill's developer prompts are deliberately untested — asserting on generated prose locks in wording; verify manually against a repository with no `.atlassian`, and again against one that already carries values, confirming `plugins/atl/` is byte-identical before and after and that the shell profile and system environment are unchanged.
