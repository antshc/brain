---
name: explore-codebase
description: Finds code (where a symbol lives, what calls it, how a flow works, which file holds a literal, config, test, or owner) as a read-only lookup run inside a caller-spawned subagent. The engine for any codebase exploration; the caller reads its Request, forms a question, prompt instruction, or skill to run plus output shape, and spawns the subagent. Use for any "where is", "what calls", "how does this work", or "find the code that..." question about the current repo or a named external codebase, and whenever a task must locate code before it can proceed.
---

# Explore Codebase

Runs inside a caller-spawned subagent; never spawns subagents. Owns target resolution, contract material, tool selection, and the read-only contract. The caller owns delegation: it reads Request, forms the request, decides one or parallel subagents, and spawns them. Skill unavailable → caller spawns the explore agent with the same request plus the read-only contract.

## Request

Caller forms before spawning; the subagent receives it verbatim:

- `@work` — one of: question | prompt instruction | skill name to run. Instruction and skill name pass **verbatim**, never paraphrased.
- `@depth` — `quick | medium | thorough`.
- `[@target]` — repository or service names as stated; omitted → current repository.
- `@outputShape` — caller's return shape; omitted → Return the verdict.
- `[@outputArtifact]` — the one file the run may write.
- `[@inputs]` — caller-supplied inputs `@work` needs.

## Run caller-supplied work

The caller owns what the exploration produces — a named skill owns its own procedure, evidence rules, and return shape; a prompt instruction owns its own task and output. Run it under the read-only contract, resolved target, and routing rules below. Return `@outputShape` unaltered rather than folding it into a verdict.

## Read-only contract

Exploration is strictly read-only. Do not edit source, documentation, configuration, generated files, `$HARNESS_REPO_PATH/graphify-out/`, or any target-repo `graphify-out/`.

The one exception is `@outputArtifact` — write that file, and nothing else.

## Resolve the repository root

Resolve `HARNESS_REPO_PATH` once with `git rev-parse --show-toplevel`; stop if cwd is not inside a Git repository.

Every harness-side search is bounded to `$HARNESS_REPO_PATH`, never above it. A supporting repository the index names is searched inside its own path, however far outside the harness that sits — never by widening the harness search.

## Resolve the target

Preserve every repository or service name in the question.

**Building-block index** — MUST use for the navigation, and the only map of the supporting repositories: they sit outside the harness, at paths nothing on disk advertises. Read `$HARNESS_REPO_PATH/ARCHITECTURE.md`'s `Deployables` table before declaring a target unresolved; a matching row's `Location` cell maps a Deployable name — or its Trigger condition — to a local path (`workspace/<repo>[/subpath]` or absolute) and an `origin` URL. Consult the `Shared dependency ownership` table the same way for a dependency more than one Deployable uses, and the `Terminal infrastructure boundaries` table for where tracing stops. This is the only reader of those tables — never search the filesystem for a fallback index file. A path a row names but the disk lacks is unresolved, not a licence to guess a neighbouring one.

**Enumerate the checkouts** — once per exploration, before any lookup. Three sources: `$HARNESS_REPO_PATH` itself for documentation, the main codebase repository under `$HARNESS_REPO_PATH/workspace/`, and every local path the `Deployables` or `Shared dependency ownership` table gives a supporting repository. Build a `<name> → <absolute path>` list of those that exist on disk. A name the list has no path for routes to the GitHub tools.

**Graph coverage** — read `graphify-out/manifest.json` under each enumerated checkout, where present. These are graphs over one multi-repo codebase, not a preference order: pick the graph whose manifest names the resolved target; several naming it are one codebase seen from different cuts — take the widest. Settle exactly one value, `GRAPH_PATH=<absolute path>` or `GRAPH=none`.

Report a name that resolves to neither a local checkout nor a GitHub repository as unresolved.

## Routing rules

### Contracts first

Before source, read the contract material for the resolved target, nearest owner first. `GLOSSARY.md` carries terminology; `ARCHITECTURE.md`, `DEPLOYMENT.md`, and `README.md` carry ownership and runtime boundaries; `*.swagger.json` carries REST contracts; `*.configuration-tweaks.md` carries configuration surfaces.

1. The target checkout's own copies of those files.
2. The `$HARNESS_REPO_PATH` document whose folder or filename names that target — a `$HARNESS_REPO_PATH/**/` glob returns one set per documented service, so match on the name rather than reading them all.
3. `$HARNESS_REPO_PATH`'s root-level copies, for terminology and boundaries spanning services.

Each level supersedes the one below it for claims about that target. A question spanning deployables reads level 3 plus levels 1-2 of every involved target, and names the contract behind each claim.

### Select tools by question shape

**Local checkout**

- Use LSP definitions, references, implementations, and call hierarchy for known symbols.
- Use exact grep for literals, configuration, errors, and test names.
- Use semantic search for fuzzy concepts or unknown ownership.
- Use targeted reads to verify final evidence.
- For a C# type absent from local source, Run `/inspect-nuget-source` skill rather than broadening the search across the disk.

**No local checkout**

- Load the deferred GitHub tools before use.
- Use `github_repo` for behavior or architecture in one known repository.
- Use `github_text_search` for exact symbols, package IDs, image names, or organization-wide ownership discovery.
- GitHub search reflects indexed branches and can be stale; carry that branch uncertainty into the verdict.

**Graphify** — local checkouts only: the target checkout itself, plus any other deployable or supporting repository that is checked out locally. A target with no local checkout stays on the GitHub tools.

- MUST use when resolution settled a `GRAPH_PATH` **and** the question is one a graph answers — architecture, relationships, an A-to-B connection or flow. A symbol, literal, config, or test lookup goes straight to LSP and grep.
- `GRAPH=none` means no graph covers the target — continue with normal exploration; never re-scan for a manifest the resolution step already ruled out.
- On a `GRAPH_PATH` and a matching question, query that graph before LSP, grep, or semantic search: `graphify query` for broad architecture or relationship questions, `graphify path` for an A-to-B connection or flow, and `graphify explain` for one graph concept. A missing Graphify node is never evidence of absence — settle decisive behavior and absence claims in source.
- Graphify stays read-only. Never build or update a missing graph, install Graphify, or run reflection, vocabulary-sidecar, `save-result`, add, watch, export, feedback, or any other write-producing operation. If the graph, command, or answer is unavailable or unhelpful, continue with normal exploration.

## Return the verdict

Default `@outputShape`: one concise verdict with target-relative files, relevant symbols, evidence, and unresolved uncertainty.
