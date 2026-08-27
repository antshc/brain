---
name: inspect-nuget-source
description: Verify a fact about a NuGet package's real API or behavior when the answer is not in local source — during code review, feature design, or code exploration. Find the referenced version across Directory.Packages.props, Directory.Build.props, Directory.Build.targets, Directory.Solution.targets, and *.csproj, locate the restored package on disk, read its shipped XML docs first, and decompile the assembly only when the docs are missing or insufficient. Never search the filesystem root. Trigger proactively — even without the words "nuget", "package", or "decompile" — whenever a claim about a type or member that lives in a package must be confirmed, and before any unscoped disk-wide `find`/`grep`.
---

# Inspect NuGet package source

Answer package questions from the restored package itself. Never guess a path; never run an unscoped filesystem-wide search first.

## 1. Find the referenced version

Grep the package id across every file that can pin or override a version, not just `Directory.Packages.props` — many repos declare/override versions in more than one place:

- `Directory.Packages.props` (central package management `<PackageVersion>` entries)
- `Directory.Build.props` / `Directory.Build.targets` (repo- or folder-wide overrides)
- `Directory.Solution.targets`
- `*.csproj` (direct `<PackageReference Include="..." Version="..." />`, used when CPM is off or overridden per-project)

Scope the grep to the repo/solution root you're working in (never the filesystem root):

```bash
grep -rn --include='Directory.Packages.props' --include='Directory.Build.props' \
  --include='Directory.Build.targets' --include='Directory.Solution.targets' \
  --include='*.csproj' -i '<packageid>' "<repo-root>"
```

If nothing turns up, the package may not be a direct dependency — check `obj/project.assets.json` for the resolved transitive version, or fall back to whatever version is already restored in the cache (step 2).

## 2. Locate the package

Get the resolved global cache — this already applies NuGet's own precedence:

```bash
dotnet nuget locals global-packages --list
```

If `dotnet` is unavailable, resolve manually, highest precedence first:

1. A per-restore `--packages <path>` override used by the project's build/restore scripts.
2. `NUGET_PACKAGES` environment variable.
3. `globalPackagesFolder` in an in-scope `nuget.config`.
4. OS default — `~/.nuget/packages`, or `%USERPROFILE%\.nuget\packages` on Windows.

Search only inside the resolved folder(s):

```bash
find "<cache>" -maxdepth 1 -iname '<packageid>*'
```

Layout: `<id>/<version>/lib/<tfm>/<Id>.dll`, the sibling `<Id>.xml`, and `<id>.nuspec`. The `.nupkg` is not there and is not needed. A `<id>/<version>/decompiled/` folder, if present, is output from a previous run of step 4 — reuse it.

**Never search from the filesystem root (`find / ...`).** If the resolved cache folder doesn't have the package, widen only within the user's home directory instead (e.g. `find "$HOME" -maxdepth 4 -iname '<packageid>*' 2>/dev/null`, or the OS-equivalent user profile dir), and say so in your answer.

## 3. Read the XML docs first

The doc file sits next to the DLL. Grep the entry for the symbol:

```bash
grep -A20 'name="T:<Namespace>.<Type>"' "<lib-path>/<Id>.xml"
```

Member keys: `T:` type, `M:` method, `P:` property, `F:` field, `E:` event.

Stop here if it answers the question. Docs state intent, not behavior — go to step 4 for control flow, defaults, null/edge handling, or when docs are absent or thin.

## 4. Decompile

Decompiled source lives next to the package, in a `decompiled/<tfm>/` folder inside the package's version directory:

```
<cache>/<id>/<version>/decompiled/<tfm>/
```

**Reuse before you decompile.** Check for a previous run first, and read it instead of re-running:

```bash
find "<cache>/<packageid>/<version>/decompiled" -name '*.cs' -print -quit
```

If that prints a file, the package is already decompiled — grep/read it and skip the rest of this step.

Otherwise decompile into that folder:

```bash
command -v ilspycmd || dotnet tool install -g ilspycmd
ilspycmd -p -o "<cache>/<packageid>/<version>/decompiled/<tfm>" "<lib-path>/<Id>.dll"
```

Keep the output in place so the next lookup reuses it. It lives in the package cache only — never copy it into the repo, commit it, or document it.

## 5. Report

Cite package id, version, and the type/member, and state whether the fact came from XML docs or decompiled IL.
