# Droid is technology-agnostic

The agent (renamed from Csdroid to Droid) and its `droid-*` skills carry no language- or toolchain-specific knowledge: no hardcoded build/test commands, project-file conventions, or language names in the agent or skill prose. Coding, verification, and Gotchas guidance live in mutable references beside their consuming skills. When a reference is absent, its consuming skill reports the absence and uses a bundled technology-agnostic fallback; verification discovers the toolchain from the invocation directory's `README.md` and project files instead of falling back to a specific language's tooling.

## Considered Options

- **Keep the agent C#-specific** (status quo before this decision) — rejected: the `csdroid` name and the `droid-feedback` fallback's hardcoded `dotnet build`/`dotnet test`/`.csproj` walk-up made the harness unusable for non-C# repos and misstated the design intent every time someone read the agent's own description.
