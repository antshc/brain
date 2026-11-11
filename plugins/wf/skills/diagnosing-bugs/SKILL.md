---
name: diagnosing-bugs
description: >-
  Run a diagnosis loop for hard bugs and performance regressions. Use for 'diagnose this', 'debug this', or reports of broken, throwing, failing, or slow behavior; also explicit bug-fix requests. Not for one-off behavior questions → `prove`.
---

# Diagnosing Bugs

A discipline for hard bugs. Skip phases only when explicitly justified.

Diagnose by default. Run Phase 5 only when the user explicitly asks for a fix. In either mode, clean up temporary diagnostic changes in Phase 6.

When exploring the codebase, read `GLOSSARY.md` (if it exists) to get a clear mental model of the relevant modules, and check ADRs in the area you're touching.

## Redact

This skill has you show commands, outputs and captured artifacts. **Redact every secret first**: write `<REDACTED>` in its place. Build loops against env vars, so the credential stays in the environment rather than in what you show. Captured artifacts carry auth headers: quote only the lines that carry the signal.

If the redacted output is not enough to diagnose the bug, say so and ask the user.

## Phase 1: Build a feedback loop

*Run `principles` skill to load only the engineering principles needed here; read its entire `SKILL.md`, then read each selected Index file in full from that skill's own folder.* Select `Build the lever` and `Test behavior, not implementation` for the feedback loop. Re-evaluate at each phase: `Fix root causes` for diagnosis, `Attack the premise` after two fixes sharing a premise fail, `Explain the number` for measurements, `Prove it works` before completion. Existing diagnosis/fix authorization gates still apply.

**This is the skill.** Everything else is mechanical. If you have a **tight** pass/fail signal for the bug (one that goes red on _this_ bug), you will find the cause; bisection, hypothesis-testing, and instrumentation all just consume it. If you don't have one, no amount of staring at code will save you.

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
10. **HITL bash script.** Last resort. If a human must click, drive _them_ with `scripts/hitl-loop.template.sh` so the loop is still structured. Captured output feeds back to you.

Build the right feedback loop, and the bug is 90% fixed.

### Tighten the loop

Treat the loop as a product. Once you have _a_ loop, **tighten** it:

- Can I make it faster? (Cache setup, skip unrelated init, narrow the test scope.)
- Can I make the signal sharper? (Assert on the specific symptom, not "didn't crash".)
- Can I make it more deterministic? (Pin time, seed RNG, isolate filesystem, freeze network.)

A 30-second flaky loop is barely better than no loop; a 2-second deterministic one is tight, a debugging superpower.

### Non-deterministic bugs

The goal is not a clean repro but a **higher reproduction rate**. Loop the trigger 100×, parallelise, add stress, narrow timing windows, inject sleeps. A 50%-flake bug is debuggable; 1% is not, so keep raising the rate until it's debuggable.

### When you genuinely cannot build a loop

Stop and say so explicitly. List what you tried. Ask the user for: (a) access to whatever environment reproduces it, (b) a redacted captured artifact (HAR file, log dump, core dump, screen recording with timestamps), or (c) permission to add temporary production instrumentation. Do **not** proceed to hypothesise without a loop.

### Completion criterion: a tight loop that goes red

Phase 1 is done when the loop is **tight** and **red-capable**: you can name **one command** (a script path, a test invocation, a curl) that you have **already run at least once** (show the invocation and its output, redacted), and that is:

- [ ] **Red-capable**: it drives the actual bug code path and asserts the **user's exact symptom**, so it can go red on this bug and green once fixed. Not "runs without erroring"; it must be able to _catch this specific bug_.
- [ ] **Deterministic**: same verdict every run (flaky bugs: a pinned, high reproduction rate, per above).
- [ ] **Fast**: seconds, not minutes.
- [ ] **Agent-runnable**: you can run it unattended; a human in the loop only via `scripts/hitl-loop.template.sh`.

If you catch yourself reading code to build a theory before this command exists, **stop: jumping straight to a hypothesis is the exact failure this skill prevents.** No red-capable command, no Phase 2.

## Phase 2: Reproduce + minimise

Run the loop. Watch it go red as the bug appears.

Confirm:

- [ ] The loop produces the failure mode the **user** described, not a different failure that happens to be nearby. Wrong bug = wrong fix.
- [ ] The failure is reproducible across multiple runs (or, for non-deterministic bugs, reproducible at a high enough rate to debug against).
- [ ] You have captured the exact symptom (error message, wrong output, slow timing) so later phases can verify the fix actually addresses it.

### Minimise

Once it's red, shrink the repro to the **smallest scenario that still goes red**. Cut inputs, callers, config, data, and steps **one at a time**, re-running the loop after each cut, and keep only what's load-bearing for the failure.

Why bother: a minimal repro shrinks the hypothesis space in Phase 3 (fewer moving parts left to suspect) and becomes the clean regression test in Phase 5.

