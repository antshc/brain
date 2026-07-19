# ARCHITECTURE.md Format
<!--
`ARCHITECTURE.md` is the map of the system: how the codebase is organized, the layering it
follows, and the index of backbone Crosscutting Concepts. It is the structural counterpart to
`CONTEXT.md` (which is the glossary). Keep it about *shape and rules*, not implementation
detail — the detail lives in the code and in the Crosscutting Concepts it links to.
-->

## Structure
<!--
ADR
“Why did we choose this approach?”
        ↓
Crosscutting Concept
“How must this approach be applied consistently?”
        ↓
Building Blocks
“Which components follow it?”
-->

```md
# {{SYSTEM_NAME}} Overview

A 1-3 sentence summary of what the system is, its architectural style (e.g. modular monolith, volatility-based layering), and the core tech stack.

## Context

References the `CONTEXT.md` file that defines the shared language (terms and domain concepts) used throughout this document.

## Building blocks *(optional)*

Documents the system's components/services and their responsibilities, how they interact, and the top-level codebase layout.

[Building blocks](https://docs.arc42.org/section-5/)

### High-Level Architecture Overview

High-level overview of the system's architecture: main components, their interactions, and overall structure, illustrated with a diagram.

\```mermaid
graph TD
    {{BUILDING_BLOCK}} --> {{BUILDING_BLOCK}}
    {{BUILDING_BLOCK}} --> {{BUILDING_BLOCK}}
\```
#### Services

Bullet list of the system's services/building blocks, each with a short description of its purpose and a reference to its API/config docs. A link to a full doc (built from [BUILDING-BLOCK-SERVICE-FORMAT.md](./BUILDING-BLOCK-SERVICE-FORMAT.md)) is optional — add it only for non-trivial services.

- **{{BUILDING_BLOCK_NAME}}** (`{{MERMAID_COMPONENT_NAME}}`) — {{SHORT_DESCRIPTION}} <!-- terse, concise, optimized for agent navigation -->. {{OPTIONAL_LINK_TO_FULL_DOC}}
- **[Order Service](docs/services/order-service.md)** (`orders`) - Order API: cart, checkout, fulfillment. [API Contracts](docs/services/order-service.swagger.json). Reports checkout and inventory analytics to Google Analytics.

#### Interactions *(optional)*

One-directional, surface communication between the building blocks — one line per dependency arrow, mapped to building blocks.

\```mermaid
{{BUILDING_BLOCK}} --> {{BUILDING_BLOCK}}   ← {{WHAT_MAPS_ONTO_IT}}
\```

### Codebase Structure

The top-level folders and what each contains, one line per folder, with nested modules grouped under their parent.

- `{{FOLDER}}/` — {{WHAT_LIVES_HERE}}
- `{{FOLDER}}/` — {{WHAT_LIVES_HERE}}
  - `{{FOLDER}}/{{MODULE}}/` — {{WHAT_THIS_MODULE_IS_RESPONSIBLE_FOR}}

## Architecture Decision Records

An ADR records a point-in-time decision — hard to reverse, non-obvious, and the result of a real trade-off — tagged **Cornerstone** (shapes the system's overall structure/communication model, or affects multiple building blocks or key quality attributes) or **Local** (confined to one component, concern, or implementation area). See [ADR-FORMAT.md](./ADR-FORMAT.md).

<!-- The index of ADRs. One row per ADR: {{NNNN}} is the sequential ADR number, {{SLUG}} its slug, {{DECISION_TITLE}} its short title, {{SUMMARY}} a 1-3 sentence agent-optimized summary that may reference related Concepts or other ADRs. Scan this table during design and modeling; open the full record only when relevant. -->

| # | Decision | Summary |
|---|----------|---------|
| [{{NNNN}}](docs/adr/{{NNNN}}-{{SLUG}}.md) | {{DECISION_TITLE}} | {{SUMMARY}} |

## Crosscutting Concepts *(optional)*

This section describes crosscutting concepts (practices, patterns, regulations, recurring approaches). They preserve architectural consistency.

<!--
Topics: Architecture Patterns, Design & Coding Patterns, Logging & Tracing, Authorization & Authentication, Configuration, Integration & Communication, Exception & Error Handling, Parallel/Batch Processing
-->

<!-- The index of Concepts — the backbone rules of the solution. One row per concept: {{NNNN}} is the sequential Concept number, {{SLUG}} its slug, {{CONCEPT_TITLE}} its title, {{SUMMARY}} a terse, agent-optimized summary — enough to decide whether to open the full record, and may reference related concepts or ADRs. Scan this table during design and modeling; open the full record only when relevant. See [CONCEPT-FORMAT.md](./CONCEPT-FORMAT.md). -->

| # | Concept | Summary |
|---|----------|---------|
| [{{NNNN}}](docs/concepts/{{NNNN}}-{{SLUG}}.md) | {{CONCEPT_TITLE}} | {{SUMMARY}} |

## Testing Strategy *(optional)*

The test categories that must be present for any change, and — for each — how to detect whether it applies and how to run its tests. Load categories from the Testing strategy Concept (`docs/concepts/`) if one exists; otherwise fall back to the default list: Coding agent feedback loop, Database integration, External system / cloud integration, REST API E2E, Frontend E2E.

#### {{CATEGORY_NAME}}

One line: what this category verifies, when it applies, and the skip condition (e.g. Coding agent feedback loop, Database integration, External system / cloud integration, REST API E2E, Frontend E2E).

- **Prerequisite:** {{INFRA_NEEDED}} <!-- e.g. docker daemon running — or "none" -->
- **Run mode:** Per changed code | Health-check guard

**Per changed code** — run only the tests that cover the changed source.

1. Map the change via the trigger table:

   | Changed source folder | Test project |
   | --- | --- |
   | `{{PATH}}` | `{{TEST_PROJECT}}` |

2. Narrow to the covering test class(es) — note each changed file's **area**, then run only those:

   \```
   dotnet test {{PROJECT}} --filter "Category={{CATEGORY}}&(FullyQualifiedName~{{TEST_CLASS_A}}|FullyQualifiedName~{{TEST_CLASS_B}})"
   \```

**Health-check guard** — always-on; run the whole suite on every change regardless of which files changed (e.g. the coding agent feedback loop):

\```
dotnet test {{PROJECT}} --filter "Category={{CATEGORY}}"
\```
```

