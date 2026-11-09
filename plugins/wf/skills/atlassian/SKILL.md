---
name: atlassian
description: >-
  Fetch, publish, convert, and query Jira and Confluence content, and address page comments. Use for 'fetch PROJ-123', 'read this Confluence page', 'publish Markdown to Confluence', 'create a Jira story', JQL or CQL search. Not for connection facts → `preflight-atlassian`.
---

# Atlassian

**Args start with `help`** → follow [help.md](help.md) before anything else: `help` alone prints every tactic and command; `help <request>` names the tactic and command for the request and runs nothing.

Operations and tactics for Jira and Confluence. Pick the tactic by trigger, load only its reference, run it, then re-evaluate: a result that changes the next action (search hit → body read, fetched page → edit) selects the next tactic.

## Tactics

| Tactic | Trigger | Load | Result |
|---|---|---|---|
| **Fetch work** | Jira key/URL, or a selected Jira search result, needs its full body | [references/fetch-work.md](references/fetch-work.md) | `work.md` + assets + linked `work.comments.json` sidecar or failure note |
| **Publish work** | Create or update a Jira work item, issue, story, task, bug, or epic from Markdown; repeat once per item | [references/publish-work.md](references/publish-work.md) | Key, URL, attachment outcomes, read-back when ADF-only constructs exist |
| **Fetch page** | Confluence page ID/URL/tiny link, or a selected search hit, needs its full body | [references/fetch-page.md](references/fetch-page.md) | `page.md` with anchors, assets, comments per mode |
| **Publish page** | Publish local Markdown to Confluence, or edit an existing page without replying to threads | [references/publish-page.md](references/publish-page.md) | Page URL, diagram/attachment and anchor outcomes, verify result |
| **Address page comments** | Settle open review comments on a Confluence page and reply to each thread; 'address page comments', 'reply to review comments' | [references/address-page-comments.md](references/address-page-comments.md) | Targeted in-place edits, one confirmed reply per pending thread, gate report |
| **Install** | Explicit request to install or set up ATL in a repo, refresh `preflight-atlassian`, or generate or migrate `pub-*` wrappers; 'install atlassian' | [references/install.md](references/install.md) | Plugin status, preflight files, config keys added, wrapper paths, missing prerequisites |
| **Map Markdown** | Convert Markdown/ADF, or decide whether Markdown alone carries a document | [references/map-markdown-adf.md](references/map-markdown-adf.md) | ADF JSON, Markdown, or construct report; offline |
| **Query or operate with TWG** | Search, discovery, metadata, people, links, transitions, comments, sprints, or other non-body operations | [references/twg.md](references/twg.md), then the TWG routes row | Credentialed `twg` result |

Address page comments runs only on an explicit review-thread request; an ordinary edit never triggers it.

Out of scope here: daily blocked items and @mentions → *run `daily-briefing` skill for the daily briefing, standup update, blocked work items, and unanswered mentions*.

## Shared constraints

1. **Preflight once per site.** Before the first operation: *run `preflight-atlassian` skill to resolve site, default project key, default space id, credentialed twg command, and token availability from `.atlassian.json.user` config* **Action: Resolve**. Keep `configPath`, `site`, `twg`, `defaultProjectKey`, `defaultSpaceId`, `tokenAvailable`, `accountId`. Later operations in the same request on the same site reuse them; a different site, or a missing fact a tactic needs, re-runs it. Map Markdown and Install need no Preflight.
2. **CLI.** `<skillDir>` = the parent of this `SKILL.md`. Body operations run `python3 <skillDir>/scripts/atl.py <command> ...` from any working directory; pass `--config "<configPath>"`, never credentials.
3. **Body transport.** Full Jira descriptions and Confluence page bodies move over REST + ADF through `atl.py` only. Search, discovery, metadata, Jira comments, transitions, and every other non-body operation use Preflight's `<twg>`. Never use the Atlassian MCP. Request Markdown, never HTML, from twg; the only HTML exception is the Address page comments tactic's targeted edits.
4. **Fallbacks.** Each fetch reference names its lossy twg fallback and warning; use it only when `atl.py` is unavailable or fails for a non-auth reason. Auth failure or policy denial → stop and report; no fallback.
5. **Read-only intents** (read, show, summarize, search, compare) issue no create, update, transition, comment, attach, or publish call.
6. **Prerequisites.** `tokenAvailable` false, `atlassian-python-api` missing or unsupported, or Preflight unavailable → ask the user to run `/atlassian install` (Install tactic) in Copilot CLI, then stop; never start it unasked.

