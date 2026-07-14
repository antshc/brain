---
name: 'lsp-navigation'
description: 'Navigate and inspect changed code with LSP tools at progressive depth before drawing review conclusions.'
---

# LSP Progressive Depth Code Analysis

Use this framework to inspect changed symbols before drawing review conclusions. Do not rely on the diff alone.

## Before exploring

Before exploring, confirm the project builds and check whether an LSP is available to assist exploration. Look at the Readme.md or ARCHITECTURE.md for build instructions. If the build fails, report this, fallback to other tools.

## Level 1 — Baseline (always required)

- `goToDefinition`: inspect declaration and contract
- `hover`: verify signature, type, generics, nullability, and modifiers
- `findReferences`: understand usage shape (do NOT inspect all references)

## Level 2 — Conditional (when behavior may be impacted)

- Inspect a **small set of representative callers** (3–5 max)
- `goToImplementation`: only when polymorphism or overrides are relevant
- Inspect key downstream dependencies if side effects are involved

## Level 3 — Deep analysis (only when evidence suggests risk, callable symbols only)

- `incomingCalls`: trace upstream callers when behavior change is significant
- `outgoingCalls`: trace downstream effects when correctness depends on it
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
