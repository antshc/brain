---
name: draft-root-cause
description: Draft one cited root-cause summary from a confirmed diagnosis — symptom, mechanism chain, evidence table, ruled-out hypotheses. Use when asked to write up or report a root cause, or when another skill confirms one or needs its summary.
argument-hint: "[bugSlug]"
---

# Draft Root Cause

Render and print one root-cause summary. Drafting is **transcription**: every claim traces to the investigation log; it adds no facts and runs no probes.

**Input:** `logPath := /memories/session/diagnosis-{{bugSlug}}.md`, the `diagnosing-root-cause` investigation log. No log → the confirmed diagnosis stated in the conversation.

## Workflow

1. **Gate** → read the log; `Status` **MUST** be `root-cause-found` or `done` with `Correct hypothesis` set. Otherwise stop and report `Status` and `Next step`. *Done when* one confirmed hypothesis is named.
2. **Map** → fill each template section from the log:
   - Title, Summary of issue ← `Summary` → `Symptom` and captured signal.
   - Root cause & mechanism ← the confirmed `H` bullet and its mechanism chain; one numbered link per step, cause first, each citing `path:line` or a `P` bullet.
   - Evidence ← one row per `P` bullet that decided an `H` status.
   - Ruled out ← one line per falsified `H`, citing the `P` that killed it.
   - Known gap / tracking ← ticket, `// TODO`, or upstream issue found in the log; else omit.

   *Done when* every chain link cites, and every falsified `H` appears under Ruled out. A claim with no log citation is dropped or marked `Unknown`.
3. **Redact** → replace every secret with `<REDACTED>`; quote only signal lines. *Done when* no credential, token, or secret value remains.
4. **Render** → fill `templates/root-cause-summary.template.md` (from this skill's base directory) and print it without wrapper prose. *Done when* no placeholder remains.
