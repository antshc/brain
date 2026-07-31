---
name: droid-feedback
description: Technology-agnostic feedback loop — run LSP, build, and test against all changed files after implementation.
---

Run the feedback loop below against all files changed during the IMPLEMENTATION. All steps must pass.

---

# Feedback Loops

Copy this checklist and check off items as you complete them:
```
Feedback Loops Progress:
- [ ] Step 0: Collect changed files
- [ ] Step 1: Verify — diagnostics, build, tests, and any project-specific checks (from sibling VERIFY.md, else sibling FALLBACK.md)
```

## Step 0: Collect changed files

Gather the full list of files changed during implementation. For each changed file, walk up to its nearest **Module** (the unit of code plus its build config — discovered from the repo's own structure, never assumed) to identify the affected Module. Deduplicate:
- **Modules**: unique set of Module directories containing changed files.
- **Verification counterparts**: for each affected Module, find its *seams*.

**Emit**: "Changed files: [list]. Affected Modules: [list]. Verification counterparts: [list]."

## Step 1: Verify (diagnostics, build, tests)

Read the sibling `VERIFY.md` reference. When it is present, follow all steps in order and emit "Verify guidance: VERIFY.md". When it is absent, report the missing reference, follow sibling `FALLBACK.md`, and emit "Verify guidance: VERIFY.md missing; using FALLBACK.md."

If the Verify phase surfaces any issues or requires changes, apply fixes and re-run Step 1 over the updated full set of changed files.

---

## If a step fails

### Environment blockers — stop immediately

If any step fails with an **environment or access error**, do NOT attempt to fix it. Stop execution and report `STATUS: blocked`. Examples:
- Package source unreachable or authentication failure
- File/directory permission denied
- SDK or runtime not installed
- Docker/container not running
- Network connectivity failure

### Code errors — fix and retry from the Verify phase

If any step fails with a **code error** (compile error, test assertion, analyzer warning):
1. Fix the issue
2. Return to the Verify phase

**Retry cap**: If after 3 retry cycles the same error persists, stop and report `STATUS: partial`. Do not continue.

Do not report completion until all steps pass with 0 errors and 0 warnings.