Done when **every remaining element is load-bearing**: removing any one of them makes the loop go green.

Do not proceed until you have reproduced **and** minimised.

## Phase 3: Hypothesise

Read [Hypothesis log](references/hypothesis-log.md) and open or resume the log. Continue `H` numbering and skip previously falsified hypotheses for the same bug. Number the ranked hypotheses in log sequence.

Generate **3–5 ranked hypotheses** before testing any of them. Single-hypothesis generation anchors on the first plausible idea.

Each hypothesis must be **falsifiable**: state the prediction it makes.

> Format: "If <X> is the cause, then <changing Y> will make the bug disappear / <changing Z> will make it worse."

If you cannot state the prediction, the hypothesis is a vibe: discard or sharpen it.

If the bug appears only after a restart, rank persisted state first: config files, caches, lock files, serialized state.

**Show the ranked list to the user before testing.** They often have domain knowledge that re-ranks instantly ("we just deployed a change to #3"), or know hypotheses they've already ruled out. Cheap checkpoint, big time saver. Don't block on it; proceed with your ranking if the user is AFK.

## Phase 4: Instrument

Each probe must map to a specific prediction from Phase 3. **Change one variable at a time.**

Tool preference:

1. **Debugger / REPL inspection** if the env supports it. One breakpoint beats ten logs.
2. **Targeted logs** at the boundaries that distinguish hypotheses.
3. Never "log everything and grep".

**Tag every debug log** with a unique prefix, e.g. `[DEBUG-a4f2]`. Cleanup at the end becomes a single grep. Untagged logs survive; tagged logs die.

**Perf branch.** For performance regressions, logs are usually wrong. Instead: establish a baseline measurement (timing harness, `performance.now()`, profiler, query plan), then bisect. Measure first, fix second.

After each check, append the result per [Hypothesis log](references/hypothesis-log.md), including checks that end blocked. A cause is confirmed when re-checkable evidence connects it to the reproduced symptom through an ordered mechanism and it fits the observations. The chain MUST end at the **first wrong decision**: keep asking "why" until the answer is code doing something it should not, or failing to handle a state it should handle, not a consequence of an earlier step. A blocked probe does not confirm a cause. If the cause remains unconfirmed, clean up and report the blocker, what was checked, and the log path.

## Phase 5: Fix + regression test

Run this phase only for an explicit fix request with a confirmed cause.

Write the regression test **before the fix**, but only if there is a **correct seam** for it.

A correct seam is one where the test exercises the **real bug pattern** as it occurs at the call site. If the only available seam is too shallow (single-caller test when the bug needs multiple callers, unit test that can't replicate the chain that triggered the bug), a regression test there gives false confidence.

**If no correct seam exists, that itself is the finding.** Note it. The codebase architecture is preventing the bug from being locked down. Flag this for the next phase.

If a correct seam exists:

1. Turn the minimised repro into a failing test at that seam.
2. Watch it fail. If you forced the red by mutating code or a fixture, `diff` against a pristine copy to prove the mutation landed before you trust it.
3. Apply the fix per Fix location.
4. Watch it pass.
5. Search for the same faulty pattern elsewhere; fix every instance or list the ones left.
6. Re-run the Phase 1 feedback loop against the original (un-minimised) scenario.

Without a seam, run steps 3, 5, and 6.

### Fix location

Fix at the root cause, not where the symptom surfaced. Decide by the triggering state:

- **Legitimate state** (system may be in it): the code that broke on it is the root cause; handle the state there.
- **Illegitimate state** (should never exist): fix whatever produced it. A guard, retry, swallowed error, clamped value, or discarded state at the break point hides the bug; MUST NOT ship one as the fix.
- A workaround needing a paragraph-long justifying comment signals the wrong location; fix the code instead.

## Phase 6: Cleanup

Required before declaring done:

For both modes, remove temporary `[DEBUG-...]` instrumentation (grep the prefix) and throwaway prototypes (or move prototypes to a clearly-marked debug location).

For a fix, also verify:

- [ ] Original repro no longer reproduces (re-run the Phase 1 loop)
- [ ] Regression test passes (or absence of seam is documented)
- [ ] The hypothesis that turned out correct is stated in the commit / PR message, so the next debugger learns

## Output

For a confirmed cause, use [Root-cause report](references/root-cause-report.md) with the hypothesis log and current evidence. Track any user-supplied artifacts used during diagnosis and what each contributed. For a fix, also report the change, regression-test result or missing seam, other instances of the pattern fixed or left, and verification of the original scenario. Include the hypothesis log path.

If the deciding fact took a deep dig to find, propose a cheap always-on signal (log line, metric, assertion, error message) that would have shown it at first look.

Based on [Matt Pocock's diagnosing-bugs](https://github.com/mattpocock/skills/tree/main/skills/engineering/diagnosing-bugs). See [LICENSE](LICENSE).
