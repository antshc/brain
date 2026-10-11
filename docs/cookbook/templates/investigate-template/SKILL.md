---
name: investigate-template
description: Investigates unknown code paths, dependency flows, legacy behavior, and design rationale; returns evidence-backed findings, contradictions, and explicit uncertainty.
---

# Investigation Skill Template

## Inputs
- `{{question|Behavior or rationale to explain}}`
- `{{scope|Repository, components, and observable boundaries}}`

## Workflow
1. Trace `{{entryPoint|Input or initiating event}}` through the current implementation to `{{outcome|Observable result}}`; identify responsible symbols. *Done when* each relevant boundary has a source.
2. Collect independent code, history, and runtime evidence; record exact searches, empty results, and conflicts. *Done when* findings have traceable evidence.
3. Separate documented intent, supported inference, and unknowns. *Done when* explanations do not overstate their evidence.

## Guardrails
- MUST NOT use `_backup/` or `_in-progress/` as current guidance.
- MUST NOT treat an inferred cause as proven rationale.

## Completion criteria
- Answer `{{question}}` with a source-backed flow, contradictions, and unresolved gaps.

## Handoff
- `{{findings|Symbols, sources, confidence, open questions}}`
