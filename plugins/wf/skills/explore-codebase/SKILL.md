---
name: explore-codebase
description: >-
  Look up codebase symbols, callers, flows, literals, and restored NuGet package APIs inline, read-only in a caller-spawned subagent. Use for 'where is', 'what calls', an unknown C# type, or a Request with @work and @depth. Not for saved cited documents → `research`.
---

# Explore Codebase

Runs inside a caller-spawned subagent; never spawns subagents. Owns target resolution, contract material, tool selection, and the read-only contract. The caller owns delegation: it reads Request, forms the request, decides one or parallel subagents, and spawns them. Skill unavailable → caller spawns the explore agent with the same request plus the read-only contract.

## Request

Caller forms before spawning; the subagent receives it verbatim:

- `@work` — one of: question | prompt instruction | skill name to run. Instruction and skill name pass **verbatim**, never paraphrased.
- `@depth` — `quick | medium | thorough`.
- `[@shape]` — `literal | symbol | relationship | nuget`; routing hint. Omitted → classify in Route the lookup.
- `[@target]` — repository or service names as stated; omitted → current repository.
- `@outputShape` — caller's return shape; omitted → Return the verdict.
- `[@outputArtifact]` — the one file the run may write.
- `[@inputs]` — caller-supplied inputs `@work` needs.

## Run caller-supplied work

The caller owns what the exploration produces — a named skill owns its own procedure, evidence rules, and return shape; a prompt instruction owns its own task and output. Run it under the read-only contract, resolved target, and routing rules below. Return `@outputShape` unaltered rather than folding it into a verdict.

## Read-only contract

Exploration is strictly read-only. Do not edit source, documentation, configuration, generated files, `@repoRoot/graphify-out/`, or any target-repo `graphify-out/`.

Exceptions: write `@outputArtifact` and nothing else in the repository; install `rg` per-user when missing (see Select tools by question shape); `graphify query`/`path`/`explain` updating `graphify-out/cache/`; NuGet tactic may install `ilspycmd` per-user and persist decompiled files solely in the resolved NuGet package cache.

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
| `@shape: nuget`; restored NuGet package, its API, or behavior | `nuget` — [NuGet tactic](nuget.md) |
| `@shape: literal`; quoted literal, config key, error text, route path, test name, file glob | `rg` |
| `@shape: symbol`; exact type or member name, asking definition, references, implementations, callers | `lsp`, then `rg` |
| `@shape: relationship`; names unknown, "how do … connect", "which modules", "end to end", "flow", "impact", "blast radius", "across A and B", architecture, doc↔code | `graphify` when Graph coverage selected a graph, else `rg` on `GLOSSARY.md` terms |

`@depth: medium | thorough` with no literal or symbol in `@work` → relationship row.

**Tactics.** For `nuget`, read [NuGet source inspection](nuget.md) in full and follow its procedure and evidence checks. For other routes, use the local/GitHub/Graphify instructions below. If a C# type/member has no definition in the target source after `lsp`/`rg -uu`, switch to `nuget` and read that tactic; an unknown package ID is a valid entry state. Report the final route in the verdict.

### Select tools by question shape

**Local checkout**

