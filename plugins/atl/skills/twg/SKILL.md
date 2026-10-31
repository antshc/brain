---
name: twg
description: >-
  Use TWG whenever Atlassian or company context would help; prefer TWG for any search across Jira, Confluence, and connected sources (JQL, CQL, fuzzy and semantic search, topic discovery); Jira workitems, issues, JQL, transitions, fields, boards, sprints, and duplicate detection; Confluence pages, PRDs, spaces, CQL, authoring, editing, comments, and exports; owners, SMEs, approvers, or escalation; personal, org, or leadership work rollups and out-of-office catch-ups; dependency maps; incidents, on-call, or reliability; and deep internal research across connected sources, docs, work, and people.
---

# twg

Entry point and orchestrator for all `twg` CLI work. Route by intent, then load only the references the route names. Live help owns command grammar.

## TWG Terms

- **Anchor**: the key, URL, person, project, repository, or window that a request starts from. Anchor read-only answers on it.
- **Hydrate**: get the full record of a search or query result.

## Fast path for common simple commands

| Need | Command |
|---|---|
| Find sources about a topic | `twg rovo search "<topic>" --limit 10` |
| Read a Confluence page | *Run `fetch-page` skill to fetch a Confluence page as Markdown (ID or URL, attachments, comments).* Fallback: `twg confluence content get <id-or-url> --detail full --format md` |
| Read a Jira workitem | *Run `fetch-work` skill to fetch a Jira work item as Markdown (key or URL, issue).* Fallback: `twg jira workitem get <KEY>` |

Use `--site <site>` when supplied or when the anchor URL identifies a site. For a multi-site request, run each query against its intended site. Do not assume the saved default matches every anchor. If the request identifies no site, use the configured default and state the scope.

Read at most 3 Confluence IDs per call with the fast path; batch reads follow *Confluence*.

Read search results before you cite them. For questions these commands cover, do not run `twg help-map` or `twg help describe "<command>"`. Run independent reads in one shell call, separated by `;`.

For other tasks or unclear syntax, follow **Plan First**.

## Command index

Quick navigation by namespace. `twg help-map` is the live, complete map (`*` = write); use this index to pick a route, then confirm grammar with `twg help describe`.

| Namespace | Covers | Route |
|---|---|---|
| `rovo search`, `rovo deep-search` | Cross-product discovery, deep research | `twg help rovo` |
| `jira workitem` | get, bulk-get, query (JQL), search, similar, create, update, transition, comment, link/unlink, attachment, worklog, field metadata | *Jira* |
| `jira board`, `jira sprint`, `jira filter`, `jira dashboard`, `jira space`, `jira field`, `spaces` | Boards, backlogs, sprints, filters, dashboards, Jira projects, field admin | *Jira* |
| `confluence content` | get, list, create, update, move, archive, trash, purge, comments, labels, versions, approvals, attachments, export | *Confluence* |
| `confluence space`, `confluence tree`, `confluence search` | Space lifecycle, instructions, hierarchy, CQL and text search | *Confluence* |
| `context`, `subgraph` | Linked artifacts, graph neighborhoods, Jira links, space containment | `twg help context` |
| `user`, `people`, `teams`, `org-tree`, `collaborators` | People lookup, reporting lines, teams | [references/USER-IDENTIFIERS.md](references/USER-IDENTIFIERS.md) |
| `responsibility` | Declared and inferred owners, experts, escalation | `twg help responsibility` |
| `work`, `docs`, `work-tree`, `workitem-tree`, `pr-tree`, `notifications` | Personal and org activity, rollups | [references/ROUTING.md](references/ROUTING.md) |
| `jsm` | Incidents, PIRs, alerts, requests, SLAs, knowledge | `twg help jsm` |
| `assets` | Assets objects, AQL, relationship graph | [references/ASSETS_GRAPH.md](references/ASSETS_GRAPH.md) |
| `trello`, `loom`, `meetings`, `videos` | Other connected products | `twg help <namespace>` |
| `help`, `help-map`, `whoami`, `doctor` | Discovery and diagnostics | [references/HELP.md](references/HELP.md) |

## Plan First

