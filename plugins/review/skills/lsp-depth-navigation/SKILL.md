---
name: 'lsp-depth-navigation'
description: 'Navigate and inspect changed code with LSP tools at progressive depth before drawing review conclusions.'
---

# LSP Progressive Depth Code Analysis

Use this framework to inspect changed symbols before drawing review conclusions. Do not rely on the diff alone.

## Before exploring

Before exploring, confirm the project builds and check whether an LSP is available to assist exploration. Look at the Readme.md or ARCHITECTURE.md for build instructions. If the build fails, report this, fallback to other tools.

## Level 1 — Baseline (always required)

- List all symbols in a file (`documentSymbol`): get an overview of a file's structure before diving in
- Search symbols by name across the workspace (`workspaceSymbol`): locate a symbol when its file location is unknown
- Find where a symbol is defined (`goToDefinition`): inspect declaration and contract
- Get type info and documentation for a symbol (`hover`): verify signature, type, generics, nullability, and modifiers
- Find all usages of a symbol (`findReferences`): understand usage shape (do NOT inspect all references)

## Level 2 — Conditional (when behavior may be impacted)

- Inspect a **small set of representative callers** (3–5 max)
- Find implementations of an interface/abstract type (`goToImplementation`): only when polymorphism or overrides are relevant
- Inspect key downstream dependencies if side effects are involved

## Level 3 — Deep analysis (only when evidence suggests risk, callable symbols only)

- Find what calls a given function (`incomingCalls`): trace upstream callers when behavior change is significant
- Find what a given function calls (`outgoingCalls`): trace downstream effects when correctness depends on it
- Do NOT automatically expand full call chains; prefer representative and high-risk paths first
- Use only when needed to understand behavior changes, side effects, or contract impact

Do NOT exhaustively inspect all references or implementations if usage is repetitive or low-signal.

## LSP Efficiency Rules (Context Control)

- Do NOT read all references if they are numerous and repetitive
- Do NOT expand the entire call graph without a clear hypothesis
- Prefer representative sampling over exhaustive inspection
- Stop LSP exploration once the impact is clearly understood
- Focus on high-risk areas:
  - API boundaries
  - shared services
  - async flows
  - error handling paths
