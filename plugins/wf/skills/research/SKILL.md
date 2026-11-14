---
name: research
description: >-
  Investigate technical questions across source code, docs, packages, and external evidence, or search a Graphify knowledge graph. Return cited findings. Use for 'research X', 'trace this flow', 'find callers of X', 'why was X built', or 'query the graph'. Not for testing one claim → `prove`.
---

# Research

Select a route, investigate, verify, and explain directly in the invoking agent. **MUST NOT** spawn subagents, including through invoked helpers. The caller owns delegation: caller → Hunter → Research for delegated research; caller → Research for direct execution. Loading this skill never launches Hunter. Stop when the bounded question is answered.

## Inputs

- `@question` — research question; accept a legacy question/prompt in `@work`. Ask if both are missing. Preserve both when `@work` supplies checks for `@question`.
- `@route` [optional] — `auto | explore | how | why | cloud | web | graphify`; default `auto`.
- `@mode` [optional] — `why` for historical rationale.
- `@whyDepth` [optional] — `anchor` for code/PR context only, or `full` (default); Why only.
- `@researchScope` [optional] — one entry per independent question: route (`system`, `cloud`, `web`), target, question. System may name a primary lens (`Behavior`, `Flow`, `Data`, `focused`). Cloud includes provider/service and whether live values matter.
- `@outputShape` [optional] — content, diagrams, framing, count; not destination policy. Preserve caller framing.
- `@outputPath` [optional] — exact final artifact path, or question-to-path mapping for multiple saved questions. Required when saving.
- `@outputBase` [optional] — caller's absolute repository/workspace root; required for relative output paths.

## Caller-owned destinations

Apply to every route and resource. **MUST NOT** define default artifact directories, filenames, or lens/provider suffixes.

- No persistence requested → return inline; no path required. Explicit `@outputPath` requests saving when the current execution context permits it.
- Save only to the caller's exact `@outputPath`. Accept a legacy explicit path in `@outputShape`; conflicting destinations block writes. A directory alone is not an exact artifact path.
- Resolve a relative path against `@outputBase`; absolute paths need no base. Missing/ambiguous base blocks saving, not useful research; never infer it from a worker CWD.
- Persistence requested without a destination → return findings inline, name the missing-destination blocker. For a direct user request, ask where to save after preparing the result.
- Multiple independent saved questions require an explicit question-to-path mapping. Do not derive sibling filenames. A combined report requires an explicit request and one exact destination.
- Under Hunter, return the complete requested report inline for the caller to save at its resolved final path. Only the brief's exact `@outputArtifact` is a permitted repository write; it is separate from final report delivery. Preserve final destination context for citations and caller saving. Direct execution may save the exact requested final report.

## Explore request

These inputs describe a direct lookup, not another agent launch. Delegating callers send the complete request to Hunter with an instruction to load Research and `@route: explore`; workers needing their own evidence invoke Research directly. Repository evidence uses local checkouts only; missing checkouts/refs are blockers, not remote lookup requests.

- `@work` — question | prompt instruction | skill name to run. Preserve instructions and names. For a named skill, resolve its exact name/description before rendering *Load and follow the `skill-name` skill to <task>* with 3–6 description keywords; never emit placeholders literally. Read full body, selected route and required resources; execute in this agent within Research's constraints.
- `@depth` — `quick | medium | thorough`; default `medium`.
- `[@shape]` — `literal | symbol | relationship | nuget`; lookup hint. Infer when absent. For a flow, name both ends in `@work` or `@question`.
- `[@target]` — repository or service names as stated. Default to the current repository.
- `@outputShape` — caller's return shape. Default to the local-search verdict.
- `[@outputArtifact]` — the one caller-designated evidence file a delegated run may write; otherwise return inline.
- `[@inputs]` — caller-supplied inputs the work needs.

## Read-only contract

**MUST NOT** modify source, configuration, external state, or graph data; run builds, restores, git writes, or graph builds/updates. Use authorized read-only tools and queries. Keep state-changing probes outside Research; report claim, consequence, blocker and exact next check.

Exceptions: write the brief's `@outputArtifact` and nothing else in the repository under Hunter; direct execution may write its exact resolved final report. Allow per-user `rg`/`ilspycmd` installation, decompilation written only to the resolved NuGet package cache, `graphify query | path | explain` updating `graphify-out/cache/`, and the pinned Research requirements install in the selected interpreter. No other graph writes. Caller restrictions may narrow these exceptions.

Use absolute paths. Resolve `@skillBase` from the loaded Research directory, never caller CWD. Repository source and package evidence use Local search. Missing tools/access block only the dependent checks; continue independent evidence. Run independent tool queries together; sequence dependent checks. Keep source behavior, documented intent, inferred conclusions and runtime observations distinct.

## Routing

