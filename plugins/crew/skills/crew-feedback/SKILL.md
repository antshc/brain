---
name: crew-feedback
description: Technology-agnostic feedback loop — run LSP, build, and test against all changed files. Shared by Codey and Chorey.
---

Run the feedback loop below against all files changed during this invocation. All steps must pass.

---

# Feedback Loops

Copy this checklist and check off items as you complete them:
```
Feedback Loops Progress:
- [ ] Step 0: Collect changed files
- [ ] Step 1: Verify — diagnostics, build, tests, and any project-specific checks (from VERIFY.md if resolved, else inline default)
```

## Step 0: Collect changed files

Gather the full list of files changed during this invocation. For each changed file, walk up to its nearest **Module** (the unit of code plus its build config — discovered from the repo's own structure, never assumed) to identify the affected Module. Deduplicate:
- **Modules**: unique set of Module directories containing changed files.
- **Verification counterparts**: for each affected Module, find its *seams*.

**Emit**: "Changed files: [list]. Affected Modules: [list]. Verification counterparts: [list]."

## Step 1: Verify (diagnostics, build, tests)

Use the optional `VERIFY_PATH` value resolved by the agent during INPUT. When it is resolved, follow all steps in that `VERIFY.md` in order — it may define more steps than the default and may add project-specific checks; emit "Verify steps: VERIFY.md". When it is unresolved, run the **Default** below and emit "Verify steps: default".

**Default** — never hardcode a language or toolchain; discover it per repo:
- **LSP diagnostics**: run `get diagnostics` on all changed files.
- **Discover the toolchain**: read `HARNESS_REPO_PATH/README.md` for documented build/verify instructions, and explore the repo's own project/config files (manifests, build files, lockfiles) to identify the build and test tooling in use. A passing `get diagnostics` does NOT replace a build — many analyzers only fire during a real build.
- **Build**: run the discovered build command for each unique affected Module (do not build the same Module twice).
- **Tests**: run the discovered test command for each unique affected Verification counterpart, scoped to the classes/specs that correspond to changed files in that Verification counterpart's scope.

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

**Retry cap**: If after 3 retry cycles the same error persists, stop and report `STATUS: partial` — unless the calling agent documents an override (Chorey discards its own edits and self-reverts instead; see `chorey.agent.md`). Do not continue past the cap.

Do not report completion until all steps pass with 0 errors and 0 warnings.
