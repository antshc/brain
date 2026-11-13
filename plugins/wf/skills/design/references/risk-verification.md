# Risk verification

Record every material design risk in Open Questions, retaining Question/Answer columns. Match existing rows before adding one. Question starts `Risk —` and names the trigger, failure and impact; do not invent unrelated hypothetical risks. Keep resolved risks for continuity; no separate Risks section.

## Select the strategy

Choose the cheapest sufficient evidence for the actual failure boundary; record why it is sufficient. Reuse verified evidence only for matching claim, revision, dependencies and environment. Do not run both skills by default.

| Risk uncertainty | Action |
| --- | --- |
| One falsifiable behavior or mitigation claim | *Load and follow the `prove` skill to confirm or refute one technical claim with reproducible evidence*. Supply claim, deciding criteria, revision/environment, prior evidence, assigned checkout, limits and exact output path/base. Let Prove select its smallest adequate method; integrations retain its Testing Integrations selection. |
| Design blind spots, interacting assumptions, or ways a mitigation could fail | *Load and follow the `challenge-this` skill to adversarially test a design and report reproducible counterexamples*. Supply scoped design/mitigation, intent, pinned target/baseline, runnable boundary, prior evidence, limits, exact output path/base and retention/cleanup ownership. Use its default adversary count unless distinct risk surfaces justify more. |
| Missing facts needed to frame a runnable claim | Gather existing source evidence through the owner's Research routing first; label source-based/inferred conclusions, not observed proof. |
| No safe runnable target, access, prerequisite or human decision | Keep risk unresolved; state the exact blocker and next check/decision owner. Continue independent risks. |

Read the selected skill body, applicable procedure and required resources fully before execution; let it own method selection, delegation and independent reproduction. Prefer existing tests/commands over new probes; a faster mock or simulation is sufficient only if it exercises the risk's actual mechanism. Reuse unchanged evidence rather than repeating runs.

## Execute and reconcile

1. Frame risk and mitigation separately: risk failure condition, proposed mitigation, deciding observation and limits. Use the selection table. Wayfinder dispatches through its existing Experiment ticket/worktree queue with `verificationMethod=prove|challenge-this`; standalone HLD performs this bounded verification before final synthesis. Done when each material risk has a selected method or precise blocker.
2. Retain reports/logs/patches at exact caller-owned destinations. Wayfinder uses `docs/prototype/<initiative-slug>/<risk-slug>/` and its existing local commit/merge/synchronize lifecycle; standalone HLD supplies the same report convention and an owned isolated checkout with cleanup handoff. Use revision/attempt-specific report names when another run could overwrite earlier risk/mitigation evidence. Keep report and rerun prerequisites through all verification consumers; standalone HLD preserves final artifacts outside disposable checkouts before cleanup. Done when independent reproduction is recorded or explicitly blocked.
3. Use reproduced findings to propose/adjust the mitigation in the HLD; evidence skills do not implement fixes. A demonstrated failure confirms the risk, not its mitigation. Where a candidate mitigation is executable, verify it separately against the original failure case and state both target identities. Newly changed assumptions invalidate only affected evidence. Production implementation, human trade-off acceptance and existing diagram approval gates retain their authorization rules. Done when the mitigation's supported scope and unverified parts are explicit.
4. Fill Answer using the rendering contract below, update affected design sections, and index evidence in Appendix B: Prototypes and Code Sketches. Retain an unresolved row for reproduced-but-unmitigated, partial, blocked or conflicting results. `No verified findings` or a passing scoped check never proves universal safety. Record user acceptance of residual risk only when explicitly given. Done when every risk has a supported outcome or precise reason unproved.

## Answer rendering

Keep the cell compact; detailed commands, output and reproduction live in the linked appendix report. Every risk Answer states:

- **Outcome:** risk reproduced, mitigation verified for stated conditions, not reproduced within tested coverage, or inconclusive; preserve existing Pending/Partial/Conflict prefixes where unresolved.
- **Mitigation:** proposed measure and verified versus unverified parts; human acceptance when explicitly recorded.
- **Method:** Prove or Challenge this and the actual test/command/probe, why selected, target revision/environment, expected versus observed result, independent rerun outcome and appendix evidence link. Reused evidence says reused; source-based/inferred evidence never claims a run.
- **Residual/blocker:** remaining risk/coverage, or exact reason unproved and next check/decision owner. A planned check is not completed proof.

Example shape: `Partial — Mitigation: per-object lock; Method: Prove, existing concurrency test (real lock boundary), revision/environment, expected/observed outcome, independent rerun; Evidence: appendix report; Residual: restart behavior unproved because restart harness unavailable; next: run recovery check when available.` Replace framing with actual evidence, never copy fictional results.
