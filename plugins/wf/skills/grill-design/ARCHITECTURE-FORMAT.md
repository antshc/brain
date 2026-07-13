# ARCHITECTURE.md Format

`ARCHITECTURE.md` is the map of the system: how the codebase is organized, the layering it
follows, and the index of backbone Solution Strategy Records. It is the structural counterpart to
`CONTEXT.md` (which is the glossary). Keep it about *shape and rules*, not implementation
detail — the detail lives in the code and in the Solution Strategy Records it links to.

## Structure

```md
# {System Name} Architecture Overview

## Project Overview

{1-3 sentences: what the system is, the architectural style (e.g. modular monolith,
volatility-based layering), and the core stack.}

## Context

{Reference the `CONTEXT.md` file(s) that define the language of the system.}

## Solution Strategy

[Solution Strategy](https://docs.arc42.org/section-4/)

{The index of Solution Strategy Records (SSRs) — the backbone rules of the solution.
One row per SSR. The Summary cell must match the SSR's `**Summary:**` line verbatim. State
that this table is the index: scan it during design and modeling, and open the full record only when a decision is relevant to the work at hand. See [SSR-FORMAT.md](./SSR-FORMAT.md).}

| # | Decision | Summary |
|---|----------|---------|
| [{NNNN}](docs/ssr/{NNNN}-{slug}.md) | {Decision title} | {One- or two-sentence summary, copied from the SSR.} |


## Building blocks

[Building blocks](https://docs.arc42.org/section-5/)

### Codebase Structure

{The top-level folders and what each contains. One line per folder. Group nested modules
under their parent.}

- `{folder}/` — {what lives here}
- `{folder}/` — {what lives here}
  - `{folder}/{module}/` — {what this module is responsible for}

{Optionally, per major area, a short "follows these principles" list — e.g. abstractions
first, dependency injection, shared foundation.}

### Layered Dependency Model

{The layers, top (most volatile) to bottom (least volatile), and the one-directional
dependency arrow. Map each layer onto the project's naming/folder conventions.}

\```mermaid
{Layer}        ← {what maps onto it}
  ↓
{Layer}        ← {what maps onto it}
  ↓
{Layer}        ← {what maps onto it}
\```

### Dependency Rules

- **{Layer} → {Layer}** — {what this layer is allowed to call, and how (e.g. through
  `*.Abstractions` interfaces)}.
- **Never** — {the forbidden upward references and other hard prohibitions}.


## Architecture Decision Records

{The index of Architecture Decision Records (ADRs) — localized, often non-obvious
decisions. One row per ADR. State that this table is the index: scan it during design and modeling, and open the full record only when a decision is relevant to the work at hand.
See [ADR-FORMAT.md](./ADR-FORMAT.md).}

| # | Decision | Summary |
|---|----------|---------|
| [{NNNN}](docs/adr/{NNNN}-{slug}.md) | {Decision title} | {One-sentence summary of the decision.} |
```

## Rules

- **Shape, not steps.** Describe how the system is decomposed and the rules that hold it together. Step-by-step "how to build X" guidance belongs in an SSR (`docs/ssr/`) or the code, not here.
- **One directional layering.** State the dependency direction explicitly and the prohibited references. The arrows are the contract.
- **Index every SSR.** The `## Solution Strategy` table is the entry point a reader (or agent) scans before designing. Every record in `docs/ssr/` appears here with a matching summary; nothing is added or retired without updating this table.
- **Link, don't inline.** Backbone decisions live in `docs/ssr/` and are *linked* from the index — keep their full content out of `ARCHITECTURE.md` so the map stays scannable.
- **Index every ADR.** The `## Architecture Decision Records` table is the entry point a reader (or agent) scans before designing. Every record in `docs/adr/` appears here with a  matching summary; nothing is added or retired without updating this table.
- **Link, don't inline.** Localized decisions live in `docs/adr/` and are *linked* from the index — keep their full content out of `ARCHITECTURE.md` so the map stays scannable.
- **Keep it current.** When the structure or layering changes, update this file in the same change; a stale architecture map is worse than none.

## Relationship to the other documents

- **`CONTEXT.md`** — the glossary (the *language*). `ARCHITECTURE.md` is the *structure*.
- **`docs/ssr/` (SSRs)** — the backbone decisions, indexed in the `## Solution Strategy` section. Use [SSR-FORMAT.md](./SSR-FORMAT.md).
- **`docs/adr/` (ADRs)** — localized, often non-obvious decisions, indexed in the `## Architecture Decision Records` table. Use [ADR-FORMAT.md](./ADR-FORMAT.md).
