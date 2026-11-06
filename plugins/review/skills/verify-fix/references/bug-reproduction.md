# Bug reproduction

## Contents

- Redact
- Phase 1: Build a feedback loop
- Ways to construct one, in roughly this order
- Tighten the loop
- Non-deterministic bugs
- When you genuinely cannot build a loop
- Completion criterion: a tight loop that goes red
- Phase 2: Reproduce + minimise
- Minimise
- Phase 5: Regression test
- Phase 6: Cleanup

Use the existing bug report and fix as context; do not restart hypothesis generation or instrument production code. All probes obey Constraints. Record unavailable original-defect evidence rather than inventing it.

## Redact

This skill has you show commands, outputs and captured artifacts. **Redact every secret first**: write `<REDACTED>` in its place. Build loops against env vars, so the credential stays in the environment rather than in what you show. Captured artifacts carry auth headers: quote only the lines that carry the signal.

If the redacted output is not enough to verify the bug fix, say so and ask the user.

## Phase 1: Build a feedback loop

**This is the skill.** Everything else is mechanical. If you have a **tight** pass/fail signal for the bug (one that goes red on _this_ bug), you can verify the fix; pre-fix and post-fix comparisons consume it. If you don't have one, no amount of staring at code will save you.

Spend disproportionate effort here. **Be aggressive. Be creative. Refuse to give up.**

### Ways to construct one, in roughly this order

1. **Failing test** at whatever seam reaches the bug: unit, integration, e2e.
2. **Curl / HTTP script** against a running dev server.
3. **CLI invocation** with a fixture input, diffing stdout against a known-good snapshot.
4. **Headless browser script** (Playwright / Puppeteer) that drives the UI and asserts on DOM/console/network.
5. **Replay a captured trace.** Save a real network request / payload / event log to disk; replay it through the code path in isolation.
6. **Throwaway harness.** Spin up a minimal subset of the system (one service, mocked deps) that exercises the bug code path with a single function call.
7. **Property / fuzz loop.** If the bug is "sometimes wrong output", run 1000 random inputs and look for the failure mode.
8. **Bisection harness.** If the bug appeared between two known states (commit, dataset, version), automate "boot at state X, check, repeat" so you can `git bisect run` it.
9. **Differential loop.** Run the same input through old-version vs new-version (or two configs) and diff outputs.
10. **HITL bash script.** Last resort. If a human must click, give _them_ exact actions, expected symptom, and a repeatable command that captures the outcome so the loop is still structured. Captured output feeds back to you.

Build the right feedback loop before claiming the fix is verified.

### Tighten the loop

Treat the loop as a product. Once you have _a_ loop, **tighten** it:

- Can I make it faster? (Cache setup, skip unrelated init, narrow the test scope.)
- Can I make the signal sharper? (Assert on the specific symptom, not "didn't crash".)
- Can I make it more deterministic? (Pin time, seed RNG, isolate filesystem, freeze network.)

A 30-second flaky loop is barely better than no loop; a 2-second deterministic one is tight, a debugging superpower.

### Non-deterministic bugs

The goal is not a clean repro but a **higher reproduction rate**. Loop the trigger 100×, parallelise, add stress, narrow timing windows, inject sleeps. A 50%-flake bug is debuggable; 1% is not, so keep raising the rate until it's debuggable.

### When you genuinely cannot build a loop

Stop and say so explicitly. List what you tried. Ask the user for: (a) access to whatever environment reproduces it, (b) a redacted captured artifact (HAR file, log dump, core dump, screen recording with timestamps), or (c) an existing safe reproduction environment. Do **not** claim verification without a loop. Continue independent review and report essential missing evidence as INCONCLUSIVE; do not add production instrumentation.

### Completion criterion: a tight loop that goes red

Phase 1 is done when the loop is **tight** and **red-capable**: you can name **one command** (a script path, a test invocation, a curl) that you have **already run at least once** (show the invocation and its output, redacted), and that is:

- [ ] **Red-capable**: it drives the actual bug code path and asserts the **user's exact symptom**, so it can go red on this bug and green once fixed. Not "runs without erroring"; it must be able to _catch this specific bug_.
- [ ] **Deterministic**: same verdict every run (flaky bugs: a pinned, high reproduction rate, per above).
- [ ] **Fast**: seconds, not minutes.
- [ ] **Agent-runnable**: you can run it unattended; a human in the loop only via the structured actions and captured outcome above.

No red-capable command, no claimed reproduction. Reviewing the existing fix may continue independently, but it cannot replace executable defect evidence.

## Phase 2: Reproduce + minimise

Run the loop against an isolated pre-fix checkout when practical. Watch it go red as the bug appears. Never reset or clean the user's checkout. If the baseline cannot run, record that limitation; do not fabricate a red result.

Confirm:

- [ ] The loop produces the failure mode the **user** described, not a different failure that happens to be nearby. Wrong bug = wrong fix.
- [ ] The failure is reproducible across multiple runs (or, for non-deterministic bugs, reproducible at a high enough rate to debug against).
- [ ] You have captured the exact symptom (error message, wrong output, slow timing) so later phases can verify the fix actually addresses it.

### Minimise

Once it's red, shrink the repro to the **smallest scenario that still goes red**. Cut inputs, callers, config, data, and steps **one at a time**, re-running the loop after each cut, and keep only what's load-bearing for the failure.

Why bother: a minimal repro becomes the clean regression test in Phase 5.

Done when **every remaining element is load-bearing**: removing any one of them makes the loop go green.

Do not claim reproduction until you have reproduced **and** minimised. If blocked, continue independent checks and retain the missing evidence in the verdict.

## Phase 5: Regression test

Run this phase only in `full`, or when the user explicitly requests test changes.

The fix already exists. Write the regression test against the pre-fix baseline when practical, but only if there is a **correct seam** for it.

A correct seam is one where the test exercises the **real bug pattern** as it occurs at the call site. If the only available seam is too shallow (single-caller test when the bug needs multiple callers, unit test that can't replicate the chain that triggered the bug), a regression test there gives false confidence.

**If no correct seam exists, that itself is the finding.** Note it. The codebase architecture is preventing the bug from being locked down. Flag this for the next phase.

If a correct seam exists:

1. Turn the minimised repro into a failing test at that seam.
2. Watch it fail. If you forced the red by mutating a disposable fixture, `diff` against a pristine copy to prove the mutation landed before you trust it. Do not mutate production code; a synthetic failure is not proof the original bug reproduced.
3. Run the same test against the existing fixed code. Do not edit production code or apply/revert the fix in the user's checkout.
4. Watch it pass.
5. Re-run the Phase 1 feedback loop against the original (un-minimised) scenario.

## Phase 6: Cleanup

Required before declaring done:

Remove only run-owned temporary `[DEBUG-...]` instrumentation in disposable harnesses (grep the prefix) and throwaway prototypes (or move prototypes to a clearly-marked debug location). Preserve pre-existing diagnostics and unrelated changes. Remove only run-owned temporary worktrees; record any cleanup failure.

For full verification, also verify:

- [ ] Original repro no longer reproduces (re-run the Phase 1 loop)
- [ ] Regression test passes (or absence of seam is documented)
- [ ] The evidenced root cause and fix mechanism are stated in the verification report, so the next debugger learns
