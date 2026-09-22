---
name: search-aws-sdk-nuget
description: Resolves AWS SDK for .NET NuGet package versions and verifies their APIs, compatibility, and upgrade guidance from official AWS documentation. Use for `AWSSDK.*` or `AWS.Logger.*` package/API work, upgrades, or debugging.
compatibility: Requires AWS Documentation MCP Server (https://knowledge-mcp.global.api.aws)
---

# AWS SDK for .NET NuGet

Use only for `AWSSDK.*` and `AWS.Logger.*` contracts in the current solution. Route service concepts and cloud-resource questions to `search-aws-docs`.

## Tools

| Tool | Purpose |
|---|---|
| `aws___search_documentation` | Find SDK APIs, guidance, and release notes. |
| `aws___read_documentation` | Read complete contract details. |
| `aws___recommend` | Find related guidance. |

**Hard stop.** No command in this workflow, or in any reasoning that leads to it, may be rooted at `/`, `/usr`, `/opt`, `/etc`, or `/home`. `find / -iname '<Type>.cs'` is forbidden outright — including with `2>/dev/null`, `| head`, or "just to locate the file". Permitted roots: the repo root, the resolved global-packages folder, and `$HOME`. Read back the root argument of every recursive command before running it.

## Version

Search `Directory.Packages.props`, `Directory.Build.props`, `Directory.Build.targets`, `Directory.Solution.targets`, and `*.csproj` in the workspace for the package. If absent, read `obj/project.assets.json` for the resolved transitive version. Do not reuse a version from an earlier session.

## Workflow

1. Identify the exact package and resolve its version.
2. Search official AWS documentation with the package, resolved version, service, and requested API or behavior; read the result in full when needed.
3. Before an upgrade, verify release notes and `.nuspec` dependency ranges.
4. Change the single authoritative version declaration and build to verify restore.
