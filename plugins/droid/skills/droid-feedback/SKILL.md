---
name: droid-feedback
description: Technology-agnostic feedback loop — run LSP, build, test, and refactoring review against all changed files after implementation.
---

Run the feedback loop below against all files changed during the IMPLEMENTATION. All steps must pass.

---

# Feedback Loops

```
Feedback Loops Progress:
- [ ] Step 0: Collect changed files
- [ ] Step 1: Verify — diagnostics, build, tests, and any project-specific checks (from VERIFY.md if found, else fallback)
- [ ] Step 2: Refactoring review (all changed files)
```

## Step 0: Collect changed files

Gather the full list of files changed during implementation. For each changed file, walk up to its nearest **Module** (the unit of code plus its build config — discovered from the repo's own structure, never assumed) to identify the affected Module. Deduplicate:
- **Modules**: unique set of Module directories containing changed files.
- **Verification counterparts**: for each affected Module, find its sibling/child **Verification counterpart** (the unit that verifies it — tests, specs, whatever the repo calls it).

**Emit**: "Changed files: [list]. Affected Modules: [list]. Verification counterparts: [list]."

## Step 1: Verify (diagnostics, build, tests)

Use the optional `VERIFY_PATH` value resolved by the agent during INPUT. When it is provided, follow all steps in that `VERIFY.md` in order; it may define more steps than the fallback and may add project-specific checks. When it is unresolved, follow `FALLBACK.md` and emit: "Verify steps: fallback".

## Step 2: Refactoring review

After the Verify phase passes, review all changed files together for refactoring candidates:
- **Duplication** → extract function/class
- **Long methods** → break into private helpers (keep tests on public interface)
- **Shallow modules** → combine or deepen
- **Feature envy** → move logic to where data lives
- **Primitive obsession** → introduce value objects
- **Existing code** the new code reveals as problematic

If any candidate applies, refactor and return to the Verify phase (re-run over the updated full set of changed files).
If none apply, emit: "Refactoring review: no candidates." and proceed.

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
