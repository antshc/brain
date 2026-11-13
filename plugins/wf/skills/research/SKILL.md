---
name: research
description: >-
  Investigate technical questions across source code, docs, packages, and external evidence, or search a Graphify knowledge graph. Return cited findings. Use for 'research X', 'trace this flow', 'find callers of X', 'why was X built', or 'query the graph'. Not for testing one claim → `prove`.
---

# Research

Return cited findings inline or save at caller-selected destinations. How orchestrates current-system research; Hunter executes reusable Explore requests.

## Inputs

- `@question` — research question. Ask if missing.
- `@mode` [optional] — `why` for historical rationale.
- `@whyDepth` [optional] — `anchor` for code/PR context only, or `full` (default); Why only.
- `@researchScope` [optional] — one entry per independent question: route (`system`, `cloud`, `web`), target, question. System may name a primary lens (`Behavior`, `Flow`, `Data`, `focused`). Cloud includes provider/service and whether live values matter.
- `@outputShape` [optional] — content, diagrams, framing, count; not destination policy. Preserve caller framing.
- `@outputPath` [optional] — exact final artifact path, or question-to-path mapping for multiple saved questions. Required when saving.
- `@outputBase` [optional] — caller's absolute repository/workspace root; required for relative output paths.

## Caller-owned destinations

Apply to How, Why, Cloud, Web, prompts, and templates. **MUST NOT** define default artifact directories, filenames, or lens/provider suffixes. Callers own placement conventions.

- No persistence requested → return inline; no path required. Explicit `@outputPath` requests saving.
- Save only to the caller's exact `@outputPath`. Accept a legacy explicit path in `@outputShape`; if both specify different destinations, report the conflict before writing. A directory alone is not an exact artifact path.
- Resolve a relative path against `@outputBase`; absolute paths need no base. Missing/ambiguous base → report it rather than infer one from worker CWD.
- Persistence requested without a destination → continue useful research, return findings inline, name the missing-destination blocker. For a direct user request, ask where to save after preparing the result.
- Multiple independent saved questions require an explicit question-to-path mapping. Do not derive sibling filenames. A combined report requires the caller's explicit request and one exact destination.
- Workers return evidence and drafts inline. Only the coordinator/designated saver writes the resolved final path. Worker evidence artifacts require explicit caller destinations via `@outputArtifact`, separate from final reports.

## Explore request

The caller sends this request verbatim directly to a `hunter` subagent. Hunter owns local target resolution, tool routing, read-only constraints, and evidence return. Repository evidence uses local checkouts only; missing checkouts/refs are blockers, not remote lookup requests. If Hunter is unavailable, report the blocked evidence request and continue independent work.

- `@work` — question | prompt instruction | skill name to run. Pass instructions and skill names verbatim. For a named skill, resolve its exact name and description before rendering *Load and follow the `skill-name` skill to <task>* with 3–6 description keywords; never emit placeholders literally. The worker reads its full body, selected route and required resources before acting.
- `@depth` — `quick | medium | thorough`.
- `[@shape]` — `literal | symbol | relationship | nuget`; routing hint. If omitted, Hunter classifies the request. For `relationship`, name both ends in `@work` when the question is a flow.
- `[@target]` — repository or service names as stated. Default to the current repository.
- `@outputShape` — caller's return shape. Default to Hunter's verdict.
- `[@outputArtifact]` — the one caller-designated evidence file the run may write; otherwise return inline.
- `[@inputs]` — caller-supplied inputs `@work` needs.
- `@research` — absolute base directory of this research skill; the caller always fills it. Hunter resolves Graphify resources from it.

A pure lookup (one literal, symbol, caller lookup, or package API) with no requested document or explicit inspection uses one Explore request. Return Hunter's verdict inline. Explicit inspection and requests for a document take precedence.

## Constraints

- **MUST** delegate source reading. The coordinator routes, briefs, verifies citations, synthesizes, and delivers. If delegation is unavailable, report the blocker; continue independent work.
- Send every Explore request and current-system evidence brief to `hunter`. Use read-only `general-purpose` workers for independent Cloud, Web, and Why evidence; preserve Why worker roles.
- Pass caller `@outputShape` verbatim to Why, Cloud, and Web. For system evidence, include it as report context and use the Explorer's Evidence return as inline `@outputShape`. Preserve the final destination only in coordinator delivery context.
- **MUST** find the graph covering each codebase target: `graphify-out/` under the launch repository root or the target's main checkout, never inside a git worktree (graphs are gitignored and built from the launch folder). A worktree target uses its main checkout's graph: main checkout = parent of `git -C <worktree> rev-parse --path-format=absolute --git-common-dir`; `<worktree>/<rel>` maps to `<mainCheckout>/<rel>`. When covered, paste the Graphify line verbatim, filling `<root>` with the graph root and `<research>` with this skill's absolute base directory, into codebase-reading briefs for agents other than Hunter; for a worktree, append the main-checkout→worktree path mapping. Hunter handles Graphify itself.

  > Graph available at `<root>/graphify-out/`. Before `rg`/LSP, read `<research>/how/graphify.md` and `<root>/GRAPHIFY.md` (project rules, when present) in full to orient. Run from `<root>`. Read-only overrides their write steps. Search with `<research>/scripts/focused_query.py` using the interpreter in `graphify-out/.graphify_python`, else `python3` (`resolve` + `path` for a flow; `terms`, then `query` with 1-2 identifier terms for unknown names); never `graphify query` with question text. Cite source files, not graph nodes; a missing node is never absence evidence.

