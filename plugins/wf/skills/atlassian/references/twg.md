# TWG

General `twg` CLI guidance for the **Query or operate with TWG** tactic. Run every command through Preflight's credentialed `<twg>` launcher in place of bare `twg`. Live help owns command grammar. Product references are routed from the `atlassian` skill's TWG routes section.

## Contents

- TWG Terms
- Fast path
- Command index
- Plan First
- Invocation And Output
- Auth/Setup Guard
- Errors in Sandboxes
- On gathering evidence
- Batch Reads
- Assorted Discovery guidelines
- Rules

## TWG Terms

- **Anchor**: the key, URL, person, project, repository, or window that a request starts from. Anchor read-only answers on it.
- **Hydrate**: get the full record of a search or query result.

## Fast path

| Need | Command |
|---|---|
| Find sources about a topic | `<twg> rovo search "<topic>" --limit 10` |
| Read a Confluence page (search hit, ID, or URL) | **Fetch page** tactic. Fallback only when it is unavailable or fails: `<twg> confluence content get <id-or-url> --detail full --format md`; warn it is lossy (diagrams, media, attachments, comments may be missing) |
| Read a Jira work item body | **Fetch work** tactic. Fallback: `<twg> jira workitem get <KEY>`; warn the body may lose ADF-only constructs |

Use `--site <site>` when supplied or when the anchor URL identifies a site. For a multi-site request, run each query against its intended site. Do not assume the saved default matches every anchor. If the request identifies no site, use the configured default and state the scope.

Read search results before you cite them. For questions these commands cover, do not run `twg help-map` or `twg help describe "<command>"`. Run independent reads in one shell call, separated by `;`.

For other tasks or unclear syntax, follow Plan First.

## Command index

`twg help-map` is the live, complete map (`*` = write); use this index to pick a route, then confirm grammar with `twg help describe`.

| Namespace | Covers |
|---|---|
| `rovo search`, `rovo deep-search` | Cross-product discovery, deep research (`twg help rovo`) |
| `jira workitem` | get, bulk-get, query (JQL), search, similar, create, update, transition, comment, link/unlink, attachment, worklog, field metadata |
| `jira board`, `jira sprint`, `jira filter`, `jira dashboard`, `jira space`, `jira field`, `spaces` | Boards, backlogs, sprints, filters, dashboards, Jira projects, field admin |
| `confluence content` | get, list, create, update, move, archive, trash, purge, comments, labels, versions, approvals, attachments, export |
| `confluence space`, `confluence tree`, `confluence search` | Space lifecycle, instructions, hierarchy, CQL and text search |
| `context`, `subgraph` | Linked artifacts, graph neighborhoods, Jira links, space containment (`twg help context`) |
| `user`, `people`, `teams`, `org-tree`, `collaborators` | People lookup, reporting lines, teams |
| `responsibility` | Declared and inferred owners, experts, escalation (`twg help responsibility`) |
| `work`, `docs`, `work-tree`, `workitem-tree`, `pr-tree`, `notifications` | Personal and org activity, rollups |
| `jsm` | Incidents, PIRs, alerts, requests, SLAs, knowledge (`twg help jsm`) |
| `assets` | Assets objects, AQL, relationship graph |
| `trello`, `loom`, `meetings`, `videos` | Other connected products (`twg help <namespace>`) |
| `help`, `help-map`, `whoami`, `doctor` | Discovery and diagnostics |

## Plan First

1. Run `twg help-map`; `*` marks writes. Do not pipe it through `head`.
2. Describe the selected commands in one call (up to 10): `twg help describe "<a>" "<b>"`. Reuse those contracts.
3. After contract review, plan internally between `### Plan` and `### End plan`. Give one step per call: exact command paths, inputs, flags, dependencies, and unknowns linked to their producer steps. Append the plan after all commands in the first execution shell call, with `#` before each line. Print only on user request or for clarification or approval.
4. Batch independent reads, separated by `;` (`&&` for dependencies). Pipe JSON to `jq` only with `set -o pipefail`; check error fields.

If a command is unclear, run `twg help <terms>`. For more guidance, run `twg help discover-skills "<intent>"`, then follow `next.loadReference`.

## Invocation And Output

Run `<twg> <command>`. The launcher finds `twg` on PATH or in its default install directory; exit `127` (`error: twg CLI not found`) → report missing "twg CLI" and ask the user to install it. Do not treat auth or command errors as PATH failures.

Do not add per-command env prefixes unless requested; hosts may set `TWG_AGENT_DEFAULTS=1`.

- Large result → `-o json --output-file <file>.json`, then extract with Python; `read_file` truncates long lines.
- Answer from inline or already-read compact output if it supports the requested facts.
- Quote extracted facts with their sources, not whole payloads.
- Keep unavailable evidence unknown.
- On a restricted host, use only `twg` and permitted output files, not arbitrary host files, credentials, or other agent runs.
- Use the prompt's timezone and window.

## Auth/Setup Guard

Do not run a command that waits for user input, such as setup, login, install, upgrade, or upkeep. Give clear instructions and ask the user to run it. Auth error → report `email`/`apiToken` in `.atlassian.json.user`.

## Errors in Sandboxes

For sandboxed `twg bb pipeline get`, `wait`, `grep`, or `tail`, log restrictions are not evidence of auth failure; report the restriction and the evidence you have.

## On gathering evidence

1. Give the first call all known references.
2. Check current claims against live fields. Date past evidence; report unknown facts.
3. Stop at the first policy denial, or when the same error repeats.
4. Treat a named project or service as exact. Keep its qualifiers and check that you found it. Use a renamed or successor item only if a source says so. If you find no evidence, say so.

## Batch Reads

When a command accepts many inputs, send about twenty IDs per call with `--agent-fields @compact`. Use query or tree metadata when it is enough. Tell the user what you omitted. After five repeated calls, check for a batch call.

## Assorted Discovery guidelines

- Use `twg trello search "<query>"` for Trello. It has no workspace scope.
- Run `twg rovo list-apps -o json` only when availability is unknown. Reuse auth. Do not auto-login or fabricate "none found".
- `docs query` and `work query` return user activity, not title or content matches. For topic text, use `docs search` or `work search`.
- Pass supported original references to native reads. Avoid separate resolve calls.
- Command shape guardrails:
  - `work query` uses `--scope me|user`, never `--scope global`.
  - Inferred teams need explicit `--include-inferred`.
- Use `assets graph` to traverse object, owner, team, or Jira relationships. Otherwise use `assets search`, `assets query --aql`, or `assets object get`.

## Rules

- Never guess IDs, flags, slugs, ARIs, or write contracts.
- For a write, load the product route's rules, follow live help, and read the current state. Tell the user what the write will change, unless they asked you to run it.
- Read every loaded reference fully; a partial read counts as not loaded.
- Do not inspect local files, caches, or schemas, unless the user asks about local state.
