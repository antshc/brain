---
name: diagnosing-root-cause
description: Find a bug's real root cause from evidence — reuse prior diagnosis handoffs, build a red-capable feedback loop, reproduce, minimise, rank falsifiable hypotheses, instrument, and report a cited root-cause summary. Use when asked to find the root cause, debug, or investigate why something is broken, throwing, failing, or slow, without fixing it.
argument-hint: "{{bugDescription}}"
---
# Diagnosing Root Cause

Discipline for hard bugs. Ends at a confirmed, cited root cause; never applies the fix. Skip phases only when explicitly justified.

When exploring the codebase, read `CONTEXT.md` (if it exists) for a mental model of the relevant modules, and check ADRs in the area you're touching.

**Evidence** — a cited fact: `path:line`, a quoted line of primary documentation with its URL, or a probe with its actual output (command, request/response, log line with host and timestamp). Everything else — blog, forum, design doc, search hit, recollection, a prior handoff — is a **lead**: it may point at evidence, never stand in for it.

**Code changes allowed:** harnesses, fixtures, captured traces, `[DEBUG-…]` instrumentation. The fix belongs to the caller.

## Redact

Shown commands, outputs and captured artifacts **MUST** have every secret replaced by `<REDACTED>`. Build loops against env vars so the credential stays in the environment. Quote only the lines that carry the signal.

If the redacted output is not enough to diagnose the bug, say so and ask the user.

## Investigation log

Write the diagnosis log with the `diagnosis-session-log` skill. Events beyond its shared ones:

| Log event | Write |
|---|---|
| A prior handoff is read | `C` bullet |
| A feedback loop is tried | `L` bullet, with outcome |
| The loop is chosen | Bullet: loop command, first-run signal line, red-capable/deterministic/fast/agent-runnable |
| A Phase 2 loop run or minimising cut completes | Bullet: runs count and symptom match, or cut and verdict |
| Hypotheses ranked, or user re-ranks | `H` bullets with predictions, user input |
| A probe returns | `P` bullet, then the `H` status it decides |

## Reuse prior diagnoses

Prior handoffs live at `patches` under the repo root. Search their `## Matching signals` sections for this bug's error text, symptom words, components, and paths.

For each plausible match, read its markdown (`DIAGNOSIS-*.md`) and `root-cause.md`, and record a Phase 0 `C` bullet. Reuse what fits:

- its loop or replay steps as the first Phase 1 candidate;
- its patch (`git apply --check` first) as a ready-made harness;
- its confirmed root cause as a Phase 3 hypothesis.

A match is a **lead** — re-verify it in this run before relying on it.

Done when every match is recorded, or the log states none were found.

## Phase 1 — Build a feedback loop

**This is the skill.** With a **tight** pass/fail signal that goes red on _this_ bug, you will find the cause; bisection, hypotheses, and instrumentation just consume it. Without one, no amount of staring at code helps. Spend disproportionate effort here. **Be aggressive. Be creative. Refuse to give up.**

### Ways to construct one — roughly in this order

