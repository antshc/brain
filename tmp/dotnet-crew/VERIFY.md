# Coding agent feedback loop
## ZIC project verify (conditional)

Run only if any changed file path is outside `support/src/` (i.e. touches the ZIC solution, `all.sln`, beyond Support). Skip this section entirely for a support-only changeset — see "Support solution verify" below. Coarse: every step below runs regardless of which non-support files changed.

- **Prerequisite:** docker daemon running (mock-sanity step).
- **Run mode:** Health-check guard.

Conditional verification (proxy tests, DynamoDB integration tests, changed REST API test selection) is **not** part of this loop — baked into each issue's Verify section at issue-creation time.

All commands run from `workspace/zerto-zic` or `workspace/zerto-zic.worktrees/{{currentWorktree}}`

1. **LSP diagnostics** — Run `get diagnostics` on all changed files.

2. **Collect changed files**

For each changed file, walk up to its `.csproj` to identify the affected project. Deduplicate:
- **Projects**: unique set of `.csproj` directories with changed files.
- **Test projects**: for each affected project, its sibling/child `.csproj` ending in `.Tests` that references it.

**Emit**: "Changed files: [list]. Affected projects: [list]. Test projects: [list]."

3. Run `dotnet format` on affected **Projects** and **Test projects**.
4. **Build all** — Run `dotnet build all.sln`.

   `get diagnostics` doesn't replace a build — StyleCop/analyzers only fire on a real build.

5. **Unit Tests** — Run unit tests for the **Test projects** `dotnet test <Test project> --no-build --filter "Category!~IntegrationTest&Category!~TestingFrameworkTest&Category!~CleanUp&Category!~AutomationTest"`.

   Reuses the step 4 build (`--no-build`); runs the whole solution's unit tests.


## Support solution verify (conditional)

Run only if any changed file path is under `support/src/`. For a support-only changeset (no changed file outside `support/src/`), this is the entire verify loop — "ZIC project verify" above is skipped. For a mixed changeset (support + non-support files), use the "ZIC project verify" section, not a replacement.

1. **Build** — Run `dotnet build support/src/Support.sln`.
2. **Unit Tests** — Run `dotnet test support/src/Support.sln --no-build`.

   No `Category` filter needed: Support.sln's test project has no `Category` traits — its true integration tests are marked `[Fact(Skip = "...")]` and are auto-skipped.

# Refactoring review
After the Verify phase passes, review all changed files together for refactoring candidates:
- **Duplication** → extract function/class
- **Long methods** → break into private helpers (keep tests on public interface)
- **Shallow modules** → combine or deepen
- **Feature envy** → move logic to where data lives
- **Primitive obsession** → introduce value objects
- **Existing code** the new code reveals as problematic