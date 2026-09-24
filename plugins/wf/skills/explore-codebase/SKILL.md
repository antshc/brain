---
name: explore-codebase
description: Finds code — where a symbol lives, what calls it, how a flow works, which file holds a literal, config, test, or owner — by delegating read-only lookups to subagents. Use for any "where is", "what calls", "how does this work", or "find the code that..." question about the current repo or a named external codebase, and whenever a task must locate code before it can proceed.
---

# Explore Codebase

Delegate every lookup through `runSubagent`; omit `agentName` so the general-purpose subagent inherits execution, skill, search, LSP, and read tools. The caller supplies the question and `quick | medium | thorough`.

## Choose delegation shape

- Use one subagent for a focused question with one likely evidence path.
- Spawn multiple independent subagents in parallel when the question has distinct, non-overlapping exploration tracks, such as separate services, symbol and configuration evidence, or architecture and test coverage. Give each agent a bounded subquestion and the same read-only contract.
- Do not split a question when one agent must discover the answer before another can proceed; make that dependency sequential.
- Consolidate all agent results into one concise verdict, resolve conflicts with targeted evidence, and state any remaining uncertainty.

## Read-only contract

Tell the subagent that exploration is strictly read-only. It must not edit source, documentation, configuration, generated files, or `graphify-out/`.

## Resolve the target

Preserve every repository or service name in the question.

**Codebase index** — optional navigation aid, never a source of truth. Glob for `**/*-codebase-index.md` before declaring a target unresolved; a hit maps a deployable, service, or repository name — or one of its trigger signals — to a local path, a GitHub repository URL, a package owner, or a terminal boundary where tracing stops. No index file is not a gap: resolve against the workspace folders instead. A path the index names but the disk lacks is unresolved, not a licence to guess a neighbouring one.

Report a name that resolves to neither a local checkout nor a GitHub repository as unresolved.

## Routing rules

### Contracts first

Before source, read the matching material in the target repository:

- `CONTEXT.md` for terminology.
- `ARCHITECTURE.md` and `DEPLOYMENT.md` for ownership and runtime boundaries.
- `docs/**/*.md` for service ownership and already-researched flows.
- `**/*.swagger.json` for REST contracts.
- `**/*.configuration-tweaks.md` for configuration surfaces.

### Select tools by question shape

**Local checkout**

- Use LSP definitions, references, implementations, and call hierarchy for known symbols.
- Use exact grep for literals, configuration, errors, and test names.
- Use semantic search for fuzzy concepts or unknown ownership.
- Use targeted reads to verify final evidence.
- For a C# type absent from local source, Run `/inspect-nuget-source` skill rather than broadening the search across the disk.
- Existing `graphify-out/graph.json` and a usable Graphify CLI are optional. Inspect `graphify-out/manifest.json` first and query only the repositories it represents; use `graphify query` for broad architecture or relationship questions, `graphify path` for an A-to-B connection or flow, and `graphify explain` for one graph concept. A missing Graphify node is never evidence of absence — settle decisive behavior and absence claims in source.
- Graphify stays read-only. Never build or update a missing graph, install Graphify, or run reflection, vocabulary-sidecar, `save-result`, add, watch, export, feedback, or any other write-producing operation. If the graph, command, or answer is unavailable or unhelpful, continue with normal exploration.

**No local checkout**

- Load the deferred GitHub tools before use.
- Use `github_repo` for behavior or architecture in one known repository.
- Use `github_text_search` for exact symbols, package IDs, image names, or organization-wide ownership discovery.
- GitHub search reflects indexed branches and can be stale; carry that branch uncertainty into the verdict.

## Return the verdict

Return one concise verdict with target-relative files, relevant symbols, evidence, and unresolved uncertainty. The caller retrieves exact quotations, signatures, and assertions directly; never re-read evidence already reported by the subagent.
