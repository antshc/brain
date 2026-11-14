# Prove direct execution plan

## Goal

Merge Prove and Execute into one direct workflow. Prove spawns no subagents and calls Research directly, never Hunter. Workflow callers own proof-worker dispatch and independent reproduction.

Planning only; no repository implementation, commits or PR.

## Baseline

Inspected `antshc/brain` main at `5103a670feca6e66c5e608b23401ed3c7c99c201`.

- Prove currently dispatches one general-purpose prover, requests isolation, collects its Execute report, independently reruns and cleans up.
- Challenge this adversaries and Blast Radius workers already call Execute inside assigned workers.
- Design evidence routing assigns dispatch/isolation/rerun/cleanup to Prove.
- Wayfinder explicitly forbids wrapping helpers and labels Prove workers Prove-owned. That rule must change for Prove.
- Research on this revision still dispatches Hunter. Removing only Prove's explicit Hunter call would leave indirect worker spawning. The direct Research refactor must land first or accompany this change.

Sources: [Prove](https://github.com/antshc/brain/blob/main/plugins/wf/skills/prove/SKILL.md), [Design evidence routing](https://github.com/antshc/brain/blob/main/plugins/wf/skills/design/references/evidence-routing.md), [Wayfinder](https://github.com/antshc/brain/blob/main/plugins/wf/skills/design/playbooks/wayfinder.md), [Research](https://github.com/antshc/brain/blob/main/plugins/wf/skills/research/SKILL.md).

## Ownership

| Concern | Prove skill | Caller |
| --- | --- | --- |
| Claim framing | Fill gaps; define falsifiable criteria | Supply question, intent and known criteria |
| Execution | Run full proof workflow in current session | Invoke directly or dispatch a skill-capable general-purpose worker with prover role |
| Research | Invoke Research directly; pass checkout, question, facts, limits and output contract | No Hunter needed for Prove's discovery |
| Method | Select smallest adequate method; integrations use Testing Integrations | Supply existing suites/facts, not a duplicated method-selection procedure |
| Isolation | Reuse verified assigned checkout; create owned worktree through Git when isolation is required and none supplied | Delegated callers request one verified worktree and pass ownership; avoid duplicate worktrees |
| Reproduction | Capture exact rerun command; record own repeat checks accurately | Delegated coordinator independently reruns before accepting observed conclusions |
| Cleanup | Remove only self-owned resources after all consumers; hand off retained state explicitly | Own worker-supplied worktrees, reruns, reviews and final cleanup |
| Integration | Return evidence and proof patch | Own approval, local commits/merges and implementation decisions |

No new public action, compatibility alias, custom agent or dispatch framework. Existing general-purpose prover role suffices.

## Unified workflow

1. **Frame.** Question, intent, assumption, expected behavior, deciding observations, exclusions. Preserve Principles loading.
2. **Reuse or research.** Reuse matching revision/environment evidence. Invoke Research directly for missing facts or questions settled by reading; preserve observed/source-based/inferred labels. Stop when adequate evidence settles the question.
3. **Prepare environment.** Verify supplied checkout, target/dirty inputs, writable scope and cleanup owner. Reuse caller isolation. Create an owned worktree through Git only when required and absent; unavailable isolation blocks dependent work.
4. **Choose.** Load applicable logic/runtime/integration/UI tactics. Preserve mandatory Testing Integrations Select and Run selected, suite reuse and real-boundary requirements.
5. **Run.** Execute the smallest sufficient existing command or probe. Reuse tactic-captured execution; no duplicate initial execution. Record assertions, actual output, executed tests/counts, environment and patch identity.
6. **Verify and return.** Check deciding observations against criteria. Capture exact rerun command and prerequisites. A repeat by the same executor is rerun verification, not independent reproduction. Missing assertion, zero collected tests, wrong target or missing output cannot confirm a claim.
7. **Finalize.** Confirmed/refuted/inconclusive; evidence, limitations and retention/cleanup status. Preserve runnable state through caller reruns, review and existing approval gates.

Delete the Actions table, Execute public entry point, Prove-only branches, internal dispatch and unconditional coordinator-rerun language. Merge both sets of framing/execution principles without duplicating their loads.

## Caller dispatch contract

For callers previously relying on Prove's internal worker:

1. Load Subagents; use Dispatch with one skill-capable general-purpose worker, prover role, explicit proof scope and isolated outputs.
2. Supply an instruction to load and follow the Prove skill to confirm or refute one technical claim with reproducible evidence. Pass all facts, limits, exact destinations, pinned target, assigned checkout and cleanup/retention owner unchanged. No action selector.
3. Collect report/blocker. Independently rerun its exact command against recorded target/patch when accepting observed proof; record actual result. Source-based/reused conclusions carry provenance instead of an invented new run.
4. Sequence any requested Challenge this review outside Prove. Retain environment until every consumer finishes, then perform owned cleanup.
5. Unavailable required worker/isolation/rerun becomes an explicit blocker or pending verification, never a silently verified result.

Already inside an assigned adversary or Blast Radius worker: call Prove directly with the same environment and ownership. Existing outer coordinator remains responsible for reproduction and cleanup. Do not add another worker layer.

Use existing caller resources/sections to share this contract within each skill. Do not access another skill's private resources or duplicate Prove's method internals.

## Affected-file checklist

Paths relative to repository root. During implementation, rescan live callers excluding `_backup/` and `_in-progress/`; reconcile additional matches before declaring complete.

### Prove

- [ ] `plugins/wf/skills/prove/SKILL.md`: unified direct workflow; no Subagents/Hunter dispatch, action selector or worker-required path; direct Research invocation; accurate verification/ownership contract.
- [ ] `plugins/wf/skills/prove/README.md`: direct and caller-delegated examples; same skill behavior in either session.
- [ ] `plugins/wf/skills/prove/tactics/integration.md`: return to unified workflow; remove Execute/default-coordinator dependencies; preserve selection and captured-run reuse.
- [ ] `plugins/wf/skills/prove/tactics/runtime.md`: retention tied to declared consumers/owner.
- [ ] `plugins/wf/skills/prove/tactics/ui.md`: same retention wording.
- [ ] `plugins/wf/skills/prove/tactics/logic.md`: verify no stale action assumptions; change only if needed.

### Design callers

- [ ] `plugins/wf/skills/design/references/evidence-routing.md`: Design dispatches prover, supplies/reuses isolation, reruns, sequences review and cleans up; Prove owns method/execution only.
- [ ] `plugins/wf/skills/design/playbooks/architect.md`: automatic and interactive Prove requests use that caller-owned contract; retain checkpoint and follow-up review behavior.
- [ ] `plugins/wf/skills/design/playbooks/wayfinder.md`: replace Prove-owned worker row and no-wrapper rule for Prove with explicit Wayfinder-owned dispatch. Reuse owned result worktree; retain sequential helpers, payload approval, local integration and cleanup gates.
- [ ] `plugins/wf/skills/design/references/risk-verification.md`: distinguish caller-owned Prove dispatch from Challenge-this-owned adversaries; independent rerun belongs to coordinator. Supporting Prove inside adversaries remains direct.
- [ ] `plugins/wf/skills/design/README.md`: update helper responsibilities, diagrams and no-wrapper/default-dispatch claims.
- [ ] `plugins/wf/skills/design/SKILL.md`: check router/resource guidance; update only affected ownership references.
- [ ] `plugins/wf/README.md`: update Prove dispatch summary.

### Existing worker callers

- [ ] `plugins/wf/skills/challenge-this/references/adversary-prompt.md`: remove Execute/default-Prove orchestration references; invoke unified Prove directly; preserve outer coordinator ownership.
- [ ] `plugins/wf/skills/review/references/blast-radius-worker-prompt.md`: remove Execute selector; invoke unified Prove directly.
- [ ] `plugins/wf/skills/review/playbooks/blast-radius.md`: remove Prove Execute terminology; retain existing claim-group dispatch and evidence aggregation.

### Other workflow callers

- [ ] `plugins/wf/skills/define/references/research.md`: caller dispatches accepted frontier experiments; preserve per-topic reports, user acceptance and retention.
- [ ] `plugins/wf/install/assets/factory-mode/SKILL.md`: concise caller-owned proof-dispatch contract for uncertainty handling.
- [ ] `plugins/wf/install/assets/factory-mode/playbooks/feature.md`: route proof requests through Factory's contract.
- [ ] `plugins/wf/install/assets/factory-mode/playbooks/prototype.md`: same contract; pass disposable environment and preserve throwaway scope.
- [ ] `plugins/wf/install/assets/factory-mode/playbooks/investigation.md`: same contract; preserve read-only production checkout and disposable proof work.
- [ ] `plugins/wf/skills/principles/SKILL.md`, `plugins/wf/skills/diagnosing-bugs/SKILL.md`, root `README.md`: check redirects/catalog descriptions; no change for mentions unrelated to orchestration.
- [ ] `plugins/wf/skills/subagents/SKILL.md`: verify existing Dispatch/prover-role contract supports callers; change only if a concrete gap exists.

### Research dependency

- [ ] Rebase on/coordinate the direct Research change. Prove uses its current direct routing contract, not old Explore-to-Hunter forwarding.
- [ ] If Research is still dispatching, remove that dependency through the separately scoped direct Research refactor before accepting zero-spawn behavior. Do not invent an unsupported inline flag or silently copy Research internals.
- [ ] Do not remove Hunter globally or change unrelated Research callers in this Prove refactor.

## Implementation order

1. Confirm current main and direct Research availability; refresh caller inventory.
2. Rewrite Prove and tactics.
3. Update assigned-worker callers first; they require no new dispatch.
4. Move orchestration to Design, Define and Factory callers; reconcile Wayfinder's exception consistently.
5. Update documentation and existing contract tests.
6. Run focused checks, repository lint/consistency checks and final caller sweep.

## Verification

Update existing tests to verify ownership/behavior, not one exact sentence.

- `tests/wf/prove/test_evidence_contracts.py`: replace obsolete Execute assertion; verify one workflow, no Prove dispatch/Hunter call, direct Research, valid local resources, Testing Integrations one-way selection/execution and truthful result states.
- `tests/wf/design/test_routing.py`: replace blanket no-wrapper assertion with Prove-specific caller-owned dispatch; retain other helper policies and approval gates.
- Review `tests/wf/design/test_architect.py`, `tests/wf/research/test_contracts.py`, `tests/wf/research/test_explore_contracts.py` and `tests/wf/subagents/test_contracts.py` for affected contracts. Preserve unrelated Research/Subagents expectations; align direct Research tests with its own refactor.
- Run affected pytest suites using repository-configured runner; inspect `.github/workflows/test.yml` and `.github/scripts/run-python-tests.py` for exact commands. Run skill-description lint and existing skill-invocation consistency checks.

Scenario checks:

| Scenario | Expected |
| --- | --- |
| Direct /prove with existing test | Current agent executes; zero worker launches |
| Missing symbol/caller facts | Research executes directly; no Hunter handoff |
| Reading or valid prior evidence settles claim | Cited/reused conclusion; no invented empirical run |
| Design/Wayfinder requests empirical proof | Caller dispatches one prover; worker runs unified skill; caller independently reruns |
| Challenge this or Blast Radius worker needs proof | Direct invocation in assigned checkout; no nested proof worker |
| Caller supplies verified worktree | Reused; no duplicate isolation or premature cleanup |
| Direct writable proof without isolation | Skill creates only necessary owned worktree through Git |
| Integration/UI evidence | Existing method selection, safety and retention rules preserved |
| Missing worker/isolation/access or zero tests | Explicit blocker/inconclusive; no false confirmation |
| Pending Wayfinder prototype approval or follow-up review | Same runnable state retained; no early merge/removal |

Final completeness sweep: every live Prove invocation classified as direct executor or caller-owned dispatch; no public Execute selector, Prove-owned worker statement, internal Hunter handoff or false independent-verification claim remains. Historical plans and unrelated uses of the word Execute are not migration targets.

## Risks and constraints

- Hidden delegation through old Research breaks zero-spawn behavior: resolve the direct Research dependency explicitly.
- Existing no-wrapper rules conflict with relocated dispatch: update Wayfinder and risk-verification docs/tests together.
- Caller/skill both create or clean worktrees: use one verified checkout and explicit ownership; never remove caller-owned resources.
- Moving orchestration can weaken verification: preserve caller independent reruns for delegated proof; label direct checks accurately.
- Preserve output destinations, proof patches, safety limits, user approval gates and caller-owned commits/integration. No new approval gates.
