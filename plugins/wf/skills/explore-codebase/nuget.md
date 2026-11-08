# NuGet source inspection

Resolve a C# type/member absent from repository source to the owning restored package; verify the version-specific API or behavior from XML documentation or decompiled IL. An unknown package ID is a valid starting point.

**Search boundary.** Resolve every recursive search root first: target checkout, its resolved NuGet package cache, or a bounded user-profile fallback. Never search from `/`, `/usr`, `/opt`, `/etc`, or `/home` as a literal root; never search arbitrary disks for a `.cs` file. Keep generated decompilation in the package cache, outside the repository.

## 1. Identify package and resolved version

1. Read the call site, namespace, `using` declarations, and referenced project. Check that `rg -uu` did not find the type in local source.
2. Inspect the relevant project's `obj/project.assets.json`: `libraries` identifies restored package IDs/versions, and `packageFolders` identifies the actual cache roots. If missing, inspect project references and lock files, then report that restore evidence is absent.
3. Check all in-scope version declarations, including central and per-project overrides:

   ```bash
   rg -n -i -F '<package-id>' -g 'Directory.Packages.props' -g 'Directory.Build.props' -g 'Directory.Build.targets' -g 'Directory.Solution.targets' -g '*.csproj' '<target-checkout>'
   ```

4. When the package ID is unknown, narrow candidates from the namespace, call site, dependency graph, and assemblies listed in `project.assets.json`; search XML docs only within those resolved candidate packages. Do not require the caller to supply a package ID. An unresolved owner is UNKNOWN, not a reason to widen to the filesystem.

Use the **restored** version from `project.assets.json` when declarations differ. For a transitive dependency, use its resolved ID/version; never infer its version from a direct reference.

## 2. Locate the restored assembly

Use the `packageFolders` entries from the relevant assets file when present. Otherwise query:

```bash
dotnet nuget locals global-packages --list
```

If `dotnet` is unavailable, resolve in this order: restore's `--packages` override, `NUGET_PACKAGES`, an in-scope `nuget.config` `globalPackagesFolder`, then the platform default (`~/.nuget/packages` or `%USERPROFILE%\.nuget\packages`). Restrict inspection to these roots; if a known package is missing, optionally search the user's profile with a bounded depth and report the fallback.

Package layout: `<cache>/<id>/<version>/lib/<tfm>/<Id>.dll` and optional `.xml`, plus `<id>.nuspec`. Choose the assembly/TFM consumed by the target project, including `ref/<tfm>` when verifying compile-time surface. Reuse any `<cache>/<id>/<version>/decompiled/<tfm>/` from an earlier run.

## 3. Verify the claim

**XML first.** Search the matching XML documentation for `name="T:<Namespace>.<Type>"` or member keys `M:`, `P:`, `F:`, `E:`:

```bash
rg -n -A 20 -F 'name="T:<Namespace>.<Type>"' '<assembly-xml-path>'
```

XML docs establish documented contracts, not executable behavior. For a signature absent from XML, control flow, defaults, retries, null/edge handling, or conflicting docs, inspect IL:

1. Reuse an existing decompiled source tree for the exact package/version/TFM.
2. If absent, use `ilspycmd`; install per-user with `dotnet tool install -g ilspycmd` only when needed, then decompile:

   ```bash
   ilspycmd -p -o '<cache>/<id>/<version>/decompiled/<tfm>' '<assembly-dll-path>'
   ```

3. Search the decompiled folder with `rg`, read the relevant method, and distinguish actual implementation from the reference assembly.

If the package is not restored, the symbol is not NuGet-owned, or tools are unavailable, report the precise unresolved step rather than claiming an API or implementation.

## 4. Return evidence

Give package ID, restored version, assembly/TFM, type/member, and the deciding XML/decompiled path or snippet. Label facts **XML documentation** or **decompiled implementation**; keep applicability and remaining uncertainty explicit. Apply the caller's `@outputShape` and `@outputArtifact` contract.
