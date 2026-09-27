---
applyTo: "**/*.cs,**/*.csproj,**/*.sln,**/*.fs,**/*.fsproj,**/*.vb,**/*.vbproj,**/*.props"
---
# .NET code conventions

- Follow the repository's existing naming, formatting, project layout, and dependency direction; check neighboring code before editing.
- Keep changes inside the affected functional slice. A nearest `.csproj` defines the build project; trace its test project through references and existing tests.
- Dispose acquired `IDisposable` resources on every exit path.
- Add or update a test at an observable input/output seam for changed behavior; prefer an existing slice test. The `codey-dotnet` agent owns test selection and feedback.
