# Evidence routing

Resolve technical questions during Architect Ground and before each Review round, including greenfield. Use existing procedures; **MUST NOT** duplicate their internals, even if simpler. Gather evidence separately from design acceptance.

## Route

Take the first applicable route per question; reevaluate after each result.

| Condition | Action |
|---|---|
| Reliable evidence answers it for the same sketch revision and environment/version | Reuse; record the answer |
| Needs facts from the codebase, installed NuGet packages, cloud/API, or web documentation | Research |
| Needs observed behavior, including a CLI/API command | Prove |
| Material falsifiable design claim has a safe runnable target | Challenge this |
| Needs user intent, policy, tradeoff, or unavailable authority | Recommend and document a reversible choice; ask only when authority is required or a checkpoint was requested |

After resolving questions, screen the synthesized sketch for falsifiable claims affecting correctness, security, reliability, compatibility, or expensive-to-reverse boundaries. Automatically challenge each uncovered material claim with a safe runnable target. Derive intent, scope, claim, and target from sketch/user brief. No safe target → record limitation; ask only for necessary permission or business choice.

## Research

*Run `research` skill to investigate primary sources (codebase, NuGet packages, cloud docs, web) via discovered specialists or subagents.* Research delegates codebase and NuGet evidence to Hunter and owns routing and synthesis for this call. Pass:

- `@question`: one sharp question, decision/current sketch, repo constraints, version, and architecture-changing fact needed. Package claim → name the type or member and the claim to confirm.
- `@outputPath`: exact file `<artifact-root>/research/<question-slug>.md` selected by Design; use distinct slugs for separate calls. For several independent reports, Design supplies a question-to-file mapping before dispatch; never pass only a directory.
- `@outputBase`: absolute repository root.
- `@outputShape`: Markdown; require answer, architectural implications, primary-source citations, version/applicability constraints, unknowns/blockers, and artifact path.

Pass framing verbatim and destinations separately; Research owns discovery, classification, and fan-out and returns worker findings inline. **MUST NOT** dispatch separate research agents. Index the caller-selected report paths in the artifact root; no specialist may override them.

Read final artifacts; check cited conclusions and applicable versions. Add findings to grounding/rationale before Arena or review; route empirical unknowns to Prove.

## Prove

*Run `prove` skill to confirm or refute one technical claim with reproducible evidence*. Pass `@question`, `@criteria` (assumption and confirm/refute observations), `@repoFacts` (launch/harness root, explicit checkout, revision, sketch/grounding/research paths, prior suites/evidence), and `@limits` (runtime/safety, exclusions, writable paths). Design chooses a fresh exact `@outputPath=<artifact-root>/prove/<question-id>-<revision>-<attempt>/report.md`, repository root as `@outputBase`, and distinct worker evidence/patch destinations in that run directory. Request method, observed output, independent rerun, conclusion, limitations and cleanup in `@outputShape`.

Prove owns method selection, integration-test discovery through Testing Integrations, isolation, rerun and cleanup. CLI-only requires no app/patch; require a patch only when code changed. When a following adversarial review needs runnable evidence, pass deferred cleanup and reuse its environment; Design releases owned resources after both runs. Material claims still receive Challenge this coverage below.

## Challenge this

*Run `challenge-this` skill to find problems in a change or design*. Pass intent, scope/material claim, pinned revision, runnable target, prior reproductions, known suites, original launch/harness root, explicit checkout, safety limits, `adversaries` when supplied, exact `@outputPath=<artifact-root>/challenge-this.md` and repository root as `@outputBase`. For per-claim runs, select distinct report/worker destinations before dispatch and aggregate coverage in the review log. Challenge this owns its adversaries and independent reruns; no duplicated procedure or internal resource access.

Design interprets returned findings. Resolve verified contract findings through its Deep module route. No verified findings is valid; blocked coverage remains explicit.

## Outcomes and reuse

Record question/claim, sketch revision, environment/version, evidence paths, outcome, and Challenge this coverage in the artifact root's `review-log.md`, including artifacts saved elsewhere.

| Outcome | Action |
|---|---|
| Confirmed and compatible | Close factual question; cite evidence in rationale |
| Refuted or verified finding | Without checkpoint: apply supported correction and log rationale; with checkpoint: present proposed correction for acceptance |
| Verified Challenge this finding on a contract (interface, invariant, ordering, error mode, configuration, seam, adapter) | Derive the correction through [Deep module](../playbooks/deep-module.md), then act as for a verified finding |
| Inconclusive | Preserve unknown, missing evidence, and impact |
| Tool, permission, or sandbox unavailable | Record blocker; invent no result |
| Material change | Recheck only invalidated assumptions |
| Unchanged question, dependencies, and sketch | Reuse evidence and prior Challenge this coverage |

Retry once per question/revision only when new evidence or setup addresses the failure; otherwise record blocker/unknown. Without checkpoint, apply evidence-backed Prove or Challenge this corrections to the sketch; with checkpoint, require approval for proposed corrections. Neither path permits production code before Phase E.

Return control to the orchestrator for **Phase B: Sketch** after Ground, or **Phase C: Review** before continuing.
