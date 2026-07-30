---
name: droid-gotchas
description: Agent gotchas — reads GOTCHAS.md, the curated list of directives distilled from past session problems. Apply during the GOTCHAS step, before implementation.
---

# Gotchas

Copy this checklist and check off items as you complete them:
```
Gotchas Progress:
- [ ] Step 1: Read GOTCHAS_PATH in full (or note "No gotchas recorded yet")
- [ ] Step 2: Apply every directive during implementation
```

## Store

Curated gotchas live in the optional `GOTCHAS_PATH` resolved by the agent during INPUT.

## Read Workflow (mandatory before implementation)

- When `GOTCHAS_PATH` is provided, read that file in full.
- When `GOTCHAS_PATH` is unresolved or the file is empty → "No gotchas recorded yet."
- Apply every directive found during implementation — do not contradict one without reporting the conflict.

**Emit**: "Gotchas loaded: [summary]" or "No gotchas recorded yet."

## Hard Constraints

- Read only — never write to `GOTCHAS.md`. Curation is a manual human step performed outside this workflow, distilled from `.droid/LOG.md` (per `droid-log`).
- Read only the supplied `GOTCHAS_PATH`. Never derive or search for another location.
