---
name: research
description: >-
  Investigate primary sources; save a cited Markdown document or return an inline read-only lookup. Use for 'research X', 'how does this work', 'inspect this system', 'where is', 'what calls', 'why was this built this way', 'verify this NuGet API', or 'check this cloud limit'.
---

# Research

Investigate current systems, historical rationale, cloud services, and web sources. Save cited findings or return a read-only lookup inline.

## Inputs

- `@question` — research question. Ask if missing.
- `@mode` [optional] — `why` for historical rationale.
- `@whyDepth` [optional] — `anchor` for code and PR context only, or `full` (default). Use only with `why`.
- `@researchScope` [optional] — one entry per independent research question with route (`system`, `cloud`, or `web`), target when known, and the question if there are several. System entries may name a primary lens (`Behavior`, `Flow`, `Data`, or `focused`). Cloud entries include provider, service, and whether live values matter.
- `@outputShape` [optional] — requested paths, diagrams, framing, or count for independent questions. Each system question produces one document.

## Explore request

The caller sends this request verbatim directly to a `hunter` subagent. Hunter owns target resolution, tool routing, read-only constraints, and evidence return. If Hunter is unavailable, report the blocked evidence request and continue independent work.

- `@work` — one of: question | prompt instruction | skill name to run. Pass instructions and skill names verbatim.
- `@depth` — `quick | medium | thorough`.
- `[@shape]` — `literal | symbol | relationship | nuget`; routing hint. If omitted, Hunter classifies the request.
- `[@target]` — repository or service names as stated. Default to the current repository.
- `@outputShape` — caller's return shape. Default to Hunter's verdict.
- `[@outputArtifact]` — the one file the run may write.
- `[@inputs]` — caller-supplied inputs `@work` needs.

A pure lookup (one literal, symbol, caller lookup, or package API) with no requested document or explicit inspection uses one Explore request. Return Hunter's verdict inline. Explicit inspection and requests for a document take precedence.

## Constraints

- **MUST** delegate source reading. The coordinator routes, briefs, verifies citations, and writes the system report. If delegation is unavailable, report the blocker.
- Send every Explore request and current-system evidence brief to `hunter`. Use read-only `general-purpose` workers for independent Cloud, Web, and Why evidence, allowing only a designated output artifact. Preserve the Why worker roles.
- For Why, Cloud, and Web, pass caller-provided `@outputShape` verbatim. In a system evidence brief, pass it as report context and set the worker's inline `@outputShape` to the explorer prompt's Evidence return. Only the coordinator applies the requested report path.
- **MUST** check codebase target roots for `graphify-out/`. When present, paste the **Graphify line** verbatim, with `<root>` filled, into codebase-reading briefs sent to agents other than Hunter. Hunter handles Graphify itself.

  > Graph available at `<root>/graphify-out/`. Before `rg`/LSP, *run `graphify` skill for codebase architecture, file relationships, and knowledge-graph query, path, explain* to orient. Read-only overrides its write steps. No `skill` tool → run `graphify query | path | explain` from the shell instead. Cite source files, not graph nodes; a missing node is never absence evidence.

## Entry routes

`/research why <question>` sets Why mode. Reject conflicting explicit mode and scope, or Why depth outside Why. Otherwise use Workflow.

| Action | Load in full | Return |
| --- | --- | --- |
| **Why code anchor** (`@mode=why`, `@whyDepth=anchor`) | [Why](why/why.md). Execute through Establish the Code Anchor. | Cited symbols, commits, PRs, linked tickets and gaps. Stop after the anchor. |
| **Why** (`@mode=why`) | [Why](why/why.md), [epistemics](why/epistemics.md), [investigator prompt](why/investigator-prompt.md), [synthesizer prompt](why/synthesizer-prompt.md), [source playbook](why/source-playbook.md) | Cited rationale, source coverage and confidence. |

For full Why, load only the relevant source playbooks in full: [code archaeology](why/sources/code-archaeology.md), [Atlassian](why/sources/atlassian.md), [Linear](why/sources/linear.md), [Notion](why/sources/notion.md), [Slack](why/sources/slack.md), [Datadog](why/sources/datadog.md), [Sentry](why/sources/sentry.md), [Databricks](why/sources/databricks.md), and [incident postmortems](why/sources/incident-postmortem.md) for defensive code.

Pass the original question, named targets or refs, and `@outputShape` to Why workers. Return the code anchor inline when requested. Otherwise save the cited rationale to the requested path or `docs/research/<slug>.md`.

## Workflow

1. **Route.** Apply a supplied scope to each question. Otherwise infer the route from the question. Use System for current behavior in repository code, config, and restored packages. Use Cloud for independent AWS or Azure questions and the generic Web brief for other external questions. Keep any provider or data fact that determines a system answer in that answer. If a target is inaccessible, report the blocked part and continue independent work.
2. **Brief and dispatch.** Apply System research below or brief each independent Cloud or Web worker with the question, target, route tools, references, and output shape. Mark missing target details unknown. *Run `subagents` skill using **Dispatch*** for independent workers, with isolated outputs when they write. Parallelize independent evidence and sequence dependent checks.
3. **Verify and return.** Reconcile evidence conflicts with focused checks. Fix mechanical defects and redispatch material evidence gaps. Return artifact paths and unresolved gaps or, for a pure lookup, Hunter's inline verdict. If no findings are available, state the completed scope and sources checked.

## System research

1. Load [System inspection](system/system-inspection.md) and [How](how/how.md) for every saved current-system answer. Use the inspection rules to select depth and the relevant lenses. Read only the selected lens references.
2. Load the [Explorer prompt](how/explorer-prompt.md). Fill it per evidence pass with the original question, assigned angle, named targets or refs, depth, and applicable lens checks. Send the filled prompt verbatim as `@work` directly to Hunter in an Explore request. Use one focused pass for a narrow question and split complex evidence only where useful. Workers return cited evidence and gaps inline.
3. Apply the evidence and runtime checks. If provider semantics or live values determine the answer, use the applicable Cloud inspection checks to request inline evidence without a separate report. Resolve material conflicts or name the unresolved claim and exact next check. Integrate the findings and save one cited Markdown document using How.

## Cloud inspection

Read [cloud-inspection.md](cloud/cloud-inspection.md) to brief. Include provider, mode (`question` or `implementation`), services, operations, region, account or subscription, relevant dimensions, and need for live values. Subagent reads the contract, selected provider reference, and [cloud-inspection-template.md](cloud/cloud-inspection-template.md) in full, then researches read-only with CLI, docs servers, and web access as needed.

| Provider | Reference |
|---|---|
| AWS | [aws.md](cloud/aws.md) |
| Azure | [azure.md](cloud/azure.md) |

## Generic brief

Use a general-purpose subagent with web access. Cite each claim in place from its primary source (official docs, source code, specifications, or first-party APIs). Write to `docs/research/<slug>.md` unless `@outputShape` names a location.

## Completion criteria

- Every independent question has its requested artifact, inline verdict, or named blocker. Each system document follows How and preserves the requested path and framing.
- Every material factual claim has an in-place primary-source citation. Mark assumptions and unknowns. Separate runtime observations from static evidence.
- Every included Mermaid block renders. Remove template placeholders, Rules blocks, and unfilled sections.
- Every codebase target with `graphify-out/` has its queries or skip reason recorded in the evidence.
