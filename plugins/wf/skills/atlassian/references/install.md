# Install

The **Install** tactic. Follow only on explicit request in Copilot CLI; it needs no Preflight (it creates it). Resolve the target with `git rev-parse --show-toplevel` and use it as CWD. Stop outside a Git repository. Resolve `assets/` and `scripts/` from the `atlassian` skill's base directory (`<skillDir>`, the parent of this file's `references/` folder). This installer does not install TWG, edit shell profiles, set persistent environment variables, or run `twg login` or `twg setup`.

## Skill install

The `atlassian` skill ships with `wf@brain`. You can also follow this file directly from a Brain checkout. If `/atlassian` is unavailable, ask the user to run `copilot plugin install wf@brain` or update their existing WF plugin. Users migrating from an earlier release should remove any standalone copy of the skill and uninstall the retired plugin with `copilot plugin uninstall atl@brain` if present. Report plugin status and leave plugin changes to the user.

## Workflow

**1 — Check config and install deps.** `configPath := .github/skills/preflight-atlassian/.atlassian.json.user`. If the config path is tracked or the existing JSON is malformed, stop and report the path without reading values into the conversation. Run `python3 -m pip install -r <skillDir>/scripts/requirements.txt` in the active Python environment. Stop on failure.

**2 — Copy preflight and ignore config.** Copy `<skillDir>/assets/preflight-atlassian/preflight-atlassian.SKILL.template.md` as `.github/skills/preflight-atlassian/SKILL.md` and refresh `scripts/twg_cred.py` from `<skillDir>/assets/preflight-atlassian/scripts/`. Remove the obsolete `scripts/twg.py` there if present. If `git check-ignore -q -- "$configPath"` fails, add `.atlassian.json.user` to the target's `.gitignore` once. Verify the path is ignored and untracked before creating or editing the config. Keep the skill and its scripts trackable.

**3 — Read config keys.** Inspect only top-level keys and credential presence. Use the copied skill's Configuration table as the key and default schema.

**4 — Ask for missing settings.** Use the existing configuration values. Ask only for missing non-secret settings from this table.

| Key | Prompt |
|---|---|
| `cloudId` | "Enter your Atlassian site URL (e.g. `https://<organization>.atlassian.net`):" |
| `jiraProjectKeys` | "Enter your Jira project key(s), comma-separated, first = default:" → trimmed JSON array |
| `confluenceSpaceIds` | "Enter your Confluence space id(s), comma-separated, first = default:" → trimmed JSON array |
| `diagramRenderer` | "How should Confluence publishing render mermaid diagrams — `png` (default, a static image), `drawio` (editable Draw.io diagram), or `mermaid` (live Mermaid macro)?" |
| `drawioExtensionKey` | "Only for `drawio` — enter the Draw.io macro's extension key, `<appId>/<envId>/static/drawio`. Find it by fetching a page that already holds a Draw.io diagram as ADF and copying the diagram node's `attrs.extensionKey`:" |

`drawio`/`mermaid` need their Confluence app installed; `drawio` also needs `drawioExtensionKey` (ids differ per site). `mermaid` not yet usable; the `atlassian` skill's Publish page tactic refuses it. `png` → leave both empty.

**5 — Write missing keys.** Create the ignored JSON object if needed. Preserve existing values and apply the table defaults for unanswered keys. Leave missing `email` and `apiToken` fields absent. Ask the user to add them locally in the ignored config and resume this file. Keep both out of the Copilot conversation. Report credential presence only.

**6 — Check TWG and cache identity.** If email or token is absent, report the missing credential and skip wrapper generation. Follow **Resolve** in the copied preflight `SKILL.md` to get the site, credentialed TWG command, and token availability, forcing the live identity check (ignore its cache-skip rule; this populates the cache). `<twg>` exit `127` → report missing "twg CLI" (user installs it), skip wrapper generation. Auth failure → report missing "valid `email`/`apiToken`", skip wrapper generation. On success, merge live `accountId` and `displayName` into missing or empty cache fields. Preserve populated fields.

**7 — Offer `pub-<issue-type>` wrappers.** All lookups through Preflight's `twg`, `-o json --output-file`.
1. `projectKey :=` Preflight `defaultProjectKey`; empty → `<twg> jira space query --limit 25`: one → use; many → ask; zero → report missing "a visible Jira project", skip wrapper generation.
2. `<twg> jira space issue-types --id-or-key <projectKey>` → `data.issueTypes`.
3. Per type ask: "Generate a repository-level skill for creating a `<issueType.name>` in `<projectKey>`? (yes/no)".
4. Per accepted type:
   - `<twg> jira workitem field create-metadata --space <projectKey> --type <issueType.name>` → keep required fields only.
   - `skillName := pub-<issueType.name lowercased, spaces → hyphens>` (`Bug` → `pub-bug`).
   - Folder exists → ask before overwriting.
   - Write CWD `.github/skills/<skillName>/SKILL.md` containing:
     - Frontmatter `name: <skillName>`, `description: Create a <issueType.name> in <projectKey> with this repository's required fields pre-filled. Use when asked to create/open/file a <issueType.name>.`
     - Required-fields table: field key, field name.
     - Step: gather each required field (developer or mirrored issue), then *run `atlassian` skill's Publish work tactic to create the Jira work item from a summary and Markdown description* with `summary`, `issueType: <issueType.name>`, `description`, `projectKey: <projectKey>`, `additionalFields`; never create the issue directly through twg or REST.
     - Description-fidelity step: mirror source headings verbatim, add no heading, keep `<details>` blocks; the Publish work tactic converts Markdown to ADF and verifies the live issue.

**8 — Migrate existing wrappers.** For each existing `.github/skills/pub-*/SKILL.md` that invokes the retired `publish-work` skill: show the planned change and ask before editing. Replace only that invocation with the Step 7 Publish work invocation; keep the frontmatter, Required-fields table, field values, and every local edit. Wrappers already on the `atlassian` skill → no change.

**9 — Report.** Include skill availability, refreshed preflight files, keys added without values, wrapper paths (generated, migrated, skipped), and any missing prerequisites. Leave target changes uncommitted.

## Rules

- Generate repo-specific skills only under the target's `.github/skills/`. Refresh bundled preflight files without changing `.atlassian.json.user` values. Ask before overwriting or migrating a `pub-*` wrapper.
- Discover required Jira fields live. Confluence pages need no wrapper; use the `atlassian` skill's Publish page tactic.
- Resolve both roots explicitly. Use a scratch file for live TWG identity output, extract only account ID and display name, then remove it.
