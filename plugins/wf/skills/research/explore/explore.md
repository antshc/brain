# Explore

Explore procedure of the Research skill. Runs inside a caller-spawned `hunter` agent; never spawns subagents. Owns target resolution, contract material, and route selection; `hunter` owns the read-only contract, tool rules, and Graphify use. The caller owns delegation: it reads the Research skill's Explore request, forms the request, decides one or parallel subagents, and spawns them per that request's agent rule.

## Contents

- Run caller-supplied work
- Read-only contract
- Resolve the repository root
- Resolve the target
- Routing rules
- Return the verdict
- Gotchas

## Run caller-supplied work

The caller owns what the exploration produces — a named skill owns its own procedure, evidence rules, and return shape; a prompt instruction owns its own task and output. Run it under the read-only contract, resolved target, and routing rules below. Return `@outputShape` unaltered rather than folding it into a verdict.

## Read-only contract

`hunter`'s read-only contract applies. Explore adds one exception: the NuGet tactic may install `ilspycmd` per-user and persist decompiled files solely in the resolved NuGet package cache.

## Resolve the repository root

Set `@repoRoot` to the output of `git rev-parse --show-toplevel`, run once from the agent session's launch folder, not the current CWD; stop if the launch folder is not inside a Git repository. Resolve every harness path below from `@repoRoot`. **MUST NOT** re-resolve `@repoRoot` from a git worktree or nested repo (e.g. code repo under `workspace/`) after a `cd`; those are checkouts to search, not the harness root.

Every harness-side search is bounded to `@repoRoot`, never above it. A supporting repository the index names is searched inside its own path, however far outside the harness that sits — never by widening the harness search.

## Resolve the target

Preserve every repository or service name in the question.

**Building-block index** — MUST use for the navigation, and the only map of the supporting repositories: they sit outside the harness, at paths nothing on disk advertises. Read `@repoRoot/ARCHITECTURE.md`'s `Deployables` table before declaring a target unresolved; a matching row's `Location` cell maps a Deployable name — or its Trigger condition — to a local path (`workspace/<repo>[/subpath]` or absolute) and an `origin` URL. Consult the `Shared dependency ownership` table the same way for a dependency more than one Deployable uses, and the `Terminal infrastructure boundaries` table for where tracing stops. This is the only reader of those tables — never search the filesystem for a fallback index file. A path a row names but the disk lacks is unresolved, not a licence to guess a neighbouring one.

**Enumerate the checkouts** — once per exploration, before any lookup. Three sources: `@repoRoot` itself for documentation, the main codebase repository under `@repoRoot/workspace/`, and every local path the `Deployables` or `Shared dependency ownership` table gives a supporting repository. Build a `<name> → <absolute path>` list of those that exist on disk. A name the list has no path for routes to the GitHub tools.

**Graph coverage** — read `graphify-out/manifest.json` under each enumerated checkout, where present. These are graphs over one multi-repo codebase, not a preference order: pick the graph whose `manifest.json` has a key starting with the target checkout's path relative to that graph's root (e.g. `workspace/<repo>/`); several naming it are one codebase seen from different cuts — take the widest. Settle exactly one graph, or none.

Report a name that resolves to neither a local checkout nor a GitHub repository as unresolved.

## Routing rules

### Contracts first

Before source, read the contract material for the resolved target, nearest owner first. `GLOSSARY.md` carries terminology; `ARCHITECTURE.md`, `DEPLOYMENT.md`, and `README.md` carry ownership and runtime boundaries; `*.swagger.json` carries REST contracts; `*.configuration-tweaks.md` carries configuration surfaces.

1. The target checkout's own copies of those files.
2. The `@repoRoot` document whose folder or filename names that target — a `@repoRoot/**/` glob returns one set per documented service, so match on the name rather than reading them all.
3. `@repoRoot`'s root-level copies, for terminology and boundaries spanning services.

Each level supersedes the one below it for claims about that target. A question spanning deployables reads level 3 plus levels 1-2 of every involved target, and names the contract behind each claim.

### Route the lookup

Before the first search, print one line: `route: rg | lsp | graphify | github | nuget — {{reason}}`. `@shape` decides when given; else the first matching row.

| Signal in `@work` | Route |
|---|---|
| target has no local checkout | `github`; package cache cannot be inferred from remote source |
| `@shape: nuget`; restored NuGet package, its API, or behavior | `nuget` — NuGet tactic |
| `@shape: literal`; quoted literal, config key, error text, route path, test name, file glob | `rg` |
| `@shape: symbol`; exact type or member name, asking definition, references, implementations, callers | `lsp`, then `rg` |
| `@shape: relationship`; names unknown, "how do … connect", "which modules", "end to end", "flow", "impact", "blast radius", "across A and B", architecture, doc↔code | `graphify` when Graph coverage selected a graph, else `rg` on `GLOSSARY.md` terms |

`@depth: medium | thorough` with no literal or symbol in `@work` → relationship row.

**Tactics.** For `nuget`, load the NuGet tactic (listed in the Research skill's Entry routes) in full and follow its procedure and evidence checks. For other routes, use Select tools by question shape. If a C# type/member has no definition in the target source after `lsp`/`rg -uu`, switch to `nuget` and read that tactic; an unknown package ID is a valid entry state. Report the final route in the verdict.

### Select tools by question shape

**Local checkout** — `hunter`'s Tools and Graphify rules. Graph coverage selected a graph → pass it to Graphify; none → never re-scan for a manifest Graph coverage already ruled out. For a C# type absent from local source, follow the NuGet tactic rather than broadening the search across the disk.

**No local checkout**

- Use the read-only `github` Repository tactic. Scope searches to the supplied repository or use the integration for authorized organization-wide discovery. Verify decisive source at a pinned commit.
- GitHub search reflects indexed branches and can be stale; carry that branch uncertainty into the verdict.

## Return the verdict

Default `@outputShape`: first line repeats the `route:` line; then one concise verdict with target-relative files, relevant symbols, evidence, and unresolved uncertainty. Nothing found after the `rg -uu` recheck → verdict is exactly `NOT FOUND` plus the searched roots.

## Gotchas

- CWD drifts after `cd` into a worktree or nested repo; `git rev-parse --show-toplevel` there returns that sub repo, hiding launch-folder `ARCHITECTURE.md`, contracts, and the `Deployables` index. Keep the launch-folder `@repoRoot`.
- NuGet inspection is a Research tactic; route it when evidence requires it, never wait for the caller to name it in `@work`.
