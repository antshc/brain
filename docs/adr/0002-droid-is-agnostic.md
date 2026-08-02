# Droid is run-location- and technology-agnostic

- **Run-location-agnostic**: Droid executes code, Git, build, test, and exploration commands in the directory from which it was launched and does not change directories to interpret a worktree path. `WORKTREE_PATH` is not part of Droid's prompt, arguments, status output, or documentation. The agent does not need to know whether its directory is a worktree, a repository root, or another valid workspace; callers establish the execution location before invocation.
- **Technology-agnostic**: the agent (renamed from Csdroid to Droid) and its `droid-*` skills carry no language- or toolchain-specific knowledge either: no hardcoded build/test commands, project-file conventions, or language names in the agent or skill prose.
- **Per-repo resolution**: Droid resolves its per-repo `CODE.md`, `VERIFY.md`, and `GOTCHAS.md` files from its current directory during INPUT. When one is not present there, Droid discovers the Harness Root by resolving Harness Settings (via `resolve-harness`/the nearest `.harness.env`) instead of assuming its current directory is the harness root. All technology specifics — style, build/verify commands, layer conventions — live only in these per-repo files.
- **Fallback discovery**: when `VERIFY.md` is absent, `droid-feedback`'s fallback discovers the toolchain by reading the repo's own `README.md` and exploring its project files, instead of falling back to a specific language's tooling.

## Considered Options

- **Keep the agent C#-specific** (status quo before this decision) — rejected: the `csdroid` name and the `droid-feedback` fallback's hardcoded `dotnet build`/`dotnet test`/`.csproj` walk-up made the harness unusable for non-C# repos and misstated the design intent every time someone read the agent's own description.
