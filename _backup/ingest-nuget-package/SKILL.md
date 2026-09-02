---
name: ingest-nuget-package
description: Decompile a NuGet package (plus its auto-detected `.Abstractions` companion) to real C# source and generate, straight from that source, a signature-only public-API surface documented with XML doc comments grounded in user-supplied repository paths — persisted as one committed Markdown file per package family under a package-id-prefix-grouped `search-nuget-<slug>` skill, auto-discovered anywhere under the reporoot or else scaffolded under `.github/skills/`. Trigger only on explicit user request ("document the API of NuGet package X", "decompile and document Y") — never automatically. Maintainer-only. The grouping prefix is auto-detected from the PackageId (or supplied explicitly); the source repository is auto-detected from the restored `.nuspec` but used only as provenance, never for grouping.
argument-hint: package=<PackageId>@<version> paths=<path1>[,<path2>,...] [prefix=<Prefix>[,<Prefix2>,...]] [force=decompile|describe|all]
---

# Document a NuGet package's API from real decompiled source

Decompile → describe → assemble. The decompiled tree is **read-only evidence**; the Markdown is generated directly from it, one fragment per source file, and never by editing the decompiled `.cs` files. The persisted deliverable is a **public-API surface view**: type/member signatures and XML doc comments only. Method bodies, private members, `using` directives, and decompiler artifacts are never committed.

**Skill base directory:** `<reporoot>/.github/skills/ingest-nuget-package/`. Load this skill's reference files from there — `references/documentation-template.md`, `references/skill-bootstrap-template.md` — never via a bare relative link, which resolves against the runtime CWD.

## Arguments

