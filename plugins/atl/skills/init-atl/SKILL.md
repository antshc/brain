---
name: init-atl
description: 'First-run setup for this repository''s Atlassian configuration (`.atlassian.json.user`), plus optional generation of repository-level Jira wrapper skills named `pub-<issue-type>`. Touches nothing outside the repository — no shell profile, no system environment, no extra binary. Use when the config is missing or incomplete, or when asked to "setup atl", "init atl", "setup atlassian", or generate a per-repo Jira skill.'
---

# Init Atl

Setup skill for the `atl` plugin. Installs a repo-local copy of `/preflight-atlassian` skill, creates or updates the config it reads (per its Configuration table), then offers repository-level skills pinning this repo's Jira required fields. Never installs a binary, edits a shell profile, or sets a system/user environment variable.

## Workflow

**1 — Install Python dependencies.** Run once, from this skill's directory: `pip install -r requirements.txt`. Covers every `atl` skill's Python needs (`atlassian-python-api` for `fetch-page`/`publish-page`, `pytest` for tests across the plugin) — no other `atl` skill installs its own.

**2 — Copy the `/preflight-atlassian` skill into the repo.** Repo-local skills (this one included) can't assume where the `atl` plugin itself is installed on disk — a dev checkout and a global install place it differently — but a skill's siblings are always co-located with it regardless. Take the absolute path of `init-atl/SKILL.md` you were already given (in the system/tool context that told you this skill exists) — never search for it — and derive the sibling `/preflight-atlassian` skill's directory the same way: its parent directory's parent, then `preflight-atlassian`. Copy `SKILL.md` and `scripts/` from there into `$HARNESS_REPO_PATH/.github/skills/preflight-atlassian/`, always overwriting so the repo copy never drifts from the source skill; never copy `tests/` or `__pycache__/` — they're dev-only.

```bash
python3 -c "
import shutil
shutil.copytree('<sibling /preflight-atlassian skill dir>', '$HARNESS_REPO_PATH/.github/skills/preflight-atlassian', dirs_exist_ok=True, ignore=shutil.ignore_patterns('tests', '__pycache__'))
"
```

**3 — Locate the config.** Resolve `$HARNESS_REPO_PATH` per `/preflight-atlassian`'s Step 1 (empty → repository root, never `/`). `configPath := $HARNESS_REPO_PATH/.github/skills/preflight-atlassian/.atlassian.json.user` — fixed, per `/preflight-atlassian`'s Configuration table, self-located the same way its own script self-locates; never search for it.

**4 — Read existing keys.** `configPath` exists → parse it as JSON; `presentKeys := <its top-level keys>`. Otherwise `presentKeys := {}`.

**5 — Collect values for missing keys only.** For each key below **not** in `presentKeys`, ask for a value; the developer may decline — write the key with an empty value (`""`, or `[]` for the two array keys) rather than omitting it. A key in `presentKeys` is never re-asked, so edited values survive a second run.

| Key | Prompt |
|---|---|
| `email` | "Enter your Atlassian account email:" |
| `site` | "Enter your Atlassian site (e.g. `<organization>.atlassian.net`):" |
| `jiraProjectKeys` | "Enter your Jira project key(s), comma-separated, first = default:" — split on commas, trim, store as a JSON array |
| `confluenceSpaceIds` | "Enter your Confluence space id(s), comma-separated, first = default:" — split on commas, trim, store as a JSON array |
| `apiToken` | "Enter an API token (optional — only needed for `/publish-page`'s mermaid-diagram upload), from https://id.atlassian.com/manage-profile/security/api-tokens:" |
| `diagramRenderer` | "How should `/publish-page` render mermaid diagrams — `png` (default, a static image), `drawio` (editable Draw.io diagram), or `mermaid` (live Mermaid macro)?" |
| `drawioExtensionKey` | "Only for `drawio` — enter the Draw.io macro's extension key, `<appId>/<envId>/static/drawio`. Find it by reading a page that already holds a Draw.io diagram with `contentFormat: "adf"` and copying the diagram node's `attrs.extensionKey`:" |

`drawio` and `mermaid` each need their Confluence app installed. `drawio` additionally needs `drawioExtensionKey`, since the app and environment ids differ per site. `mermaid` is declared but not yet usable — `/publish-page` refuses it until its macro shape is captured. Leave both keys empty for `png`.

**6 — Write.**
- Not yet created → create `configPath` with all seven keys as a single JSON object, one key each (empty string, or empty array for the two array keys, when declined). Parent directories are created as needed — they already exist from Step 2's copy.
- Already exists → merge in only the keys missing from `presentKeys`; every existing key's value stays untouched.
- Never print, log, or echo `apiToken`'s value.
- `accountId`/`displayName` are never part of this step — they're auto-populated from a live call in Step 8, never asked of the developer here.
- `maxResults`/`limit` are never part of this step either — `/preflight-atlassian` defaults both to `10` when absent; a developer who wants a different default hand-edits `configPath` afterwards.

**7 — Confirm the config file — and only the config file — is gitignored.** `SKILL.md` and `scripts/` under `.github/skills/preflight-atlassian/` are checked-in code, copied fresh by Step 2 on every run; only the data file holding credentials needs ignoring.
```bash
git -C "$HARNESS_REPO_PATH" check-ignore -q "$configPath" || echo "NOT IGNORED"
```
Nothing printed → continue. `NOT IGNORED` → append a `.atlassian.json.user` line (with a short comment noting it holds a credential) to `$HARNESS_REPO_PATH/.gitignore`, creating that file if needed — never a whole-folder ignore, which would also hide the checked-in `SKILL.md`/`scripts/`.

