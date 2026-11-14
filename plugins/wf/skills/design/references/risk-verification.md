# Risk verification

Record every material risk in the Wayfinder root issue's **Not yet specified** fog, matching stable IDs before adding entries. Name trigger, failure and impact; do not invent unrelated hypothetical risks. Standalone HLD returns unresolved discovery to its caller without creating a map. Preserve HLD Open Questions as user presentation content; no agent risks there.

## Select the strategy

Choose the cheapest sufficient evidence for the actual failure boundary; record why it is sufficient. Reuse verified evidence only for matching claim, revision, dependencies and environment. Do not run both skills by default.

| Risk uncertainty | Action |
| --- | --- |
| One falsifiable behavior or mitigation claim | *Load and follow the `prove` skill to confirm or refute one technical claim with reproducible evidence*. Supply claim, deciding criteria, revision/environment, prior evidence, assigned checkout, limits and exact output path/base. Let Prove select its smallest adequate method; integrations retain its Testing Integrations selection. |
| Design blind spots, interacting assumptions, or ways a mitigation could fail | *Load and follow the `challenge-this` skill to adversarially test a design and report reproducible counterexamples*. Supply scoped design/mitigation, intent, pinned target/baseline, runnable boundary, prior evidence, limits, exact output path/base and retention/cleanup ownership. Use its default adversary count unless distinct risk surfaces justify more. |
| Missing facts needed to frame a runnable claim | Gather existing source evidence through the owner's Research routing first; label source-based/inferred conclusions, not observed proof. |
| No safe runnable target, access, prerequisite or human decision | Keep risk unresolved; state the exact blocker and next check/decision owner. Continue independent risks. |

Read the selected skill body, applicable procedure and required resources fully before execution; let it own method selection, worker dispatch and independent reproduction. Run it in the caller's session; do not wrap it in a subagent. Prefer existing tests/commands over new probes; a faster mock or simulation is sufficient only if it exercises the risk's actual mechanism. Reuse unchanged evidence rather than repeating runs.

## Execute and reconcile

1. Frame risk and mitigation separately: risk failure condition, proposed mitigation, deciding observation and limits. Use the selection table. Wayfinder uses Experiment for Prove; Challenge this is supporting verification on the current issue or a root-owned run, including whole-HLD scope, never its own ticket. Record `verificationMethod=prove|challenge-this` on that owner; standalone HLD performs this bounded verification before final synthesis. Done when each material risk has a selected method or precise blocker.
2. Retain reports/logs/patches at exact caller-owned destinations. Wayfinder uses `docs/prototype/<initiative-slug>/<risk-slug>/` with caller-owned lifecycle: Prove prototypes use an owned result worktree and Prototype approval; Challenge this uses an owned result worktree for code changes or tests, then integrates evidence automatically without approval; standalone HLD supplies the same report convention and an owned isolated checkout with cleanup handoff. Use revision/attempt-specific report names when another run could overwrite earlier risk/mitigation evidence. Keep report and rerun prerequisites through all verification consumers; standalone HLD preserves final artifacts outside disposable checkouts before cleanup. Done when independent reproduction is recorded or explicitly blocked.
3. For Wayfinder, update HLD conclusions after verified integration: Challenge this is automatic without approval, while Prove prototypes require Prototype approval. Pending approval-gated findings remain in root fog/progress. Use eligible reproduced findings to propose/adjust the mitigation in the HLD; evidence skills do not implement fixes. A demonstrated failure confirms the risk, not its mitigation. Where a candidate mitigation is executable, verify it separately against the original failure case and state both target identities. Newly changed assumptions invalidate only affected evidence. Production implementation, human trade-off acceptance and existing diagram approval gates retain their authorization rules. Done when the mitigation's supported scope and unverified parts are explicit.
4. Record the outcome on the owning issue/root using Outcome rendering below; update supported HLD design conclusions after verified integration for Wayfinder, automatically for Challenge this and after approval for Prove prototypes. Index retained local evidence on root/child issues, not an HLD appendix. Retain a fog entry for reproduced-but-unmitigated, partial, blocked or conflicting results. `No verified findings` or a passing scoped check never proves universal safety. Record user acceptance of residual risk only when explicitly given. Done when every risk has a supported outcome or precise reason unproved.

## Outcome rendering

Keep the root entry compact; detailed commands, output and reproduction live in the linked local report. Every risk outcome states:

- **Outcome:** risk reproduced, mitigation verified for stated conditions, not reproduced within tested coverage, or inconclusive; preserve existing Pending/Partial/Conflict prefixes where unresolved.
- **Mitigation:** proposed measure and verified versus unverified parts; human acceptance when explicitly recorded.
- **Method:** Prove or Challenge this and the actual test/command/probe, why selected, target revision/environment, expected versus observed result, independent rerun outcome and local report evidence link. Reused evidence says reused; source-based/inferred evidence never claims a run.
- **Residual/blocker:** remaining risk/coverage, or exact reason unproved and next check/decision owner. A planned check is not completed proof.

Example shape: `Partial — Mitigation: per-object lock; Method: Prove, existing concurrency test (real lock boundary), revision/environment, expected/observed outcome, independent rerun; Evidence: local report; Residual: restart behavior unproved because restart harness unavailable; next: run recovery check when available.` Replace framing with actual evidence, never copy fictional results.
