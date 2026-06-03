# Feedback Loops

These steps are **mandatory** after every file change — all three must run:
To find <project-dir>, walk up from the changed file until you find a .csproj. Use that directory.

1. **LSP diagnostics** — call `get_errors` on every edited file
2. **Build** — run `dotnet build <project-dir> --no-incremental` for every `.csproj` that contains a changed file. A passing `get_errors` does NOT replace a build; StyleCop / analyzers only fire during a real build.
3. **Tests** — run only the test project(s) that cover the changed code:
   - Find the test project by searching for a `.csproj` in a sibling or child directory whose name ends in `.Tests` and references the production project.
   - `dotnet test <test-project> --filter <relevant-class>`

If any step fails, fix the issue and re-run **from step 1** before proceeding.
Do not report completion until all three steps pass with 0 errors and 0 warnings.
