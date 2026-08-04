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

Source: `git status --porcelain` (uncommitted), or `git show --stat <BASELINE_COMMIT>` (checkpoint). None → emit "No changed files; nothing to verify", skip Step 1.

Per file, walk up to nearest **Module** (code unit + build config; discover from repo structure, never assume). Nested Modules → keep innermost only. Dedupe:

- **Modules**: unique Module dirs containing changed files.
- **Verification counterparts**: each Module's *seams* — existing tests/checks, discovered from `CODE.md`/`VERIFY.md`/convention. None found → nearest enclosing dir with a runnable check (test config, build file).

**Emit**:
- Changed files: [list]
- Affected Modules: [list]
- Verification counterparts: [list]

## 1. Verify (diagnostics, build, tests)

`VERIFY_PATH` resolved → run its steps in order; scope file/path-targeted commands to Step 0's Modules/counterparts, not the whole repo. **Emit**: "Verify steps: VERIFY.md".

`VERIFY_PATH` unresolved → run Step 0's verification counterparts.

If Verify surfaces issues or requires changes, apply fixes and re-run this step over the updated full set of changed files.

## If a step fails

**Environment or access error** — do NOT attempt a fix. Stop and report `STATUS: blocked`. Covers: unreachable package source or auth failure, permission denied, SDK/runtime not installed, container not running, network failure.

**Code error** (compile error, test assertion, analyzer warning) — fix it and return to Verify.

**Retry cap**: if the same error persists after 3 retry cycles, stop and report `STATUS: partial` — unless the calling agent documents an override (Chorey self-reverts instead; see `chorey.agent.md`). Do not continue past the cap.

Do not report completion until all steps pass with 0 errors and 0 warnings.