## Rules

- **Shape, not steps.** Describe how the system is decomposed and the rules that hold it together. Step-by-step "how to build X" guidance belongs in a Concept (`docs/concepts/`) or the code, not here.
- **One directional layering.** State the dependency direction explicitly and the prohibited references. The arrows are the contract.
- **Index every concept.** The `Crosscutting Concepts` table is the entry point a reader (or agent) scans before designing. Every record in `docs/concepts/` appears here with a matching summary; nothing is added or retired without updating this table.
- **Link, don't inline.** Backbone decisions live in `docs/concepts/` and are *linked* from the index — keep their full content out of `ARCHITECTURE.md` so the map stays scannable.
- **Index every ADR.** The `## Architecture Decision Records` table is the entry point a reader (or agent) scans before designing. Every record in `docs/adr/` appears here with a  matching summary; nothing is added or retired without updating this table.
- **Link, don't inline.** Localized decisions live in `docs/adr/` and are *linked* from the index — keep their full content out of `ARCHITECTURE.md` so the map stays scannable.
- **Keep it current.** When the structure or layering changes, update this file in the same change; a stale architecture map is worse than none.

## Relationship to the other documents

- **`CONTEXT.md`** — the glossary (the *language*). `ARCHITECTURE.md` is the *structure*.
- **`docs/concepts/` (Concepts)** — the backbone concepts, indexed in the `Crosscutting Concepts` section. Use [CONCEPT-FORMAT.md](./CONCEPT-FORMAT.md).
- **`docs/adr/` (ADRs)** — a fundamental architectural direction, backbone decisions or localized, often non-obvious decisions, indexed in the `Architecture Decision Records` table. Use [ADR-FORMAT.md](./ADR-FORMAT.md).