**8 — Resolve the MCP connection and cache identity.** Run `/preflight-atlassian` skill (resolves cloudId, default project key, default space id, token availability, `.atlassian.json.user` config) **Action: Resolve**, forcing the live identity/connectivity check — this step is what populates the cache Preflight's Step 3 later reads instead of calling `atlassianUserInfo` again, so its own cache-skip rule does not apply here. `mcpConnected` false → name "an Atlassian MCP connection" as the missing prerequisite, skip Step 9, go to Step 10. `mcpConnected` true and `accountId`/`displayName` missing from `presentKeys` → merge them into `configPath` with Preflight's live `accountId`/`displayName`, mirroring Step 6's merge-only-missing-keys behavior.

**9 — Offer a wrapper skill per Jira work item type.**
1. Resolve `projectKey`: Preflight's `defaultProjectKey` if non-empty. Else `getVisibleJiraProjects` — exactly one → use it; more → ask; zero → name "a visible Jira project" as the missing prerequisite, skip to Step 10.
2. Call `getJiraProjectIssueTypesMetadata` with `projectIdOrKey: <projectKey>` — this repo's work item types.
3. Per type, ask: "Generate a repository-level skill for creating a `<issueType.name>` in `<projectKey>`? (yes/no)".
4. Per accepted type:
   - `getJiraIssueTypeMetaWithFields` with `projectIdOrKey`, `issueTypeId`, `requiredFieldsOnly: true`.
   - `skillName := pub-<issueType.name, lowercased, spaces → hyphens>` (e.g. `Bug` → `pub-bug`, `Story` → `pub-story`).
   - `$HARNESS_REPO_PATH/.github/skills/<skillName>/` exists → ask before overwriting; never overwrite silently.
   - Create `$HARNESS_REPO_PATH/.github/skills/<skillName>/SKILL.md` — never under `plugins/atl/`, `plugins/atl/skills/`, or any other plugin folder — with:
     - Frontmatter `name: <skillName>`, `description: Create a <issueType.name> in <projectKey> with this repository's required fields pre-filled. Use when asked to create/open/file a <issueType.name>.`
     - A table of the discovered required fields: field key, field name.
     - A workflow step gathering a value per required field (from the developer, or by mirroring an existing issue), then running `/publish-work` with `summary`, `issueType: <issueType.name>`, `description`, `projectKey: <projectKey>`, `additional_fields`. The generated skill never calls `createJiraIssue` itself.
     - A description-fidelity step, because the wrapper is what drafts the description: run `/map-markdown-adf` skill **Action: Detect ADF-only constructs** over the source **before** drafting; mirror the source's headings verbatim, adding no wrapper heading of its own and flattening no `<details>` block; and after an ADF publish, confirm the result by fetching the issue back with `getJiraIssue` rather than trusting the publish response.

**10 — Report.** Whether `.github/skills/preflight-atlassian/` was copied fresh; whether its config was created or updated and which keys were added (never a value — only whether a token was supplied); which wrapper skills were generated and their `.github/skills/` paths; which capabilities were skipped and the missing prerequisite for each; and that `plugins/atl/` and `plugins/atl/skills/` were not touched.

## Rules

- Generated skills always land under `$HARNESS_REPO_PATH/.github/skills/`, never under any plugin folder — one team's required fields never reach another repository.
- `.github/skills/preflight-atlassian/` is always overwritten in full on every run (Step 2) — unlike the never-overwrite-without-asking `pub-<issue-type>` skills, it carries no repo-specific customization, only code kept in sync with its source.
- A missing prerequisite (no MCP connection, no visible project) is named explicitly — never a silent skip that looks like success.
- Never offer or generate a Confluence-page-defaults wrapper skill — Confluence publishing goes through `/publish-page` directly.
- Required fields are always discovered live via `getJiraIssueTypeMetaWithFields`, never hardcoded.
- No binary installed, no shell profile or system/user environment variable touched — `.atlassian.json.user` is the only configuration surface.

## Degraded mode

No MCP connection → Steps 1-7 complete in full; Step 9 is skipped, naming "an Atlassian MCP connection" as the missing prerequisite.

## Gotchas

**Never `find`/`grep`/`ls -R` the filesystem to locate this skill's own directory.** The tool/system context that told you this skill exists already gave you `init-atl/SKILL.md`'s absolute path verbatim (it's how you're reading this). Take that literal path's parent directory directly (e.g. strip the trailing `/SKILL.md` yourself) — never rediscover it with a search rooted at `/`, `$HOME`, or any other unbounded root, even bounded by `-maxdepth`. The same rule applies to deriving the sibling `/preflight-atlassian` skill's directory in Step 2 — it's always `<this directory>/../preflight-atlassian`, never rediscovered by search.

## Verification

Config creation, value preservation, and fact derivation all share `/preflight-atlassian`'s test suite: `python3 -m pytest plugins/atl/skills/preflight-atlassian/tests -q`. Generated wrapper content and developer prompts are deliberately untested — asserting on generated prose locks in wording; verify manually against a repo with no config, and again against one already carrying values, confirming `.github/skills/preflight-atlassian/` was copied byte-identical to its source, `plugins/atl/` and `plugins/atl/skills/` are byte-identical before and after, and that the shell profile and system environment are unchanged.
