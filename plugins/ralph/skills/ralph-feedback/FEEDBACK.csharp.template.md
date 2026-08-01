# FEEDBACK

<!-- Followed in order by ralph-feedback. List every repository-specific changed-file verification step. -->

1. Run `get diagnostics` on all changed files.

2. **Collect changed files**

For each changed file, walk up to its `.csproj` to identify the affected project. Deduplicate:
- **Projects**: unique set of `.csproj` directories with changed files.
- **Test projects**: for each affected project, its sibling/child `.csproj` ending in `.Tests` that references it.

**Emit**: "Changed files: [list]. Affected projects: [list]. Test projects: [list]."

3. Run `dotnet format` on affected and test projects.
4. **Build all** — Run `dotnet build {{solution}}.sln`.

   `get diagnostics` doesn't replace a build — StyleCop/analyzers only fire on a real build.

5. **Unit Tests** — Run `dotnet test {{solution}}.sln --no-build`.

   Reuses the step 4 build (`--no-build`); runs the whole solution's unit tests.
