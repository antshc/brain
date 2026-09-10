---
name: inspect-nuget-source
description: Resolve a C# type or member that has no definition in local source to the NuGet package that owns it, and verify its real API or behavior from the package's XML docs or decompiled assembly. Use when a repo-wide search for a type, interface, base class, or member comes back empty; when a claim about a package type must be confirmed during code review, feature design, or exploration; when checking whether packages are restored; and before any disk-wide `find`/`grep`. Triggers even when the words "nuget", "package", or "decompile" never appear and the owning package is unknown — identifying it is this skill's first step, not a precondition.
---

# Inspect NuGet package source

Answer package questions from the restored package itself. Never guess a path; never run an unscoped filesystem-wide search first.

**Entry state — you do not need to know the package.** "A C# type/member has no definition anywhere in the repo" is a sufficient and complete trigger. Identifying the owning package is step 1's job, not a precondition for starting. Never treat "I'm not sure which package it's in" as a reason to keep grepping instead.

**Hard stop.** No command in this workflow, or in any reasoning that leads to it, may be rooted at `/`, `/usr`, `/opt`, `/etc`, or `/home`. `find / -iname '<Type>.cs'` is forbidden outright — including with `2>/dev/null`, `| head`, or "just to locate the file". Permitted roots: the repo root, the resolved global-packages folder, and `$HOME`. Read back the root argument of every recursive command before running it.

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
