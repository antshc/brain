---
name: research
description: >-
  Research primary sources and save cited findings as Markdown. Use for 'research X', 'how is this system built', 'verify this NuGet API', or 'check this cloud limit'.
---

# Research

## Inputs

- `@question` — research question. Ask if missing.
- `@outputShape` [optional] — requested file count, paths, diagrams, or framing.

## Constraints

- **MUST** delegate source reading. Parent routes, briefs, and verifies to keep raw evidence in subagent context. If delegation is unavailable, report the blocker.
- **MUST** pass `@outputShape` verbatim to every subagent. It takes precedence over report defaults.

## Workflow

1. **Route.** Split by evidence owner. System inspection covers repository code, config, and restored NuGet packages. Cloud inspection covers AWS and Azure services, IAM/RBAC, APIs, SDKs, quotas, and resource state, one part per provider. Generic brief covers other providers and external sources. *Done when* every part has a route.
2. **Brief and dispatch.** Brief from the question and route. Mark missing names, symbols, or account details `unknown`. Spawn one subagent per part with route tools, question, brief, output shape, and applicable contract, reference, and template paths. Resolve absolute paths from the skill base. Parallelize independent parts. Default to one cited Markdown report per part. *Done when* each part has a subagent report or blocker.
3. **Verify.** Check each artifact against Completion criteria. Fix mechanical defects directly. Redispatch evidence defects with the violated constraint first. Route Data and cloud follow-ups as new parts. Offer Behavior follow-ups. Run on request. *Done when* every part and follow-up is accounted for.

## System inspection

Read [system-inspection.md](system/system-inspection.md) to brief. Select one axis below or request a focused report for an isolated lookup or package API question. Include named deployables or repositories and planned lookups with `@shape` and `@depth` from Codebase lookups. Quote literals and symbols exactly. Subagent reads the contract and any selected axis reference and template in full, applies Codebase lookups, and inspects as built.

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