## TWG routes

Read [references/twg/jira/rules.md](references/twg/jira/rules.md) before any Jira write or authoritative Jira answer, and [references/twg/confluence/rules.md](references/twg/confluence/rules.md) before any Confluence write or pre-edit read. Then load the narrowest row.

| Intent | Load |
|---|---|
| Known or several known work items, related artifacts, links | [references/twg/jira/workitems.md](references/twg/jira/workitems.md) |
| Jira fuzzy text, exact JQL, board, backlog, sprint ordering | [references/twg/jira/querying.md](references/twg/jira/querying.md) |
| Duplicate work item detection | [references/twg/jira/duplicates.md](references/twg/jira/duplicates.md) and Jira querying |
| Field metadata, required fields, transitions | [references/twg/jira/fields-and-transitions.md](references/twg/jira/fields-and-transitions.md) |
| Jira comments, mentions, rich text outside Publish work | [references/twg/jira/rich-content.md](references/twg/jira/rich-content.md) |
| Jira configuration | [references/twg/jira/administration.md](references/twg/jira/administration.md) |
| Confluence CQL, date-filtered lists, fuzzy page discovery | [references/twg/confluence/querying.md](references/twg/confluence/querying.md) |
| Paginated content list | [references/twg/confluence/pagination.md](references/twg/confluence/pagination.md) |
| Comments, embeds, smart links, exports, non-Markdown content | [references/twg/confluence/content.md](references/twg/confluence/content.md) |
| twg-native page edits (outside Publish page) | [references/twg/confluence/editing.md](references/twg/confluence/editing.md), [references/twg/confluence/body-formats.md](references/twg/confluence/body-formats.md) |
| Spaces, space instructions, hierarchy | [references/twg/confluence/spaces.md](references/twg/confluence/spaces.md) |
| Native selectors, first-call scope | [references/twg/KNOWLEDGE-IDENTIFIERS.md](references/twg/KNOWLEDGE-IDENTIFIERS.md) |
| People, teams, reporting lines | [references/twg/USER-IDENTIFIERS.md](references/twg/USER-IDENTIFIERS.md) |
| Inferred teams | [references/twg/inferred-teams.md](references/twg/inferred-teams.md) |
| Work, docs, activity rollups | [references/twg/ROUTING.md](references/twg/ROUTING.md) |
| Assets objects and graph | [references/twg/ASSETS_GRAPH.md](references/twg/ASSETS_GRAPH.md) |
| Help, discovery, diagnostics | [references/twg/HELP.md](references/twg/HELP.md) |
| Output gaps, sandboxed logs | [references/twg/OUTPUT.md](references/twg/OUTPUT.md) |

Current user's personal space → `<twg> confluence space me`; reuse the returned identity, never infer it.

## Gotchas

- **MUST NOT** `find`/`grep`/`ls -R` to locate this skill's directory; use the parent of the `SKILL.md` path you were given.
- Read every loaded reference fully; a partially read reference counts as not loaded.
- **MUST NOT** echo `email`/`apiToken`. `-o json --output-file` files are unredacted; extract needed fields with Python.
- `<twg>` exit `127` → report missing "twg CLI". **MUST NOT** run `twg login`, `setup`, or any interactive command.
