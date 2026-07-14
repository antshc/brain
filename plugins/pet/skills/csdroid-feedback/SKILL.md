---
name: csdroid-feedback
description: C# feedback loop — run LSP, build, test, and refactoring review against all changed files after implementation.
---

Run the feedback loop below against all files changed during the IMPLEMENTATION. All steps must pass.

---

# Feedback Loops

```
Task Progress:
- [ ] Step 0: Collect changed files
- [ ] Step 1: Verify — diagnostics, build, tests, and any project-specific checks (from VERIFY.md if present, else fallback)
- [ ] Step 2: Refactoring review (all changed files)
```

## Step 0: Collect changed files

Gather the full list of files changed during implementation. For each changed file, walk up to its `.csproj` to identify the affected project. Deduplicate:
- **Projects**: unique set of `.csproj` directories containing changed files.
- **Test projects**: for each affected project, find the sibling/child `.csproj` ending in `.Tests` that references it.

**Emit**: "Changed files: [list]. Affected projects: [list]. Test projects: [list]."

## Step 1: Verify (diagnostics, build, tests)

Use the `HARNESS_ROOT` value provided to you by the agent (substitute its literal absolute value for `$HARNESS_ROOT`; it defaults to the current working directory when no argument was given). Look for  `VERIFY.md` or `ARCHITECTURE.md` at `$HARNESS_ROOT` with the `Testing strategy` section for a Coding agent feedback loop instructions. If it exists, follow **all** of its steps in order — it may define more steps than the fallback, and may add project-specific checks (linting, formatting, integration tests, etc.). Otherwise, use the fallback below and emit: "Verify steps: fallback".

### Fallback

- **LSP diagnostics**: run `get_errors` on all changed files.
- **Build**: run `dotnet build <project-dir> --no-incremental` for each unique affected project (do not build the same project twice). A passing `get_errors` does NOT replace a build — StyleCop and analyzers only fire during a real build.
- **Tests**: run `dotnet test <test-project> --filter <relevant-classes>` for each unique affected test project, filtering by the classes that correspond to changed files in that test project's scope.

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
- NuGet source unreachable or authentication failure
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
