---
applyTo: "**/*.cs,**/*.csproj,**/*.sln,**/Directory.Build.props,**/Directory.Packages.props"
description: "C# coding and test conventions — naming, formatting, CancellationToken propagation, error handling, utils usage, serialization, unit/integration test rules, and fakes/test-data reuse. Loads whenever any *.cs, csharp related file changes."
---
# .NET code conventions

- Follow the repository's existing naming, formatting, project layout, and dependency direction; check neighboring code before editing.
- Keep changes inside the affected functional slice and follow the repository's project boundaries.
- Dispose resources whose lifetime the changed code owns, including async resources; leave injected dependencies to their owner.