`/research why <question>` sets Why mode. Honor an explicit compatible `@route`, then supplied scope, then infer. Reject unknown routes, conflicting explicit route/mode/scope, or Why depth outside Why before dependent work. `system` scope selects Explore for a pure lookup and How for behavior/inspection. An explicit How route may answer a narrow lookup with a concise explanation; Explore cannot silently discard a requested inspection/report. Use Why anchor when requested.

Auto: one literal, symbol, caller or package API lookup without a document/inspection → Explore; current mechanism/inspection → How; historical motivation → Why; independent provider question → Cloud; direct existing-graph request → Graphify; other external question → Web. Ambiguous scope → state a bounded interpretation and proceed. Route independent questions separately; sequence dependent evidence. Provider/data facts deciding a system answer remain within How. Verify/deliver each requested question before the next.

Read the entire selected procedure and required resources before acting. Load only selected or triggered resources, directly from this index.

| Route | Load in full | Result |
|---|---|---|
| Explore | Local search below; NuGet/Graphify when triggered | Inline cited verdict or blocker |
| How | [How](how/how.md), [Inspection evidence](how/inspection.md), [Evidence checklist](how/explorer-prompt.md), [How report](how/report.md), Local search | One cited current-system explanation |
| Why code anchor | [Why](why/why.md), through Establish the Code Anchor; Local search | Cited symbols, commits, PRs, tickets, gaps; stop after anchor |
| Why | Why, [Epistemics](why/epistemics.md), [Source investigation](why/investigator-prompt.md), [Why report](why/synthesizer-prompt.md), [Source playbook](why/source-playbook.md), Local search | Rationale, source coverage, confidence |
| Cloud | [Cloud inspection](cloud/cloud-inspection.md), [Cloud template](cloud/cloud-inspection-template.md), selected provider below | Cited constraints and applicability |
| Web | Web procedure below | Primary-source findings |
| Graphify | [Graphify search](how/graphify.md), Local search | Graph-oriented answer verified against source; build/update/export requests return project build entry point, never build |

## Conditional resources

Read triggered resources in full from this skill base, not caller CWD. These direct links own loading; playbooks name registered resources without loading chains.

| Trigger | Resource |
|---|---|
| Any route reads local source, history anchors or package caches | [Local search](tactics/local-search.md) |
| How checks one deployable's triggers, implementation, outcomes | [Behavior](how/behavior.md) |
| How checks cross-deployable handoffs/contracts/terminals | [Flow](how/flow.md) |
| How checks data shape, keys, ownership, consistency, migration, concurrency, retention | [Data](how/data.md) |
| Restored NuGet API/implementation evidence, including Explore or Cloud SDK checks | [NuGet](how/nuget.md) |
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

## Verification and delivery

Large reading scope or material measurement claims → *Load and follow the `principles` skill to load indexed engineering principles by name*. Select `Guard the context window` for bounded source reading and `Explain the number` before relying on measurements.

For Cloud facts within How, load Cloud inspection, its template and the selected provider directly from this index. Bound provider, mode (`question` or `implementation`), services, operations, region, account/subscription, relevant dimensions and need for live values. Investigate in this agent; integrate deciding facts into the same explanation.

Reconcile conflicts and check material gaps directly. Apply Caller-owned destinations. No findings → state completed scope and checked sources. Incomplete → name missing evidence and consequence. Preserve Why confidence language.

## Web procedure

Search and read primary sources using available authorized web tools: official documentation, source specifications and first-party APIs. Cite material claims in place; distinguish versions and applicability. Repository implementation evidence still requires a local checkout. Missing web access → name the exact gap; do not substitute uncited recollection. Return findings inline or apply Caller-owned destinations.

## Gotchas

- `scripts/focused_query.py` needs `graphifyy` and `networkx`. Before first run, read `scripts/requirements.txt` in full from `@skillBase`.
- `ModuleNotFoundError` for `graphify`/`networkx` → install with the selected interpreter: `<python> -m pip install -r <skillBase>/scripts/requirements.txt`; rerun. Skip install when imports succeed.
- Install only requirements.txt; **MUST NOT** upgrade or unpin versions. If caller restrictions prevent install, use the documented fallback and report coverage limits.

## Completion criteria

- Each independent question has its requested artifact at the exact permitted destination, inline findings for caller saving, or a named blocker. Each How explanation follows How report.
- Material factual claims carry in-place primary-source citations. Assumptions/unknowns and runtime observations remain distinct from static evidence.
- Included Mermaid blocks render or carry an explicit rendering blocker; remove template placeholders, Rules blocks, and unfilled sections.
- Covered codebase targets, including worktrees via their main checkout, record graph queries or skip reasons.
- All investigation, verification and synthesis ran in this agent. Last, sweep the original question and requested branches against evidence; resolve omissions or name their consequence and next check.