## Routing

`/research why <question>` sets Why mode. Reject conflicting explicit mode/scope and Why depth outside Why. Otherwise honor supplied scope, then infer from the question. Route independent questions separately; sequence dependent evidence. Provider/data facts determining a system answer stay in How rather than separate reports. If scope is ambiguous, state a bounded interpretation and proceed. After a route returns, verify/deliver before selecting the next requested question.

| Route | Select when | Load in full | Result |
|---|---|---|---|
| Explore | Pure lookup under Explore request | No report playbook; Hunter owns procedure | Inline cited verdict or blocker |
| How | Current behavior in source, configuration, restored packages; explicit system inspection | [How](how/how.md), [Inspection evidence](how/inspection.md), [Explorer prompt](how/explorer-prompt.md), [Explainer prompt](how/explainer-prompt.md), [How report](how/report.md) | One cited current-system explanation |
| Why code anchor | `@mode=why`, `@whyDepth=anchor` | [Why](why/why.md), through Establish the Code Anchor | Cited symbols, commits, PRs, tickets, gaps; stop after anchor |
| Why | `@mode=why` | [Why](why/why.md), [Epistemics](why/epistemics.md), [Investigator prompt](why/investigator-prompt.md), [Synthesizer prompt](why/synthesizer-prompt.md), [Source playbook](why/source-playbook.md) | Rationale, source coverage, confidence |
| Cloud | Independent AWS/Azure provider question | [Cloud inspection](cloud/cloud-inspection.md), [Cloud template](cloud/cloud-inspection-template.md), selected provider below | Cited constraints and applicability |
| Web | Other external question | Generic brief below | Primary-source findings |
| Graphify | Direct graph query, path, or explain request against an existing `graphify-out/`; build, update, or export requests → report the build entry point named in `<root>/GRAPHIFY.md`, never build | [Graphify search](how/graphify.md) | Graph-oriented answer verified against source |

## Conditional resources

Read triggered resources in full from this skill base, not caller CWD. These direct links own loading; playbooks name registered resources without loading chains.

| Trigger | Resource |
|---|---|
| How checks one deployable's triggers, implementation, outcomes | [Behavior](how/behavior.md) |
| How checks cross-deployable handoffs/contracts/terminals | [Flow](how/flow.md) |
| How checks data shape, keys, ownership, consistency, migration, concurrency, retention | [Data](how/data.md) |
| Hunter needs restored NuGet API/implementation evidence, including direct Explore | [NuGet](how/nuget.md) |
| Caller needs system question examples | [How request guide](how/README.md) |
| Cloud evidence targets AWS | [AWS](cloud/aws.md) |
| Cloud evidence targets Azure | [Azure](cloud/azure.md) |
| Why searches source history | [Code archaeology](why/sources/code-archaeology.md) |
| Why searches Jira/Confluence | [Atlassian](why/sources/atlassian.md) |
| Why searches Linear | [Linear](why/sources/linear.md) |
| Why searches Notion | [Notion](why/sources/notion.md) |
| Why searches team chat | [Slack](why/sources/slack.md) |
| Why searches observability | [Datadog](why/sources/datadog.md) |
| Why searches exceptions | [Sentry](why/sources/sentry.md) |
| Why searches product analytics | [Databricks](why/sources/databricks.md) |
| Why investigates defensive code | [Incident postmortems](why/sources/incident-postmortem.md) |

## Dispatch and delivery

Large reading dispatch or material measurement claims → *Load and follow the `principles` skill to load indexed engineering principles by name*. Select `Guard the context window` for bounded source-reading briefs and `Explain the number` before relying on measurements. Keep source-based, inferred and observed evidence distinct; preserve existing delegation contracts.

For independent non-How workers, *Load and follow the `subagents` skill to dispatch independent workers with role-based models* using Dispatch. Brief question, target/refs, relevant tools/resources, caller framing, and read-only return. Why owns its investigator/synthesizer sequence; How owns current-system orchestration. No inaccessible target blocks unrelated work.

Cloud briefs include provider, mode (`question` or `implementation`), services, operations, region, account/subscription, relevant dimensions, and need for live values. Pass the loaded contract, template, and selected provider; request the filled report inline.

Reconcile conflicts with focused checks; redispatch material gaps and fix mechanical defects. Apply Caller-owned destinations. No findings → state completed scope and checked sources. Incomplete → name missing evidence and consequence. Preserve Why confidence language.

## Generic brief

Use a read-only `general-purpose` worker with web access. Cite material claims in place from primary sources: official documentation, source code, specifications, first-party APIs. Return findings inline for coordinator verification and caller-directed delivery.

## Completion criteria

- Each independent question has its requested artifact at the exact caller destination, inline findings, or a named blocker. Each How explanation follows How report; saved paths and framing match the caller.
- Material factual claims carry in-place primary-source citations. Assumptions/unknowns and runtime observations remain distinct from static evidence.
- Included Mermaid blocks render; remove template placeholders, Rules blocks, and unfilled sections.
- Codebase targets covered by a graph, including worktrees via their main checkout, record queries or skip reasons in evidence.
