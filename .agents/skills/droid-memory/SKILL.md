---
name: droid-memory
description: Agent guardrails — reads MEMORY.md, the curated list of directives distilled from past session problems. Apply during the GUARDRAILS step, before implementation.
---

# Guardrails

Copy this checklist and check off items as you complete them:
```
Guardrails Progress:
- [ ] Step 1: Read MEMORY_PATH in full (or note "No guardrails recorded yet")
- [ ] Step 2: Apply every directive during implementation
```

## Store

Curated guardrails live in the optional `MEMORY_PATH` resolved by the agent during INPUT.

## Read Workflow (mandatory before implementation)

- When `MEMORY_PATH` is provided, read that file in full.
- When `MEMORY_PATH` is unresolved or the file is empty → "No guardrails recorded yet."
- Apply every directive found during implementation — do not contradict one without reporting the conflict.

**Emit**: "Guardrails loaded: [summary]" or "No guardrails recorded yet."

## Hard Constraints

- Read only — never write to `MEMORY.md`. Curation is a manual human step performed outside this workflow, distilled from `.droid/LOG.md` (per `droid-log`).
- Read only the supplied `MEMORY_PATH`. Never derive or search for another location.