1. Run `twg help-map`; `*` marks writes. Do not pipe it through `head`.
2. Describe the selected commands in one call (up to 10): `twg help describe "<a>" "<b>"`. Reuse those contracts.
3. After contract review, plan internally between `### Plan` and `### End plan`. Give one step per call: exact command paths, inputs, flags, dependencies, and unknowns linked to their producer steps. Append the plan after all commands in the first execution shell call, with `#` before each line. Print only on user request or for clarification or approval.
4. Batch independent reads, separated by `;` (`&&` for dependencies). Pipe JSON to `jq` only with `set -o pipefail`; check error fields.

If a command is unclear, run `twg help <terms>`. For more guidance, run `twg help discover-skills "<intent>"`, then follow `next.loadReference`.

## Routing

Load the narrowest route. Jira and Confluence are bundled here. Read each referenced file fully, resolved from this skill's base directory.

- Search: prefer `twg` for every search (JQL, CQL, `rovo search`, `docs search`, `work search`); never use the skills below to search.
- Preferred skills for fetching or publishing a known page or work item; use `twg` only as the fallback when one does not cover the request or fails:
  - *Run `fetch-page` skill to fetch, read, or summarize a Confluence page as Markdown (ID, tiny ID, URL, attachments).*
  - *Run `publish-page` skill to create or update a Confluence page from a local Markdown file (diagrams, ADF, inline comments).*
  - *Run `fetch-work` skill to fetch, read, or summarize a Jira work item as Markdown (key, URL, issue).*
  - *Run `publish-work` skill to create or update a Jira work item from a Markdown description (summary, story, task, bug, epic).*
- Jira: follow *Jira*.
- Confluence: follow *Confluence*.
- People: [references/USER-IDENTIFIERS.md](references/USER-IDENTIFIERS.md).

## Jira

Use when a Jira key, issue URL, project key, board, sprint, filter, or dashboard is the primary anchor; the user asks to create, update, transition, comment on, link, watch, or delete Jira work; duplicates must be found; required or custom fields must be populated; or a workflow needs authoritative Jira fields or status. Skip when Jira is only one supporting artifact in a cross-product answer.

Prefer *`fetch-work` skill (fetch work item as Markdown)* to read and *`publish-work` skill (create or update work item)* to write; use the routes below as the fallback.

**MUST** read [references/jira/rules.md](references/jira/rules.md) before any Jira write or authoritative Jira answer. Then load the route's reference.

| Intent | Route | Load |
|---|---|---|
| Known workitem | Native workitem `get` | [references/jira/workitems.md](references/jira/workitems.md) |
| Several known workitems | One `get`/`bulk-get` with all keys | [references/jira/workitems.md](references/jira/workitems.md) |
| Jira-only fuzzy text discovery | Workitem `search` (JQL-backed) | [references/jira/querying.md](references/jira/querying.md) |
| Exact Jira filtering | Workitem `query` with JQL | [references/jira/querying.md](references/jira/querying.md) |
| Board, backlog, or sprint ordering | Board/backlog/sprint command | [references/jira/querying.md](references/jira/querying.md) |
| Semantic Jira discovery | `rovo search --app jira` | none |
| Duplicate workitem detection | Bounded candidates, semantic gates | [references/jira/duplicates.md](references/jira/duplicates.md), [references/jira/querying.md](references/jira/querying.md) |
| Related artifacts or people | Native read plus `context` | [references/jira/workitems.md](references/jira/workitems.md) |
| Link implementation artifacts | `jira workitem link` | [references/jira/workitems.md](references/jira/workitems.md) |
| Create or update | Field metadata, then mutation | [references/jira/fields-and-transitions.md](references/jira/fields-and-transitions.md), [references/jira/workitems.md](references/jira/workitems.md) |
| Change workflow state | Discover transitions, then transition | [references/jira/fields-and-transitions.md](references/jira/fields-and-transitions.md) |
| Descriptions, comments, mentions | Advertised body format | [references/jira/rich-content.md](references/jira/rich-content.md) |
| Jira configuration | Jira administration namespace | [references/jira/administration.md](references/jira/administration.md) |

## Confluence

Use for Confluence content, spaces, hierarchy, authoring, editing, comments, versions, permissions, exports, and CQL.

Prefer *`fetch-page` skill (fetch page as Markdown)* to read and *`publish-page` skill (create or update page from Markdown)* to write; use the routes below as the fallback.

**MUST** read [references/confluence/rules.md](references/confluence/rules.md) before any Confluence write or pre-edit read. Then load the route's reference.

