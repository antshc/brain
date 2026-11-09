---
name: research
description: >-
  Investigate primary sources and save a cited Markdown document. Use for 'research X', 'investigate X', 'why was this built this way', 'verify this NuGet API', 'check this cloud limit'. Not for inline lookups → `explore-codebase`.
---

# Research

## Inputs

- `@question` — research question. Ask if missing.
- `@mode` [optional] — `how` or `why`.
- `@whyDepth` [optional] — `anchor` for code and PR context only, or `full` (default). Use only with `why`.
- `@researchScope` [optional] — one entry per research part with route (`system`, `cloud`, or `web`), target when known, system axis when applicable (`Behavior`, `Flow`, `Data`, or `focused`), and a part question for multi-part requests. Cloud entries include provider, service, and whether live values matter.
- `@outputShape` [optional] — requested file count, paths, diagrams, or framing.

## Constraints

- **MUST** delegate source reading. Parent routes, briefs, and verifies to keep raw evidence in subagent context. If delegation is unavailable, report the blocker.
- **MUST** pass `@outputShape` verbatim to every subagent. It takes precedence over report defaults.

## Entry routes

`/research how <question>` and `/research why <question>` set the corresponding mode. Reject conflicting explicit mode and scope, or Why depth on any other route. With no explicit mode, use Workflow and preserve the existing scoped or inferred inspection routes.

| Action | Load in full | Return |
| --- | --- | --- |
| **How** | [How](how/how.md), [explainer prompt](how/explainer-prompt.md), [explorer prompt](how/explorer-prompt.md) on the complex path | Cited explanation of current behavior. |
| **Why code anchor** (`@mode=why`, `@whyDepth=anchor`) | [Why](why/why.md). Execute through Establish the Code Anchor. | Cited symbols, commits, PRs, linked tickets and gaps. Stop after the anchor. |
| **Why** (`@mode=why`) | [Why](why/why.md), [epistemics](why/epistemics.md), [investigator prompt](why/investigator-prompt.md), [synthesizer prompt](why/synthesizer-prompt.md), [source playbook](why/source-playbook.md) | Cited rationale, source coverage and confidence. |

For full Why, load only the relevant source playbooks in full: [code archaeology](why/sources/code-archaeology.md), [Atlassian](why/sources/atlassian.md), [Linear](why/sources/linear.md), [Notion](why/sources/notion.md), [Slack](why/sources/slack.md), [Datadog](why/sources/datadog.md), [Sentry](why/sources/sentry.md), [Databricks](why/sources/databricks.md), and [incident postmortems](why/sources/incident-postmortem.md) for defensive code.

For How or Why, pass the original question, named targets or refs, and `@outputShape` to each brief. Keep evidence workers read-only. The Research coordinator verifies citations, saves the Markdown output to the requested path or `docs/research/<slug>.md`, and returns its path and any gaps. A caller may request the Why code anchor inline. If evidence is missing, report the gap with any verified results.

## Workflow

1. **Route.** When `@researchScope` is supplied, use each entry's route, target, applicable axis, and question (or `@question` for a single part). Route `system` to system inspection, `cloud` to cloud inspection for AWS or Azure (generic brief for other providers), and `web` to the generic brief. If a specified target is inaccessible, report that part as blocked and offer any viable alternative. Continue independent parts. Without `@researchScope`, split by evidence owner. System inspection covers repository code, config, and restored NuGet packages. Cloud inspection covers AWS and Azure services, IAM/RBAC, APIs, SDKs, quotas, and resource state, one part per provider. Generic brief covers other providers and external sources. *Done when* every part has a route.
2. **Brief and dispatch.** Brief each part from its routed question, target, and applicable axis. Mark missing names, symbols, or account details `unknown`. For one worker per part, *run `subagents` skill to dispatch independent workers with isolated outputs* using **Dispatch**. Pass route tools, question, brief, output shape, and applicable contract, reference, and template paths. Resolve absolute paths from the skill base. Parallelize independent parts. Default to one cited Markdown report per part. *Done when* each part has a subagent report or blocker.
3. **Verify.** Check each artifact against Completion criteria. Fix mechanical defects directly. Redispatch evidence defects with the violated constraint first. Route Data and cloud follow-ups as new parts. Offer Behavior follow-ups. Run on request. *Done when* every part and follow-up is accounted for.

## System inspection

Read [system-inspection.md](system/system-inspection.md) to brief. Use the supplied axis when present (`focused` requests a focused report). Otherwise select one axis below or request a focused report for an isolated lookup or package API question. Include named deployables or repositories and planned lookups with `@shape` and `@depth` from Codebase lookups. Quote literals and symbols exactly. Subagent reads the contract and any selected axis reference and template in full, applies Codebase lookups, and inspects as built.

| Axis | Select for | Reference | Template |
|---|---|---|---|
| Behavior | One deployable's functional slice or implementation choice | [behavior-inspection.md](system/behavior-inspection.md) | [behavior-inspection-template.md](system/behavior-inspection-template.md) |
| Flow | Handoffs and contracts across deployables | [flow-inspection.md](system/flow-inspection.md) | [flow-inspection-template.md](system/flow-inspection-template.md) |
| Data | One data boundary, including keys, ownership, consistency, migration, concurrency, retention, or deletion | [data-inspection.md](system/data-inspection.md) | [data-inspection-template.md](system/data-inspection-template.md) |

## Cloud inspection

Read [cloud-inspection.md](cloud/cloud-inspection.md) to brief. Include provider, mode (`question` or `implementation`), services, operations, region, account or subscription, relevant dimensions, and need for live values. Subagent reads the contract, selected provider reference, and [cloud-inspection-template.md](cloud/cloud-inspection-template.md) in full, then researches read-only with CLI, docs servers, and web access as needed.

| Provider | Reference |
|---|---|
| AWS | [aws.md](cloud/aws.md) |
| Azure | [azure.md](cloud/azure.md) |

## Generic brief

Use a general-purpose subagent with web access. Cite each claim in place from its primary source (official docs, source code, specifications, or first-party APIs). Write to `docs/research/<slug>.md` unless `@outputShape` names a location.

## Output

- Return artifact paths, cited findings, unknowns, and any Data, Behavior, or cloud follow-ups.
- No findings: report the completed scope and sources checked.
- Incomplete: return verified artifacts and identify blocked parts or missing evidence.

## Completion criteria

- Every part has an artifact or a named blocker. Artifacts match route and requested paths, count, diagrams, and framing.
- Every factual claim has an in-place primary-source citation. Mark assumptions and unknowns. Use the inspection contract's citation format where applicable.
- Every Mermaid block renders. Remove template placeholders, Rules blocks, and unfilled sections.
