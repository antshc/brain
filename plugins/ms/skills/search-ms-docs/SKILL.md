---
name: search-ms-docs
description: Queries official Microsoft documentation for concepts, tutorials, configuration, limits, quotas, and best practices. Use for Microsoft technology questions that do not require implementation samples.
compatibility: Primarily uses the Microsoft Learn MCP Server (https://learn.microsoft.com/api/mcp); if that is unavailable, fall back to the mslearn CLI (`npx @microsoft/learn-cli`).
---

# Microsoft Docs

## Tools

| Tool | Purpose |
|---|---|
| `microsoft_docs_search` | Find official documentation. |
| `microsoft_docs_fetch` | Read a result in full. |

**Hard stop.** No command in this workflow, or in any reasoning that leads to it, may be rooted at `/`, `/usr`, `/opt`, `/etc`, or `/home`. `find / -iname '<Type>.cs'` is forbidden outright — including with `2>/dev/null`, `| head`, or "just to locate the file". Permitted roots: the repo root, the resolved global-packages folder, and `$HOME`. Read back the root argument of every recursive command before running it.

## Version

For a NuGet package, search `Directory.Packages.props`, `Directory.Build.props`, `Directory.Build.targets`, `Directory.Solution.targets`, and `*.csproj` in the workspace. If absent, read `obj/project.assets.json` for the resolved transitive version. For another SDK, read its dependency manifest and lockfile. Do not reuse a version from an earlier session.

## Workflow

1. For an SDK, .NET library, or API question, resolve the version from the workspace before searching.
2. Search with product, feature, intent, platform, and resolved version when applicable.
3. Fetch the full page for complete tutorials, configurations, limits, or incomplete excerpts.
4. Route implementation patterns and API signatures to `search-ms-code-samples`.
5. If Learn MCP is unavailable, use the equivalent `mslearn` CLI command.
