---
name: search-ms-code-samples
description: Finds official Microsoft code samples and verifies SDK APIs, signatures, and migrations. Use for Microsoft SDK, .NET library, Azure client library, or Microsoft API implementation, debugging, and review.
compatibility: Primarily uses the Microsoft Learn MCP Server (https://learn.microsoft.com/api/mcp); if that is unavailable, fall back to the mslearn CLI (`npx @microsoft/learn-cli`).
---

# Microsoft Code Reference

## Tools

| Tool | Purpose |
|---|---|
| `microsoft_docs_search` | Verify packages, types, and members. |
| `microsoft_code_sample_search` | Find official working samples. |
| `microsoft_docs_fetch` | Read full API and migration details. |

**Hard stop.** No command in this workflow, or in any reasoning that leads to it, may be rooted at `/`, `/usr`, `/opt`, `/etc`, or `/home`. `find / -iname '<Type>.cs'` is forbidden outright — including with `2>/dev/null`, `| head`, or "just to locate the file". Permitted roots: the repo root, the resolved global-packages folder, and `$HOME`. Read back the root argument of every recursive command before running it.

## Version

For a NuGet package, search `Directory.Packages.props`, `Directory.Build.props`, `Directory.Build.targets`, `Directory.Solution.targets`, and `*.csproj` in the workspace. If absent, read `obj/project.assets.json` for the resolved transitive version. For another SDK, read its dependency manifest and lockfile. Do not reuse a version from an earlier session.

## Workflow

1. For a NuGet, .NET library, or API request, identify the owning package and resolve its version.
2. Search for the package, resolved version, namespace, type, member, task, and target language.
3. Fetch complete details for overloads, parameters, migrations, or unclear excerpts.
4. Find a sample before writing unfamiliar code; compare it with failing code during debugging.
5. If Learn MCP is unavailable, use the equivalent `mslearn` CLI command.