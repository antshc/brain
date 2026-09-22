---
name: search-aws-docs
description: Queries official AWS documentation for service concepts, API references, configuration, limits, regional availability, and best practices. Use for AWS questions, including code-adjacent API details.
context: fork
compatibility: Requires AWS Documentation MCP Server (https://knowledge-mcp.global.api.aws)
---

# AWS Docs

## Tools

| Tool | Purpose |
|---|---|
| `aws___search_documentation` | Find official docs. |
| `aws___read_documentation` | Read a result in full. |
| `aws___recommend` | Find related docs. |
| `aws___get_regional_availability` | Verify regional support. |
| `aws___list_regions` | List regions. |

**Hard stop.** No command in this workflow, or in any reasoning that leads to it, may be rooted at `/`, `/usr`, `/opt`, `/etc`, or `/home`. `find / -iname '<Type>.cs'` is forbidden outright — including with `2>/dev/null`, `| head`, or "just to locate the file". Permitted roots: the repo root, the resolved global-packages folder, and `$HOME`. Read back the root argument of every recursive command before running it.

## Version

For a NuGet package, search `Directory.Packages.props`, `Directory.Build.props`, `Directory.Build.targets`, `Directory.Solution.targets`, and `*.csproj` in the workspace. If absent, read `obj/project.assets.json` for the resolved transitive version. For another SDK, read its dependency manifest and lockfile. Do not reuse a version from an earlier session.

## Workflow

1. For SDK, library, or API questions, resolve the version from the workspace before searching.
2. Search with service, feature, intent, platform, and resolved version when applicable.
3. Read the full page for complete API, policy, configuration, or tutorial details.
4. Verify regional availability before recommending a regional deployment or feature.
