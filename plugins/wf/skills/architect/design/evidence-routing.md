# Evidence routing

Resolve technical questions during Ground and before each Review round, including greenfield. Use existing procedures; **MUST NOT** duplicate their internals, even if simpler. Gather evidence separately from design acceptance.

## Route

Take the first applicable route per question; reevaluate after each result.

| Condition | Action |
|---|---|
| Reliable evidence answers it for the same sketch revision and environment/version | Reuse; record the answer |
| Needs facts from the codebase, installed NuGet packages, cloud/API, or web documentation | Research |
| Needs observed behavior, including a CLI/API command | Experiment |
| Material falsifiable design claim has a safe runnable target | Interrogate |
| Needs user intent, policy, tradeoff, or unavailable authority | Preserve for review or report blocker |

After resolving questions, screen the synthesized sketch for falsifiable claims affecting correctness, security, reliability, compatibility, or expensive-to-reverse boundaries. Automatically Interrogate each uncovered material claim with a safe runnable target. Derive intent, scope, claim, and target from sketch/user brief. No safe target → record limitation; ask only for necessary permission or business choice.

## Research

*Run `research` skill to investigate primary sources (codebase, NuGet packages, cloud docs, web) via discovered specialists or subagents.* Research routes codebase and NuGet parts through `explore-codebase`, which resolves targets and runs `inspect-nuget-source` for package types; **MUST NOT** invoke either directly. Pass:

- `@question`: one sharp question, decision/current sketch, repo constraints, version, and architecture-changing fact needed. Package claim → name the type or member and the claim to confirm.
- `@outputShape`: Markdown; one result per topic/source part; location `<repo-root>/tmp/architect-<slug>/research/`; require answer, architectural implications, primary-source citations, version/applicability constraints, unknowns/blockers, and artifact path.

Pass `@outputShape` verbatim; Research propagates it to every specialist and owns discovery, classification, and fan-out. **MUST NOT** dispatch separate research agents. Honor stronger specialist artifact-location contracts; index returned paths in the artifact root.

Read final artifacts; check cited conclusions and applicable versions. Add findings to grounding/rationale before Arena or review; route empirical unknowns to Experiment.

## Experiment

*Run `experiment` skill to test one uncertain technical question by observing actual behavior.* Pass question, falsifiable assumption, observable success/refutation criteria, repo/current sketch/prior evidence, runtime/environment constraints, safety limits, and out-of-scope behavior.

Experiment selects the smallest method: CLI/API command, existing test, script, simulation, process set, throwaway app, or existing UI route. **MUST NOT** require an app or code patch for a CLI-only result. Keep code isolated in disposable worktrees and state local or in authorized sandboxes; **MUST NOT** use destructive production targets or expand credentials/permissions.

Require a report with question, method, exact reproducible command, actual output, conclusion (`confirmed`, `refuted`, or `inconclusive`), evidence paths, architectural implication, and cleanup. Require a patch only when code was created.

Use loaded Prototype for builder isolation, rerun, and cleanup; automatic runs skip its Prove step. Material claims still route to Interrogate below; reuse Prove coverage for the same scope/revision when it ran.

## Interrogate

Run loaded Interrogate with intent, scope, material claim, runnable target, and prior reproductions. Reviewers use Experiment for probes; coordinator independently reruns findings. Reuse valid reproductions. No verified findings is valid.

## Outcomes and reuse

Record question/claim, sketch revision, environment/version, evidence paths, outcome, and Interrogate coverage in the artifact root's `review-log.md`, including artifacts saved elsewhere.

| Outcome | Action |
|---|---|
| Confirmed and compatible | Close factual question; cite evidence in rationale |
| Refuted or verified finding | Present proposed correction; apply only after user acceptance |
| Inconclusive | Preserve unknown, missing evidence, and impact |
| Tool, permission, or sandbox unavailable | Record blocker; invent no result |
| Material change | Recheck only invalidated assumptions |
| Unchanged question, dependencies, and sketch | Reuse evidence and prior Interrogate coverage |

Retry once per question/revision only when new evidence or setup addresses the failure; otherwise record blocker/unknown. **MUST NOT** automatically apply Experiment or Interrogate proposals; only **implement** permits production code.

Return control to the orchestrator for **Phase B: Sketch** after Ground, or **Phase C: Review loop** before presenting a round.
