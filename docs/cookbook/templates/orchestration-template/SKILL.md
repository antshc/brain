---
name: orchestration-template
description: Coordinates multiple coding agents, bounded delegated work, independent ownership, shared progress tracking, stop orders, and verified aggregation.
---

<!-- @: Copy into a concrete skill folder; rename folder and frontmatter name, then replace all task placeholders. -->

# Agent orchestration

## Objective and roles
- Objective: {{objective|Fixed success predicate and task scope}}
- Workers: {{workers|Specialties, owned files, concurrency limits}}

## Delegation contracts
1. Partition work by dependencies and independent state ownership. *Done when* assignments avoid conflicts.
2. Delegate goals, inputs, immutable constraints, output artifacts, and evidence requirements. *Done when* workers can execute without inherited hidden state.
- MUST NOT replace required delegation with parent execution even when faster.

## Coordination ledger
- {{ledger|Owner, task, state, side effects, errors, blockers}}
3. Judge progress by real changes and evidence; reconcile blocked or stalled work. *Done when* status matches actual state.
- MUST NOT allow concurrent writes to shared files or state without a single coordinator.

## Aggregation and stop
4. Inspect worker outputs and integrate them against the unchanged predicate. *Done when* all slices have a disposition.
- {{stop|Cancellation, escalation, and immediate no-writes handling}}
- MUST propagate operator stop orders to all active workers.

## Completion criteria
- Every delegated result is verified, blocked, or canceled; no worker continues after a stop order.
