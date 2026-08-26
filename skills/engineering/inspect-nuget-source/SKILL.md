---
name: inspect-nuget-source
description: Verify a fact about a NuGet package's real API or behavior when the answer is not in local source — during code review, feature design, or code exploration. Locate the restored package on disk, read its shipped XML docs first, and decompile the assembly only when the docs are missing or insufficient. Trigger proactively — even without the words "nuget", "package", or "decompile" — whenever a claim about a type or member that lives in a package must be confirmed, and before any unscoped disk-wide `find`/`grep`.
---

# Inspect NuGet package source

Answer package questions from the restored package itself. Never guess a path; never run an unscoped filesystem-wide search first.

## 1. Locate the package

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

Layout: `<id>/<version>/lib/<tfm>/<Id>.dll`, the sibling `<Id>.xml`, and `<id>.nuspec`. The `.nupkg` is not there and is not needed.

Widen to a full-disk search (`find / -iname '<packageid>*' 2>/dev/null`) only as a last resort, and say so in your answer.

## 2. Read the XML docs first

The doc file sits next to the DLL. Grep the entry for the symbol:

```bash
grep -A20 'name="T:<Namespace>.<Type>"' "<lib-path>/<Id>.xml"
```

Member keys: `T:` type, `M:` method, `P:` property, `F:` field, `E:` event.

Stop here if it answers the question. Docs state intent, not behavior — go to step 3 for control flow, defaults, null/edge handling, or when docs are absent or thin.

## 3. Decompile

```bash
command -v ilspycmd || dotnet tool install -g ilspycmd
ilspycmd -p -o /tmp/<packageid>-decompiled "<lib-path>/<Id>.dll"
```

Read what you need, then discard. Throwaway output — never committed, cached, or documented.

## 4. Report

Cite package id, version, and the type/member, and state whether the fact came from XML docs or decompiled IL.