1. **Failing test** at whatever seam reaches the bug — unit, integration, e2e.
2. **Curl / HTTP script** against a running dev server.
3. **CLI invocation** with a fixture input, diffing stdout against a known-good snapshot.
4. **Headless browser script** (Playwright / Puppeteer) — drives the UI, asserts on DOM/console/network.
5. **Replay a captured trace** — save a real request / payload / event log to disk; replay it through the code path in isolation.
6. **Throwaway harness** — minimal subset of the system (one service, mocked deps) exercising the bug path with one call.
7. **Property / fuzz loop** — for "sometimes wrong output", run 1000 random inputs and look for the failure mode.
8. **Bisection harness** — bug appeared between two known states (commit, dataset, version): automate "boot at X, check" and `git bisect run` it.
9. **Differential loop** — same input through old vs new version (or two configs); diff outputs.
10. **HITL bash script** — last resort. Drive the human with `scripts/hitl-loop.template.sh` (from this skill's base directory) so the loop stays structured.

### Tighten the loop

Once you have _a_ loop, make it faster (cache setup, skip unrelated init, narrow scope), sharper (assert the specific symptom, not "didn't crash"), and more deterministic (pin time, seed RNG, isolate filesystem, freeze network). A 30-second flaky loop is barely better than none.

### Non-deterministic bugs

Goal is a **higher reproduction rate**, not a clean repro. Loop the trigger 100×, parallelise, add stress, narrow timing windows, inject sleeps. 50% is debuggable; 1% is not — keep raising it.

### When you genuinely cannot build a loop

Stop and say so. List what you tried. Ask the user for: (a) access to an environment that reproduces it, (b) a redacted captured artifact (HAR, log dump, core dump, timestamped recording), or (c) permission for temporary production instrumentation. **MUST NOT** hypothesise without a loop.

### Completion — a tight loop that goes red

Done when you can name **one command** you have **already run** (invocation and redacted output shown) that is:

- [ ] **Red-capable** — drives the actual bug path and asserts the **user's exact symptom**; goes green once fixed.
- [ ] **Deterministic** — same verdict every run (flaky bugs: pinned, high reproduction rate).
- [ ] **Fast** — seconds, not minutes.
- [ ] **Agent-runnable** — unattended; a human only via `scripts/hitl-loop.template.sh`.

Reading code to build a theory before this command exists is the exact failure this skill prevents — stop and return to the loop.

## Phase 2 — Reproduce + minimise

Run the loop; watch it go red. Confirm:

- [ ] It produces the failure the **user** described — not a nearby one. Wrong bug = wrong fix.
- [ ] Reproducible across runs (or at a debuggable rate).
- [ ] Exact symptom captured (error message, wrong output, timing).

Then shrink to the **smallest scenario that still goes red**: cut inputs, callers, config, data, and steps **one at a time**, re-running after each cut. A minimal repro shrinks the hypothesis space and becomes the caller's regression test.

Done when reproduced **and** every remaining element is load-bearing — removing any one turns the loop green.

## Phase 3 — Hypothesise

Generate **3–5 ranked hypotheses** before testing any — including boring ones (config, permissions, version skew, caching, clock, retries, ordering, resource exhaustion) and "the expectation is wrong". Each **MUST** be falsifiable:

> If <X> is the cause, then <changing Y> will make the bug disappear / <changing Z> will make it worse.

No statable prediction → sharpen or discard. Rank by cost of falsification, then by how many facts each explains.

**Show the ranked list to the user before testing**; they may re-rank or rule some out. Don't block — proceed with your ranking if the user is AFK.

Done when Phase 3 lists every hypothesis with its prediction, all `open`.

## Phase 4 — Instrument

Each probe maps to one Phase 3 prediction. **Change one variable at a time.**

1. **Debugger / REPL** if the env supports it — one breakpoint beats ten logs.
2. **Targeted logs** at boundaries that distinguish hypotheses.
3. Never "log everything and grep".

**Tag every debug log** with a unique prefix, e.g. `[DEBUG-a4f2]`, so cleanup is a single grep.

**Perf branch:** for performance regressions, establish a baseline measurement (timing harness, profiler, query plan), then bisect. Measure first.

Record each outcome before the next probe. All hypotheses falsified → the fact set is incomplete; gather a new class of fact (wider log window, another layer, deployed config vs source default) and return to Phase 3 — never re-test a falsified hypothesis.

Done when one hypothesis is `confirmed`, or all are falsified/blocked and `Next step` names the next probe.

## Phase 5 — Confirm root cause

A confirmed hypothesis becomes the root cause only once it passes all three:

1. **Mechanism chain** — cause to symptom in ordered steps, each cited `path:line` or `P` bullet; no "and then somehow".
2. **Fits every fact** — explains the delta, intermittency, working cases, and every logged fact; a contradiction sends it back to Phase 4.
3. **Nothing else fits** — every rival is falsified with evidence.

Then set `Status: root-cause-found` and `Correct hypothesis` in the log. *Run `draft-root-cause` skill to draft the cited root-cause summary — mechanism chain, evidence table, ruled-out hypotheses — from the log.*

Done when the summary is printed and the log reads `Status: root-cause-found`.
