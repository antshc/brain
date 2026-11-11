# Blast-radius final report

Coordinator: fill from verified worker evidence after aggregation and the completeness sweep. Return one report; remove guidance and placeholders. Link shared evidence by claim ID while preserving each verdict. Do not silently resolve conflicting results or upgrade worker claims without evidence.

## What changed

{Scope, baseline/head or local-state identity, affected observable behavior, and non-obvious consequences. State whether the reviewed revision is still current.}

## Central safety fact

{State the deciding claim, its claim ID, verdict, ladder level, and proof. Without executable proof, mark unproven with reason and next check.}

## Risks and cleared claims

| ID / claim | Failure mechanism, location, likelihood / impact | Verdict | Ladder level | Proof method and evidence | Unproven reason / next step |
| --- | --- | --- | --- | --- | --- |
| {ID and claim} | {Mechanism and file:line} | {confirmed / cleared / unresolved} | {1–5} | {Source trace or execution evidence link} | {Reason and next check, or none} |

Include confirmed defects, cleared risks, and unresolved claims. For each execution, inline or link its exact command, environment, executed tests and counts or runtime observation, result, target/patch identity, and artifacts. Preserve baseline comparisons and worker provenance; distinguish an existing defect from a demonstrated regression.

## Completeness

- **Coverage:** {complete / incomplete; behavior-to-claim mapping, omitted/inaccessible scope, and consequences}
- **Risk verification:** {risks resolved / unresolved; conflicts, missing worker results, and blockers}

Coverage complete does not mean safe. Confirmed defects remain explicit even when all verdicts are settled; unproven claims retain their limits and next checks.

## Before merge

{Cheapest remaining tests/reproductions, confirmed defects requiring action, reusable regression patches, retained evidence, and worktree/resource cleanup outcomes.}
