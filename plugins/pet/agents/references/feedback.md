# Feedback Loops

**Mandatory** after every file change. Copy this checklist and check off items as you complete them:

```
Task Progress:
- [ ] Step 1: LSP diagnostics (get_errors on every edited file)
- [ ] Step 2: Build (dotnet build --no-incremental)
- [ ] Step 3: Tests (dotnet test --filter)
- [ ] Step 4: Refactoring review
```

## Setup

To find `<project-dir>`, walk up from the changed file until you find a `.csproj`. Use that directory.

## Step 1: LSP diagnostics

Run: `get_errors` on every edited file.

## Step 2: Build

Run: `dotnet build <project-dir> --no-incremental` for every `.csproj` that contains a changed file.

A passing `get_errors` does NOT replace a build — StyleCop and analyzers only fire during a real build.

## Step 3: Tests

Find the test project by searching for a `.csproj` in a sibling or child directory whose name ends in `.Tests` and references the production project.

Run: `dotnet test <test-project> --filter <relevant-class>`

## Step 4: Refactoring review

After steps 1–3 pass, review changed files for refactoring candidates:
- **Duplication** → extract function/class
- **Long methods** → break into private helpers (keep tests on public interface)
- **Shallow modules** → combine or deepen
- **Feature envy** → move logic to where data lives
- **Primitive obsession** → introduce value objects
- **Existing code** the new code reveals as problematic

If any candidate applies, refactor and return to Step 1.
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
