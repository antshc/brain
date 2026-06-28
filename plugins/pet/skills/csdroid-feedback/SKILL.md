---
name: csdroid-feedback
description: C# feedback loop — run LSP, build, test, and refactoring review against all changed files after implementation.
---

Run the feedback loop below against all files changed during the IMPLEMENTATION. All four steps must pass.

Do not suppress warnings (e.g., `#pragma warning disable`) to achieve a green build.

If feedback loops fail, fix the issues and re-run.

If feedback returns STATUS: blocked or partial, stop immediately and emit that status in the STATUS REPORT after completing RECORD DECISIONS.

---

# Feedback Loops

```
Task Progress:
- [ ] Step 0: Collect changed files
- [ ] Step 1: LSP diagnostics (get_errors on all changed files)
- [ ] Step 2: Build (dotnet build --no-incremental, deduplicated)
- [ ] Step 3: Tests (dotnet test --filter, all affected projects)
- [ ] Step 4: Refactoring review (all changed files)
```

## Step 0: Collect changed files

Gather the full list of files changed during implementation. For each changed file, walk up to its `.csproj` to identify the affected project. Deduplicate:
- **Projects**: unique set of `.csproj` directories containing changed files.
- **Test projects**: for each affected project, find the sibling/child `.csproj` ending in `.Tests` that references it.

**Emit**: "Changed files: [list]. Affected projects: [list]. Test projects: [list]."

## Step 1: LSP diagnostics

Run: `get_errors` on all changed files.

## Step 2: Build

Run: `dotnet build <project-dir> --no-incremental` for each unique affected project (do not build the same project twice).

A passing `get_errors` does NOT replace a build — StyleCop and analyzers only fire during a real build.

## Step 3: Tests

Run: `dotnet test <test-project> --filter <relevant-classes>` for each unique affected test project.

Filter by all classes that correspond to changed files in that test project's scope.

## Step 4: Refactoring review

After steps 1–3 pass, review all changed files together for refactoring candidates:
- **Duplication** → extract function/class
- **Long methods** → break into private helpers (keep tests on public interface)
- **Shallow modules** → combine or deepen
- **Feature envy** → move logic to where data lives
- **Primitive obsession** → introduce value objects
- **Existing code** the new code reveals as problematic

If any candidate applies, refactor and return to Step 1 (re-run over the updated full set of changed files).
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

### Code errors — fix and retry from Step 1

If any step fails with a **code error** (compile error, test assertion, analyzer warning):
1. Fix the issue
2. Return to Step 1

**Retry cap**: If after 3 retry cycles the same error persists, stop and report `STATUS: partial`. Do not continue.

Do not report completion until all four steps pass with 0 errors and 0 warnings.
