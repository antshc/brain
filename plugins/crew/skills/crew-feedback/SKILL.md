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

**Emit**: "Changed files: [list]".

## 1. Verify (diagnostics, build, tests)

`VERIFY_PATHS` non-empty → run every loaded `VERIFY-<stack>.md` in sequence, not only the primary Stack's when several matched. Each file owns its own Stack's walk-up from a changed file to its nearest Module and the mapping to that Module's Verification counterparts, in that Stack's own vocabulary, and scopes its commands to what that walk-up reaches — never the whole repo. **Emit**: "Verify steps: [list of VERIFY-<stack>.md paths]".

`VERIFY_PATHS` empty (no matched Stack's verification steps resolved) → **unscoped fallback**: discover the toolchain from the repo's own README and project/build files (manifests, CI config — never assume a specific tool), and run it once across the whole repository. **Emit**: "Verify steps: unscoped — discovered <tool/command> from <source>", and state plainly that the run was unscoped.

If Verify surfaces issues or requires changes, apply fixes and re-run this step over the updated full set of changed files.

## If a step fails

**Environment or access error** — do NOT attempt a fix. Stop and report `STATUS: blocked`. Covers: unreachable package source or auth failure, permission denied, SDK/runtime not installed, container not running, network failure.

**Code error** (compile error, test assertion, analyzer warning) — fix it and return to Verify.

**Retry cap**: if the same error persists after 3 retry cycles, stop and report `STATUS: partial` — unless the calling agent documents an override (Chorey self-reverts instead; see `chorey.agent.md`). Do not continue past the cap.

Do not report completion until every Verify step — scoped or unscoped — passes with 0 errors and 0 warnings; a partially-passed run never reports completion.
