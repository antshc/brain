---
name: explore-codebase
description: Finds code — where a symbol lives, what calls it, how a flow works, which file holds a literal, config, test, or owner — by delegating read-only lookups to subagents. The engine for any codebase exploration: the caller supplies a question, its own prompt instruction, or a skill to run inside the subagent. Use for any "where is", "what calls", "how does this work", or "find the code that..." question about the current repo or a named external codebase, and whenever a task must locate code before it can proceed.
---

# Explore Codebase

Delegate every lookup through `runSubagent`; omit `agentName` so the general-purpose subagent inherits execution, skill, search, LSP, and read tools. The caller supplies `quick | medium | thorough` plus the work itself — a question, a prompt instruction of its own, or a skill to run. This skill owns the delegation, the target, and the contract whichever form arrives.

## Choose delegation shape

- Use one subagent for a focused question with one likely evidence path.
- Spawn multiple independent subagents in parallel when the question has distinct, non-overlapping exploration tracks, such as separate services, symbol and configuration evidence, or architecture and test coverage. Give each agent a bounded subquestion and the same read-only contract.
- Do not split a question when one agent must discover the answer before another can proceed; make that dependency sequential.
- Consolidate all agent results into one concise verdict, resolve conflicts with targeted evidence, and state any remaining uncertainty.

## Run caller-supplied work inside the subagent

Beyond a plain question, a caller may hand over a prompt instruction to carry out, or name a skill for the subagent to run. Either way the caller owns what the exploration produces — a named skill owns its own procedure, evidence rules, and return shape; a prompt instruction owns its own task and output.

Pass the instruction or skill name through **verbatim**, never paraphrased, and put into the brief the caller-supplied inputs, the read-only contract, the resolved target, and the routing rules below — the subagent reads none of this file on its own. Return the caller's own output shape unaltered rather than folding it into a verdict.

## Read-only contract

Tell the subagent that exploration is strictly read-only. It must not edit source, documentation, configuration, generated files, `$HARNESS_REPO_PATH/graphify-out/`, or any target-repo `graphify-out/`.

The one exception is an output artifact the caller names — the subagent writes that file, and nothing else.

## Resolve the harness

Run `/resolve-harness` skill to get `HARNESS_REPO_PATH` (cwd fallback when the skill is unavailable or the value is empty). Resolve it once and put the absolute path in every subagent brief — the subagent never re-resolves it.

Every harness-side search is bounded to `$HARNESS_REPO_PATH`, never above it. A supporting repository the index names is searched inside its own path, however far outside the harness that sits — never by widening the harness search.

## Resolve the target

Preserve every repository or service name in the question.

**Codebase index** — MUST use for the navigation, and the only map of the supporting repositories: they sit outside the harness, at paths nothing on disk advertises. Search `$HARNESS_REPO_PATH/**/*-codebase-index.md` before declaring a target unresolved; a hit maps a deployable, service, or repository name — or one of its trigger signals — to a local path, a GitHub repository URL, a package owner, or a terminal boundary where tracing stops. No index file is not a gap: the harness and its main repository still resolve, and every other named target is remote. A path the index names but the disk lacks is unresolved, not a licence to guess a neighbouring one.

**Enumerate the checkouts** — once per exploration, before any lookup. Three sources: `$HARNESS_REPO_PATH` itself for documentation, the main codebase repository under `$HARNESS_REPO_PATH/workspace/`, and every local path the index gives a supporting repository. Build a `<name> → <absolute path>` list of those that exist on disk and put it in every subagent brief — the subagent never re-enumerates. A name the list has no path for routes to the GitHub tools.

**Graph coverage** — read `graphify-out/manifest.json` under each enumerated checkout, where present. These are graphs over one multi-repo codebase, not a preference order: pick the graph whose manifest names the resolved target; several naming it are one codebase seen from different cuts — take the widest. Emit exactly one value into every brief, `GRAPH_PATH=<absolute path>` or `GRAPH=none`, so parallel subagents query the same graph.

Report a name that resolves to neither a local checkout nor a GitHub repository as unresolved.

## Routing rules

### Contracts first

Before source, read the contract material for the resolved target, nearest owner first. `CONTEXT.md` carries terminology; `ARCHITECTURE.md`, `DEPLOYMENT.md`, and `README.md` carry ownership and runtime boundaries; `*.swagger.json` carries REST contracts; `*.configuration-tweaks.md` carries configuration surfaces.

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

- MUST use when the brief carries a `GRAPH_PATH` **and** the question is one a graph answers — architecture, relationships, an A-to-B connection or flow. A symbol, literal, config, or test lookup goes straight to LSP and grep.
- `GRAPH=none` means no graph covers the target — continue with normal exploration; never re-scan for a manifest the resolution step already ruled out.
- On a `GRAPH_PATH` and a matching question, query that graph before LSP, grep, or semantic search: `graphify query` for broad architecture or relationship questions, `graphify path` for an A-to-B connection or flow, and `graphify explain` for one graph concept. A missing Graphify node is never evidence of absence — settle decisive behavior and absence claims in source.
- Graphify stays read-only. Never build or update a missing graph, install Graphify, or run reflection, vocabulary-sidecar, `save-result`, add, watch, export, feedback, or any other write-producing operation. If the graph, command, or answer is unavailable or unhelpful, continue with normal exploration.

## Return the verdict

Return one concise verdict with target-relative files, relevant symbols, evidence, and unresolved uncertainty. The caller retrieves exact quotations, signatures, and assertions directly; never re-read evidence already reported by the subagent.
