---
name: orchestrate-template
description: Orchestrates bounded parallel agents, ownership, handoff contracts, context isolation, stop orders, and verifiable autonomous delivery.
---

# Orchestration Skill Template

## Inputs
- `{{objective|Outcome and finish condition}}`
- `{{workers|Available agents, scopes, and concurrency bounds}}`

## Workflow
1. Partition work by independent ownership, dependencies, and verifiable results. *Done when* assignments do not conflict.
2. Delegate each slice with files, inputs, immutable constraints, and output contract. *Done when* every worker can act without parent context.
3. Track actual file or system effects, not progress claims; replace stalled workers within `{{limits|Resource and time budget}}`. *Done when* changes have evidence.
4. Integrate worker results, review diffs, propagate stop orders, and enforce the unchanged finish condition. *Done when* the final state is independently checked.

## Guardrails
- MUST NOT silently replace required delegation with parent execution, even when faster.
- MUST NOT let multiple workers mutate the same owned state without coordination.

## Completion criteria
- Each assigned slice has verified output, unresolved blockage, or explicit cancellation; stop orders are honored.

## Handoff
- `{{ledger|Assignments, worker results, evidence, decisions, next steps}}`
