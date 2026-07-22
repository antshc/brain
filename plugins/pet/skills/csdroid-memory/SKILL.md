---
name: csdroid-memory
description: C# agent guardrails — reads MEMORY.md, the curated list of directives distilled from past session problems. Apply during the GUARDRAILS step, before implementation.
---

# Agent Memory

## Store

Curated guardrails live in `MEMORY.md`, kept inside the harness root at the fixed path `$HARNESS_ROOT/agent/MEMORY.md` — never recursively scanned, never the worktree cwd.

## Read Workflow (mandatory before implementation)

Use the `HARNESS_ROOT` value provided to you by the agent (substitute its literal absolute value for `$HARNESS_ROOT`; it defaults to the current working directory when no argument was given).

- Read `$HARNESS_ROOT/agent/MEMORY.md` in full.
- If the file doesn't exist or is empty → "No guardrails recorded yet."
- Apply every directive found during implementation — do not contradict one without reporting the conflict.

**Emit**: "Guardrails loaded: [summary]" or "No guardrails recorded yet."

## Hard Constraints

- Read only — never write to `MEMORY.md`. Curation is a manual human step performed outside this workflow, distilled from `agent/LOG.md` (per `csdroid-log`).
- Read the repo-resolved fixed path only. Never derive or search any other location.
