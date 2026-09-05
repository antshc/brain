---
name: search-aws-sdk-nuget
description: AWS SDK for .NET NuGet package contract coverage. Trigger automatically — whether the user explicitly asks, or the agent itself needs this during its own research, implementation, or debugging — whenever AWS SDK for .NET package information, versions, APIs, method signatures, compatibility, upgrade guidance, or implementation/debugging work is needed for any `AWSSDK.*` or `AWS.Logger.*` package; on signals "AWSSDK.", "AWS SDK for .NET", "upgrade AWSSDK", "which AWS SDK version", or before writing/changing code against those SDKs or bumping their pinned versions.
compatibility: Requires AWS Documentation MCP Server (https://knowledge-mcp.global.api.aws)
---

# AWS SDK for .NET NuGet contract coverage

Scope: only the AWS SDK for .NET NuGet packages (`AWSSDK.*`, `AWS.Logger.*`) consumed by the current .NET solution. For AWS service concepts unrelated to the .NET SDK contract, or live cloud resources, route to `query-aws` instead (this skill covers the **package/API contract** angle only).

## Tools

| Tool | Use For |
|------|---------|
| `aws___search_documentation` | Find AWS SDK for .NET API references/guides — scope queries to "AWS SDK for .NET" + package/service name |
| `aws___read_documentation` | Read full page content when search excerpts don't cover the needed member/parameter/behavior |
| `aws___recommend` | Discover related API docs, migration guides, best practices |

## Discover pinned versions — don't assume, look them up

Version pins live in central MSBuild files; they are not recorded in this skill. Before answering any version/compatibility question:

1. Look for central package management files at the repo/solution root: `Directory.Packages.props`, `Directory.Build.props`, `Directory.Build.targets`.
2. Search them (and, if absent, individual `.csproj` files) for `AWSSDK.`/`AWS.Logger.` package references — e.g. `<PackageReference Update="AWSSDK.Core" Version="..."/>` or `<PackageVersion Include="AWSSDK.Core" Version="..."/>`.
3. Treat whatever you find as the current ground truth; do not reuse a version number from a prior turn/session without re-checking, since it may have been bumped since.

## Rules

- **Never inspect or disassemble locally restored NuGet packages** (NuGet cache, `packages/`, `obj/`/`bin/` DLLs) to determine SDK behavior, method signatures, or defaults. Restored packages are build artifacts, not documentation, and may not even match the version actually pinned.
- For API references, method signatures, parameter defaults, client configuration (retries/timeouts/pagination), breaking changes, or migration/upgrade guidance for any pinned package — call `aws___search_documentation` / `aws___read_documentation` directly, scoped to "AWS SDK for .NET" + the package/service name (e.g. `"AWS SDK for .NET DynamoDBv2 client retry configuration"`).
- Before changing any pinned version, use `aws___search_documentation`/`aws___read_documentation` to check the target version's release notes/changelog for breaking changes, and check the package's `.nuspec` dependency ranges (e.g. `AWSSDK.EC2` may pin a specific `AWSSDK.Core` range) so the bump doesn't silently violate another package's constraint.
- After bumping a version, update it only at its single central-management source — do not add per-project version overrides.

## Workflow

1. Identify the exact package(s) involved (`AWSSDK.Core`, `AWSSDK.DynamoDBv2`, etc.).
2. Discover the currently pinned version per the section above.
3. Call `aws___search_documentation` for the API/behavior/upgrade question, including the target version and package name in the query; follow up with `aws___read_documentation` if the excerpt is insufficient.
4. Cross-check any dependency-range constraints via the package's `.nuspec` (metadata only — dependency ranges, not implementation).
5. Implement/upgrade, then build to confirm restore succeeds.
