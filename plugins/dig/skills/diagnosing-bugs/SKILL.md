---
description: Diagnose and fix hard bugs and performance regressions — find the cited root cause, lock it with a regression test, apply the fix, and clean up. Use when the user says "diagnose"/"debug this" or reports something broken, throwing, failing, or slow and wants it fixed.
name: diagnosing-bugs
argument-hint: "{{bugDescription}}"
---
# Diagnosing Bugs

Root cause first, fix second. Skip phases only when explicitly justified.

## Phase 1–4 — Root cause

*Run `diagnosing-root-cause` skill to build a red-capable feedback loop, reproduce, minimise, falsify ranked hypotheses, and report a cited root-cause summary* for `{{bugDescription}}`.

Its **Redact** rules apply to every phase below.

Done when its log reads `Status: root-cause-found` and the root-cause summary is printed. Blocked → stop and report its `Next step`.

## Fix log

Keep writing the same diagnosis log with the `diagnosis-session-log` skill. Events beyond its shared ones:

| Log event | Write |
|---|---|
| A test fails or passes | `T` bullet: test name, run command, redacted verdict line |
| A fix is applied | `F` bullet: change summary with `path:line` |
| A cleanup item is done, or prevention is named | `K` bullet: the Phase 6 item or recommendation |

## Phase 5 — Fix + regression test

Write the regression test **before the fix** — but only at a **correct seam**: one where the test exercises the **real bug pattern** as it occurs at the call site. A seam too shallow (single-caller test when the bug needs several callers, unit test that can't replicate the triggering chain) gives false confidence.

**No correct seam is itself the finding.** Note it; the architecture prevents locking the bug down. Flag it for Phase 6.

With a correct seam:

1. Turn the minimised repro into a failing test at that seam.
2. Watch it fail.
3. Apply the fix.
4. Watch it pass.
5. Re-run the Phase 1 loop against the original (un-minimised) scenario.

Done when the log holds the `F` bullet and `T` bullets for fail-before, pass-after, and the original loop green — or the missing-seam finding.

## Phase 6 — Cleanup + post-mortem

Required before declaring done:

- [ ] Original repro no longer reproduces (re-run the Phase 1 loop)
- [ ] Regression test passes (or absence of seam is documented)
- [ ] All `[DEBUG-...]` instrumentation removed (`grep` the prefix)
- [ ] Throwaway prototypes deleted (or moved to a clearly-marked debug location)
- [ ] The correct hypothesis stated in the commit / PR message

**Then ask: what would have prevented this bug?** If the answer involves architectural change (no good test seam, tangled callers, hidden coupling), recommend it with specifics — **after** the fix is in.

Set `Status: done`, report `$logPath`, and tell the user to run `/handoff-diagnosis-patch` to persist the diagnosis for future investigations.