| Argument | Required | Description |
| --- | --- | --- |
| `package` | yes | `<PackageId>@<version>`, e.g. `Contoso.Infra.Utils@4.0.39`. |
| `paths` | yes | Comma-separated repository paths to search for call sites, implementations, and existing contract comments. Ask if absent. |
| `prefix` | no | One or more comma-separated PackageId prefixes (e.g. `Contoso.Infrastructure` or `Contoso.Infra,Contoso.Infrastructure`) to use verbatim as the target skill's grouping key instead of auto-detecting one — the way to deliberately fold this package into an existing or differently-scoped skill. Default: auto-detect (see step 3). |
| `force` | no | `decompile` re-runs `ilspycmd` (and invalidates that package's fragment cache, since fragments derive from the decompiled source), `describe` re-generates fragments from the existing decompilation, `all` does both. Default: reuse whatever already exists. |

Ask for any missing required argument before proceeding. The source repository (`owner/repo`) is never an argument — step 2 detects it, for provenance only.

## Workflow

1. **Decompiler.** `command -v ilspycmd` → if missing, `dotnet tool install -g ilspycmd`.

2. **Restore + detect source repository.** Reuse an existing restore; never restore unconditionally.
   ```bash
   pkgdir="nuget/.packages/<id-lowercase>/<version>"
   if [ -d "$pkgdir" ]; then
     echo "Reusing $pkgdir"
   else
     tmp=$(mktemp -d)
     cat > "$tmp/restore.csproj" <<'EOF'
   <Project Sdk="Microsoft.NET.Sdk">
     <PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup>
     <ItemGroup><PackageReference Include="ID" Version="VERSION"/></ItemGroup>
   </Project>
   EOF
     sed -i "s/ID/<Id>/;s/VERSION/<version>/" "$tmp/restore.csproj"
     dotnet restore "$tmp/restore.csproj" --packages nuget/.packages
   fi
   ```
   Read `<repository type="git" url="...">` from `$pkgdir/<id-lowercase>.nuspec` (fall back to `<projectUrl>`), strip the `https://github.com/` / `git@github.com:` prefix and any `.git` suffix → `owner/repo`. Recorded per-package in the manifest as **provenance only** — it plays no part in naming or grouping the skill (one prefix can span several source repos).

3. **Auto-detect the `.Abstractions` companion.** If `nuget/.packages/<id-lowercase>.abstractions/` exists after the restore (restore pulls transitive deps into the same cache), ingest it in this same run at the resolved version — its own decompile and fragment passes, but folded into the primary package's single assembled file. Only the literal `.Abstractions` suffix qualifies; ignore `.Client`, `.Core`, etc.

3a. **Derive the grouping prefix(es).** If the `prefix` argument was supplied, split it on commas and use those values verbatim (each trimmed) — this is the deliberate-merge escape hatch (e.g. folding a `Contoso.Infrastructure.*` package into a skill that also covers `Contoso.Infra.*`). Otherwise auto-detect one prefix from the primary PackageId: strip a trailing `.Abstractions`, then drop the last dot-segment (`Contoso.Infrastructure.Configuration` → `Contoso.Infrastructure`; `Contoso.Infra.Utils` → `Contoso.Infra`). Guard: if the id has only 2 segments, don't drop — use it as-is (never collapse to a single bare word). This prefix (or list of prefixes) is the skill's grouping identity for step 8 onward, replacing the old repository-based slug.

4. **Pick the best-TFM DLL** per package: under `$pkgdir/lib/`, the highest applicable TFM present (prefer `net6.0`+ / newest `netstandard2.x` over `net4x`) → `<tfm>/<Id>.dll`.

5. **Decompile — only if not already decompiled.**
   ```bash
   src="nuget/.packages/.documented/<Id>/<version>/src"
   if [ -n "$(find "$src" -name '*.cs' -print -quit 2>/dev/null)" ] && [ "$force" != decompile ] && [ "$force" != all ]; then
     echo "Reusing existing decompilation at $src"
   else
     rm -rf "$src"
     ilspycmd -p -o "$src" "<resolved dll path>"
   fi
   ```
   Reuse is the default because a decompile of a fixed `<Id>@<version>` is deterministic. `nuget/.packages/` is gitignored; the `.csproj`/`Properties/AssemblyInfo.cs` scaffolding exists only so `ilspycmd -p` can run and is never rendered or committed. Nothing in this workflow ever writes into the decompiled tree.

6. **Build the worklist** per package: every decompiled `.cs` file except `Properties/AssemblyInfo.cs`, recording its `public`/`protected`/`protected internal` types and members (interfaces, abstract classes, enums, extension methods, properties, generics). This per-file member list is both the subagent's assignment and the fidelity checklist in step 9 — keep it.

   Each file's output is a Markdown **fragment** cached at `nuget/.packages/.documented/<Id>/<version>/api/<relative-cs-path>.md`. **Skip any file whose fragment already exists** — it was generated by a prior run — unless `force` is `describe` or `all`. A file with no public/protected members produces no fragment; record it as skipped.

7. **Fan out to subagents — one file each, at most 3 concurrent across both packages.** Use a file-editing agent (it writes the fragment), but the decompiled `.cs` is **read-only input — never edit it**. Give each: the source file path, its public/protected worklist, the fragment output path, the PackageId/version, and all user-supplied repository paths. Instruct it to, for that file only:
   - Search the given paths for real call sites, DI registrations, implementations, and pre-existing contract comments on consuming/wrapper types.
   - Write exactly one file — the fragment — containing a `##` heading holding the source file's path relative to its `src/` root, followed by a single ```` ```csharp ```` block, and nothing else.
   - In that block: keep the namespace, type declarations, base lists, and generic constraints; reduce every public/protected member to its declaration signature terminated by `;`, **copied verbatim from the source** — never retyped from memory, never altered, never invented.
   - Drop `using` directives, method/property bodies, every private member (fields, methods, nested types) — not even as stubs — plus `//IL_...` comments, decompiler casts (e.g. `(IWidgetRestClient)(object)this`), and constructor initializers (`: base(...)`, `: this(...)`).
   - Fully qualify a type in a `cref`/`paramref`/prose only where dropping the `using` made it ambiguous.
   - Above every kept declaration write XML doc comments — `<summary>`, `<param>` each, `<returns>` when non-void, `<exception>` per distinct thrown/propagated type, `<remarks>` only for non-obvious constraints — shaped per `references/documentation-template.md` under this skill's base directory.
   - Cover contract, observable behavior, semantics, constraints, nullability, exceptions, cancellation, side effects, extension points. Omit implementation details, redundant restatements, incidental exceptions.
   - Front-load `<summary>` with one terse plain-language clause of *what the member does* — bodies never reach the fragment, so `<summary>` is the only surviving behavioral description. Contract-only restatements are insufficient; implementation walkthroughs are too much.
   - `<inheritdoc/>` alone for an override/implementation that adds nothing to its base or interface member.
   - No evidence found → still write a best-effort `<summary>` from name and signature, plus `<remarks>_No usage evidence found in the given repository path(s)._</remarks>`. Never present inference as fact.
   - Report back: fragment path, members emitted, evidence cited (path + file/symbol), no-evidence fallbacks.

8. **Locate or scaffold the target skill.** First recursively search `<reporoot>` for every existing `search-nuget-*/manifest.json` — anywhere in the repo, not just under `.github/skills/` — for a `prefixes[]` entry matching (or, for the auto-detected case, matching by dot-segment) this package's derived prefix — reuse that skill's own folder (wherever it was found) if a match exists, since its folder name doesn't have to equal the slugified prefix (a skill can cover multiple prefixes). Only if no existing skill anywhere under `<reporoot>` covers the prefix, scaffold a new one under `<reporoot>/.github/skills/`: slug = the (first, if several) prefix lowercased and hyphenated (`Contoso.Infrastructure` → `contoso-infrastructure`) → `<reporoot>/.github/skills/search-nuget-<slug>/`, created from `references/skill-bootstrap-template.md` under this skill's base directory. The `.Abstractions` companion always shares whichever skill its primary package resolved to.

9. **Verify and assemble — mechanical, no authoring.** The orchestrator writes no prose and rewrites no signature; it only checks fragments and concatenates them.
   - Check each fragment against its step-6 worklist: every listed member present exactly once, nothing extra. Reject a fragment that contains a `//IL_` comment, a `using ` directive, a `private ` declaration, or a member declaration not terminated by `;`.
   - On failure, re-dispatch that one file once with the specific defect named; if it still fails, leave the fragment out and report it.
   - Concatenate verbatim in stable path order: `# <Id> <version>` then the primary package's fragments. If a companion was ingested, append `# <Id>.Abstractions <version>` and its fragments — same file, never a separate one.
   - Write to `<target-skill-dir>/references/<Id>.<version>.md` — `<target-skill-dir>` being the skill folder located or scaffolded in step 8, wherever it lives under `<reporoot>` — (named after the primary package; flat, no subfolders), replacing any existing file for that exact id/version. This file **is** committed, is fully regenerated each run, and is never hand-edited or diffed.

10. **Update `manifest.json` and `SKILL.md` — orchestrator only, never a subagent** (they share one skill folder; concurrent edits race):
    - `manifest.json`: ensure `prefixes[]` includes this run's prefix(es) (union, no duplicates). Add or union-merge a `packages[]` entry `{ "id", "versions": ["<version>"], "skip": false, "repository": "<owner/repo or null>" }` per package, the companion included as its own entry — `repository` is per-package provenance, never a grouping key. Add/update one `codebases[]` entry per supplied path (`{ "name": "<slug>", "path", "patterns": [...] }`), deduplicated by path; `patterns` holds every exact `<Id>`/`<Id>.Abstractions` plus one `<prefix>.*` wildcard per covered prefix (added once, not per package).
    - `SKILL.md`: description names every covered prefix as an explicit wildcard (e.g. `` `Contoso.Infrastructure.*` ``) so routing isn't misled by the skill's own name. Add or refresh a "Covered packages" row per package. Both the primary and its companion point at the same `references/<Id>.<version>.md`, making the grouping visible.

11. **Report**: packages decompiled vs. reused, skill created vs. updated, manifest/SKILL paths, fragments generated vs. reused vs. skipped (no public members), members documented, fragments re-dispatched or dropped by the step-9 check, evidence sources, no-evidence fallbacks.

## Notes

- Read-only output: not source-linked, not buildable, not a package replacement.
- The decompiled tree is never written to — documentation lives only in the fragment cache and the committed `.md`.
- Reuse is the default at every cached layer (restore, decompile, fragments); `force` is the only way to redo work. The committed `.md` is the one exception — always reassembled from the current fragments.
- One skill per **package-name prefix (family)**, not per source repository or per package: repeated ingestions whose prefix resolves to the same skill (auto-detected or via an explicit `prefix` override) accumulate into the same folder, `manifest.json`, and `SKILL.md`. Repository is recorded for provenance only and never decides grouping — a single skill can legitimately span several source repos.
- The only thing written under `nuget/` is the gitignored `nuget/.packages/` restore, decompile, and fragment cache.
- On-demand only. The `.Abstractions` auto-inclusion in step 3 is the sole action that doesn't need its own ask.
