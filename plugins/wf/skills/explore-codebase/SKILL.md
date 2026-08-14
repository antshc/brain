---
name: explore-codebase
description: Delegate read-only codebase questions to a general-purpose subagent and route its lookup by target and question shape. Use when a caller needs architecture, relationship, flow, symbol, reference, implementation, call, literal, configuration, error, test, ownership, or cross-layer evidence from the current or a named external codebase.
---

# Explore Codebase

Delegate every lookup through `runSubagent`; omit `agentName` so the general-purpose subagent inherits execution, skill, search, LSP, and read tools. The caller supplies the question and `quick | medium | thorough`. The call blocks until one verdict returns.

## Read-only contract

Tell the subagent that exploration is strictly read-only. It must not edit source, documentation, configuration, generated files, or `graphify-out/`.

## Resolve the target

Preserve every repository or service name in the question. When the question names an external codebase and a matching installed `search-*` local lookup skill exists, Follow `/{{matchingSearchSkill}}` skill first to resolve its checkout. If no matching skill resolves the named codebase, report it as unresolved; never guess a path.

## Select tools by question shape

- Existing `graphify-out/graph.json` and a usable Graphify CLI are optional. Use `graphify query` for broad architecture or relationship questions, `graphify path` for an A-to-B connection or flow, and `graphify explain` for one graph concept.
- Graphify stays read-only. Never build or update a missing graph, install Graphify, or run reflection, vocabulary-sidecar, `save-result`, add, watch, export, feedback, or any other write-producing operation. If the graph, command, or answer is unavailable or unhelpful, continue with normal exploration.
- Use LSP definitions, references, implementations, and call hierarchy for known symbols.
- Use exact grep for literals, configuration, errors, and test names.
- Use semantic search for fuzzy concepts or unknown ownership.
- Use targeted reads to verify final evidence.

## Return the verdict

Return one concise verdict with target-relative files, relevant symbols, evidence, and unresolved uncertainty. The caller retrieves exact quotations, signatures, and assertions directly; never re-read evidence already reported by the subagent.
