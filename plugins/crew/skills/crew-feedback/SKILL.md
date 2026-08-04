---
name: crew-feedback
description: Technology-agnostic feedback loop — run LSP, build, and test against all changed files. Shared by Codey and Chorey.
---

# Feedback Loops

Run this loop against all files changed during this invocation. All steps must pass.

Copy this checklist and check off each item as you complete it:

```
- [ ] 0 Collect changed files
- [ ] 1 Verify — diagnostics, build, tests, plus any project-specific checks
```

## 0. Collect changed files

List every file changed during this invocation. For each, walk up to its nearest **Module** (the unit of code plus its build config — discovered from the repo's own structure, never assumed). Deduplicate:

- **Modules**: unique set of Module directories containing changed files.
- **Verification counterparts**: each affected Module's *seams*.

**Emit**: "Changed files: [list]. Affected Modules: [list]. Verification counterparts: [list]."

## 1. Verify (diagnostics, build, tests)

`VERIFY_PATH` resolved by the agent during INPUT → follow all steps in that `VERIFY.md` in order; it may add steps and project-specific checks. **Emit**: "Verify steps: VERIFY.md".

`VERIFY_PATH` unresolved → follow `FALLBACK.md` in this skill's directory. **Emit**: "Verify steps: default".

If Verify surfaces issues or requires changes, apply fixes and re-run this step over the updated full set of changed files.

## If a step fails

**Environment or access error** — do NOT attempt a fix. Stop and report `STATUS: blocked`. Covers: unreachable package source or auth failure, permission denied, SDK/runtime not installed, container not running, network failure.

**Code error** (compile error, test assertion, analyzer warning) — fix it and return to Verify.

**Retry cap**: if the same error persists after 3 retry cycles, stop and report `STATUS: partial` — unless the calling agent documents an override (Chorey self-reverts instead; see `chorey.agent.md`). Do not continue past the cap.

Do not report completion until all steps pass with 0 errors and 0 warnings.
