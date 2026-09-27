---
applyTo: "**/*.cs,**/*.csproj,**/*.sln,**/Directory.Build.props,**/Directory.Packages.props"
---
# .NET code conventions

- Follow the repository's existing naming, formatting, project layout, and dependency direction; check neighboring code before editing.
- Keep changes inside the affected functional slice and follow the repository's project boundaries.
- Dispose resources whose lifetime the changed code owns, including async resources; leave injected dependencies to their owner.
