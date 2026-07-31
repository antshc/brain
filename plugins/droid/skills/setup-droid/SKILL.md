---
name: setup-droid
description: Manual, user-invoked bootstrap that restores missing Droid skill-owned guidance references from bundled fallbacks. Never called by the droid agent itself.
disable-model-invocation: true
---

# Setup Droid

Restore missing skill-owned guidance references from the fallback files next to their consuming skills. Run only when a person explicitly invokes this skill — never as part of an autonomous `droid` implementation run.

## Restore missing references

For each reference below, check whether it already exists. **Skip silently** if it exists — never overwrite, merge, or prompt about an existing reference. If missing, copy the matching fallback from its consuming skill into the target reference.

| Reference | Target path | Fallback |
|---|---|---|
| `CODE.md` | `../droid-implement/CODE.md` | `../droid-implement/FALLBACK.md` |
| `VERIFY.md` | `../droid-feedback/VERIFY.md` | `../droid-feedback/FALLBACK.md` |
| `GOTCHAS.md` | `../droid-gotchas/GOTCHAS.md` | `../droid-gotchas/FALLBACK.md` |


## Hard rules

- Manual invocation only — do not wire this into `droid.agent.md`'s INPUT step.
- Never overwrite, merge, or prompt about a reference that already exists.
- Do not create or modify repository files, Harness Settings, or `.droid/`.

**Emit**: "Restored: [list]. Skipped (already exist): [list]."