- Use LSP definitions, references, implementations, and call hierarchy for known symbols.
- Exact search is rg-backed only: the harness search tool (`grep`, `rg`, or `glob`, by host) or shell `rg` (`-t <lang>`/`-g <glob>` to narrow). **MUST NOT** run recursive `grep` (`-r`, `-R`, `find -exec grep`, `xargs grep`) or chain `rg … || grep …`; `grep` filtering rg output through a pipe is fine. Holds after loading any other skill; its shell snippets do not relax it.
- `rg` exit codes: `0` match, `1` no match (a result, not a missing binary), `2` error. Only `command -v rg` decides presence.
- `command -v rg` empty, and only then → install it once per-user, no sudo: fetch the latest `BurntSushi/ripgrep` release asset for the platform (`x86_64-unknown-linux-musl`, `aarch64-unknown-linux-gnu`, `<arch>-apple-darwin` `.tar.gz`; `x86_64-pc-windows-msvc` `.zip`), verify it against its `.sha256` asset, extract only the `rg` binary to `~/.local/bin/` (Windows: `%LOCALAPPDATA%\Programs\ripgrep\`), and run it by absolute path if that folder is not on `PATH`. Checksum mismatch, no network, or any failure → `grep -r` is the fallback; never use sudo or a system package manager.
- Use semantic search for fuzzy concepts or unknown ownership.
- Use targeted reads to verify final evidence.
- For a C# type absent from local source, follow the [NuGet tactic](nuget.md) rather than broadening the search across the disk.

**No local checkout**

- Use the read-only `github` Repository tactic. Scope searches to the supplied repository or use the integration for authorized organization-wide discovery. Verify decisive source at a pinned commit.
- GitHub search reflects indexed branches and can be stale; carry that branch uncertainty into the verdict.

**Graphify** — local checkouts only: the target checkout itself, plus any other deployable or supporting repository that is checked out locally. A target with no local checkout stays on the GitHub tools.

- MUST use when Graph coverage selected a graph **and** the answer depends on relationships rather than one known item: architecture/orientation, multi-hop or cross-module/cross-repo flow, impact/blast radius, concept→code mapping with unknown names, doc↔code links, or narrowing a large search space. Known symbol, literal, config, test, or single-file lookups go straight to LSP/grep.
- Graph selected → **MUST** *load `graphify` skill first for graph query, path, explain, health preflight, and knowledge-graph routing*. Its routing rules supersede the defaults below; the read-only contract supersedes its write steps:

  | graphify step | Under explore-codebase |
  |---|---|
  | `graphify reflect --if-stale` | skip; read `graphify-out/reflections/LESSONS.md` if present |
  | query vocabulary file (`.vocab.txt`) | build in memory or print to stdout; never write |
  | `save-result`, `--update`, add, watch, export, feedback, rebuild | never |
  | `graphify query`/`path`/`explain` updating `graphify-out/cache/` | allowed; the only tolerated `graphify-out/` write |

- `graphify` on `PATH` → query through `graphify query | path | explain`; inline `graph.json` traversal only when the CLI is missing.
- `graphify` skill unavailable → `graphify query` for broad architecture or relationship questions, `graphify path` for an A-to-B connection or flow, `graphify explain` for one graph concept.
- No graph covers the target → continue with normal exploration; never re-scan for a manifest Graph coverage already ruled out.
- Graph narrows and orients; LSP/grep locate; source proves. A missing Graphify node is never evidence of absence; settle decisive behavior and absence claims in source. Code changed after the graph build → trust source.
- Read-only either way: the read-only contract overrides the `graphify` skill. Never build or update a graph, install Graphify, or run reflection, vocabulary-sidecar, `save-result`, add, watch, export, feedback, or any other write-producing operation. Graph, skill, or answer unavailable or unhelpful → continue with normal exploration.

## Return the verdict

Default `@outputShape`: first line repeats the `route:` line; then one concise verdict with target-relative files, relevant symbols, evidence, and unresolved uncertainty. Nothing found after the `rg -uu` recheck → verdict is exactly `NOT FOUND` plus the searched roots.

## Gotchas

- CWD drifts after `cd` into a worktree or nested repo; `git rev-parse --show-toplevel` there returns that sub repo, hiding launch-folder `ARCHITECTURE.md`, contracts, and the `Deployables` index. Keep the launch-folder `@repoRoot`.
- `graphify` is a tool skill; NuGet inspection is a local tactic. Route both when evidence requires them; never wait for the caller to name them in `@work`.
- grep tool and `rg` skip gitignored and hidden files (generated code, build output, `graphify-out/`, vendored folders). Before claiming something is absent, re-search with `rg -uu` or confirm the path is not ignored.