| Intent | Route | Load |
|---|---|---|
| Known content ID/URL | `confluence content get` | [references/confluence/content.md](references/confluence/content.md) (Embed And Smart Link Reads) |
| Several known pages | One `confluence content get <id-or-url...>` for the selected set | none |
| Exact Confluence filtering | Confluence search with CQL | [references/confluence/querying.md](references/confluence/querying.md) |
| Date-filtered page/blogpost list | `confluence search query --cql` with `lastmodified`; `content list` has no date filter | [references/confluence/querying.md](references/confluence/querying.md) |
| Paginated content list | `confluence content list` with `nextCursor` | [references/confluence/pagination.md](references/confluence/pagination.md) |
| Fuzzy page/topic discovery | Cross-product search, then native get | [references/confluence/querying.md](references/confluence/querying.md) |
| Create or update content | Unified `confluence content` surface | [references/confluence/content.md](references/confluence/content.md), [references/confluence/body-formats.md](references/confluence/body-formats.md) |
| Edit an existing body | Read, save, edit file, update with snapshot token | [references/confluence/editing.md](references/confluence/editing.md), [references/confluence/body-formats.md](references/confluence/body-formats.md) |
| Current user's personal space | `confluence space me`; reuse returned identity, never infer it from `accountId` or search | none |
| Read or write comments | `confluence content comments` | [references/confluence/content.md](references/confluence/content.md) (Comments) |
| Space metadata, lifecycle, instructions | `confluence space` | [references/confluence/spaces.md](references/confluence/spaces.md) |
| Hierarchy | `confluence tree` | [references/confluence/spaces.md](references/confluence/spaces.md) |
| Export | Word returns a download directly; PDF requires export-status polling | [references/confluence/content.md](references/confluence/content.md) (Exports) |
| Native selectors, first-call scope | Pass original references | [references/KNOWLEDGE-IDENTIFIERS.md](references/KNOWLEDGE-IDENTIFIERS.md) |

## Invocation And Output

Run `twg <command>`. On shell `command not found`, use `$HOME/.local/bin/twg` (macOS/Linux) / `$env:LOCALAPPDATA\Programs\twg\bin\twg.exe` (PowerShell), then tell user to add that directory to PATH. Do not treat auth or command errors as PATH failures.

Do not add per-command env prefixes unless requested; hosts may set `TWG_AGENT_DEFAULTS=1`.

- Answer from inline or already-read compact output if it supports the requested facts.
- Quote extracted facts with their sources, not whole payloads.
- For gaps, follow [references/OUTPUT.md](references/OUTPUT.md). Keep unavailable evidence unknown.
- On a restricted host, use only `twg` and permitted output files, not arbitrary host files, credentials, or other agent runs.
- Use the prompt's timezone and window.

## Auth/Setup Guard

Do not run a command that waits for user input, such as setup, login, install, upgrade, or upkeep. Give clear instructions and ask the user to run it.

## Errors in Sandboxes

For sandboxed `twg bb pipeline get`, `wait`, `grep`, or `tail`, follow [references/OUTPUT.md](references/OUTPUT.md). Log restrictions are not evidence of auth failure.

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
- `docs query` and `work query` return user activity, not title or content matches. For topic text, use `docs search` or `work search`. See [references/ROUTING.md](references/ROUTING.md).
- Pass supported original references to native reads. Avoid separate resolve calls. Person handoffs: [references/USER-IDENTIFIERS.md](references/USER-IDENTIFIERS.md).
- Command shape guardrails:
  - `work query` uses `--scope me|user`, never `--scope global`.
  - Inferred teams need explicit `--include-inferred`; see [references/inferred-teams.md](references/inferred-teams.md).
- Use `assets graph` to traverse object, owner, team, or Jira relationships. See [references/ASSETS_GRAPH.md](references/ASSETS_GRAPH.md). Otherwise use `assets search`, `assets query --aql`, or `assets object get`.

## Rules

- Never guess IDs, flags, slugs, ARIs, or write contracts.
- For a write, load the product route's rules, follow live help, and read the current state. Tell the user what the write will change, unless they asked you to run it.
- Read every loaded reference fully; a partial read counts as not loaded.
- Do not inspect local files, caches, or schemas, unless the user asks about local state.
