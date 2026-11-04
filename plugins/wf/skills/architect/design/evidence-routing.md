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
| Needs user intent, policy, tradeoff, or unavailable authority | Recommend and document a reversible choice; ask only when authority is required or a checkpoint was requested |

After resolving questions, screen the synthesized sketch for falsifiable claims affecting correctness, security, reliability, compatibility, or expensive-to-reverse boundaries. Automatically Interrogate each uncovered material claim with a safe runnable target. Derive intent, scope, claim, and target from sketch/user brief. No safe target → record limitation; ask only for necessary permission or business choice.

## Research

*Run `research` skill to investigate primary sources (codebase, NuGet packages, cloud docs, web) via discovered specialists or subagents.* Research routes codebase and NuGet parts through `explore-codebase`, which resolves targets and runs `inspect-nuget-source` for package types; **MUST NOT** invoke either directly. Pass:

- `@question`: one sharp question, decision/current sketch, repo constraints, version, and architecture-changing fact needed. Package claim → name the type or member and the claim to confirm.
- `@outputShape`: Markdown; one result per topic/source part; location `<repo-root>/tmp/architect-<slug>/research/`; require answer, architectural implications, primary-source citations, version/applicability constraints, unknowns/blockers, and artifact path.

Pass `@outputShape` verbatim; Research propagates it to every specialist and owns discovery, classification, and fan-out. **MUST NOT** dispatch separate research agents. Honor stronger specialist artifact-location contracts; index returned paths in the artifact root.

Read final artifacts; check cited conclusions and applicable versions. Add findings to grounding/rationale before Arena or review; route empirical unknowns to Experiment.

## Experiment

Read `experiment` skill's Inputs and Workflow first, then *run `experiment` skill to test one uncertain technical question by observing actual behavior*, filling: `@question`; `@criteria` = falsifiable assumption plus observable success/refutation criteria; `@repoFacts` = repo, current sketch, grounding and Research artifact paths, prior evidence; `@limits` = runtime/environment constraints, safety limits, out-of-scope behavior, disposable worktree.

Experiment's Workflow selects the method and artifact; **MUST NOT** prescribe one, and **MUST NOT** require an app or code patch for a CLI-only result. Keep code isolated in disposable worktrees and state local or in authorized sandboxes; **MUST NOT** use destructive production targets or expand credentials/permissions.

Require a report with question, method, exact reproducible command, actual output, conclusion (`confirmed`, `refuted`, or `inconclusive`), evidence paths, architectural implication, and cleanup. Require a patch only when code was created.

Use loaded Prove for prover isolation, rerun, and cleanup; automatic runs skip its Attack step. Material claims still route to Interrogate below; reuse Attack coverage for the same scope/revision when it ran.

## Interrogate

Run loaded Interrogate with intent, scope, material claim, runnable target, and prior reproductions. Reviewers use Experiment for probes; coordinator independently reruns findings. Reuse valid reproductions. No verified findings is valid.

## Outcomes and reuse

Record question/claim, sketch revision, environment/version, evidence paths, outcome, and Interrogate coverage in the artifact root's `review-log.md`, including artifacts saved elsewhere.

| Outcome | Action |
|---|---|
| Confirmed and compatible | Close factual question; cite evidence in rationale |
| Refuted or verified finding | Without checkpoint: apply supported correction and log rationale; with checkpoint: present proposed correction for acceptance |
| Verified Interrogate finding on a contract (interface, invariant, ordering, error mode, configuration, seam, adapter) | Derive the correction through Deep-module design in `SKILL.md`, then act as for a verified finding |
| Inconclusive | Preserve unknown, missing evidence, and impact |
| Tool, permission, or sandbox unavailable | Record blocker; invent no result |
| Material change | Recheck only invalidated assumptions |
| Unchanged question, dependencies, and sketch | Reuse evidence and prior Interrogate coverage |

Retry once per question/revision only when new evidence or setup addresses the failure; otherwise record blocker/unknown. Without checkpoint, apply evidence-backed Experiment or Interrogate corrections to the sketch; with checkpoint, require approval for proposed corrections. Neither path permits production code before Phase E.

Return control to the orchestrator for **Phase B: Sketch** after Ground, or **Phase C: Review** before continuing.
