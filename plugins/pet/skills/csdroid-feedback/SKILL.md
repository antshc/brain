---
name: csdroid-feedback
description: Run mandatory feedback loops after every C# file change — LSP diagnostics, build, and tests. Use after any implementation step in C# projects.
---

# Feedback Loops

These steps are **mandatory** after every file change — all three must run:

1. **LSP diagnostics** — call `get_errors` on every edited file
2. **Build** — run `dotnet build <project-dir> --no-incremental` for every `.csproj` that contains a changed file. A passing `get_errors` does NOT replace a build; StyleCop / analyzers only fire during a real build.
3. **Tests** — run only the test project(s) that cover the changed code:
   `dotnet test <test-project> --filter <relevant-class>`

If any step fails, fix the issue and re-run **from step 1** before proceeding.
Do not report completion until all three steps pass with 0 errors and 0 warnings.
