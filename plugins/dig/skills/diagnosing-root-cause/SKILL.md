---
name: diagnosing-root-cause
description: Find a bug's real root cause from evidence — build a red-capable feedback loop, reproduce, minimise, falsify hypotheses, and return a cited root-cause summary without fixing or saving the summary to a file.
argument-hint: "{{bugDescription}}"
---
# Diagnosing Root Cause

Find and return the confirmed root cause. Never apply the fix.

When exploring the codebase, read `CONTEXT.md` when present and relevant ADRs.

**Evidence** is a re-checkable fact: `path:line`, actual probe output, or an authoritative source with canonical URL. Everything else is a lead.

## Shared hypothesis log

Use `diagnosis-session-log`.

Default log:
`repository root/docs/tmp/{{bugSlug}}/diagnosis.md`.

The log records **only checked hypotheses**. Do not write phases, setup, loop attempts, fixes, tests, artifacts, plans, or next steps to it.

Each checked hypothesis MUST record:
- hypothesis;
- prediction;
- verification method;
- actual observed fact;
- evidence;
- result: `confirmed | falsified | blocked`.

If verification relies on an authoritative source, include its canonical URL in that hypothesis entry.

## Redact

Commands, outputs, and captured evidence MUST replace secrets with `<REDACTED>`. Credentials stay in environment variables. Quote only signal lines.

## Phase 1 — Build a red-capable feedback loop

Create one command/check that exercises the reported bug and can become green after a fix.

Prefer, in order:
1. existing failing test;
2. HTTP/CLI invocation;
3. captured trace replay;
4. throwaway harness;
5. browser automation;
6. fuzz/property loop;
7. bisect/differential loop;
8. HITL script from `scripts/hitl-loop.template.sh`.

The loop MUST be:
- red-capable for the user's exact symptom;
- deterministic or high-reproduction for flaky bugs;
- fast enough for repeated checks;
- agent-runnable.

If no valid loop can be built, stop and report what evidence or access is missing. MUST NOT invent a root cause from code reading alone.

## Phase 2 — Reproduce and minimise

Run the loop and verify it reproduces the exact symptom.

Shrink inputs, callers, configuration, data, and steps one at a time. Re-run after each cut.

Done when the smallest practical scenario still reproduces the same symptom.

## Phase 3 — Hypothesise

Generate 3–5 ranked falsifiable hypotheses before testing them.

Each MUST include a prediction:
> If X is the cause, then checking/changing Y will produce Z.

Show the hypotheses to the user, then proceed unless they re-rank or reject one.

Do **not** write open hypotheses to the shared log.

## Phase 4 — Verify

Test one hypothesis at a time. Change one variable at a time.

Preferred verification:
1. debugger/REPL;
2. focused probe or targeted log;
3. authoritative source when behavior depends on an external API/platform contract.

After each check, write exactly one hypothesis entry to the shared log using `diagnosis-session-log`.

A hypothesis is:
- `confirmed` only when evidence supports its prediction;
- `falsified` when evidence contradicts it;
- `blocked` when the check cannot be completed.

All hypotheses falsified → gather a new class of facts and create a new ranked set. Do not recycle falsified hypotheses without new evidence.

## Phase 5 — Confirm root cause

A confirmed hypothesis is the root cause only when:

1. **Mechanism chain** — cause to symptom in ordered steps, each backed by evidence.
2. **Fits all facts** — no known observation contradicts it.
3. **Rivals eliminated** — competing hypotheses were falsified with evidence.

Then run `draft-root-cause` to render the final cited root-cause summary from the shared hypothesis log plus the current run evidence.

## Output

Return the rendered root-cause summary directly to the user.

MUST NOT save the rendered root-cause summary to a file. Persistence belongs only to an explicitly invoked handoff/persistence workflow.
