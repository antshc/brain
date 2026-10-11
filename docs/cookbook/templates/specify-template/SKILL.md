---
name: specify-template
description: Specifies ambiguous feature intent, stakeholder constraints, scope, quality thresholds, and acceptance outcomes before downstream design or implementation.
---

# Requirements Skill Template

## Inputs
- `{{request|User problem and intended outcome}}`
- `{{stakeholders|Decision owner and affected consumers}}`

## Workflow
1. Restate user intent and list assumptions or conflicts; ask for the minimum missing decision. *Done when* the intended capability is unambiguous or blockers explicit.
2. Evaluate meaningful alternatives and reject unnecessary scope. *Done when* selected and excluded capabilities are distinguished.
3. Write observable scenarios, boundaries, quality thresholds, and open questions. *Done when* a consumer can decide whether the result is complete.
4. Record approval or unresolved decision ownership before planning. *Done when* the requirements status is explicit.

## Guardrails
- MUST NOT silently choose between conflicting requirements.
- MUST NOT start implementation as part of specification work.

## Completion criteria
- `{{specification|Scope, scenarios, constraints, acceptance outcomes, unresolved decisions}}` exists and reflects stakeholder intent.

## Handoff
- `{{decisionStatus|Approved, provisional, or blocked; decision owner}}`
