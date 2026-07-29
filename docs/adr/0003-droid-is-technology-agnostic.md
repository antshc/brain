# Droid is technology-agnostic

The agent (renamed from Csdroid to Droid) and its `droid-*` skills carry no language- or toolchain-specific knowledge: no hardcoded build/test commands, project-file conventions, or language names in the agent or skill prose. All technology specifics — style, build/verify commands, layer conventions — live only in the per-repo `CODE.md`, `VERIFY.md`, and `MEMORY.md` files the agent resolves during INPUT. When `VERIFY.md` is unresolved, `droid-feedback`'s inline default discovers the toolchain by reading the repo's own `README.md` and exploring its project files, instead of falling back to a specific language's tooling.

## Considered Options

- **Keep the agent C#-specific** (status quo before this decision) — rejected: the `csdroid` name and the `droid-feedback` default's hardcoded `dotnet build`/`dotnet test`/`.csproj` walk-up made the harness unusable for non-C# repos and misstated the design intent every time someone read the agent's own description.
