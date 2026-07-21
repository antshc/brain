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
# {{systemName}} Overview

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
    {{buildingBlock1}} --> {{buildingBlock2}}
    {{buildingBlock2}} --> {{buildingBlock3}}
\```
#### Services

Bullet list of the system's services/building blocks, each with a short description of its purpose and a reference to its API/config docs. A link to a full doc (built from [BUILDING-BLOCK-SERVICE-FORMAT.md](./BUILDING-BLOCK-SERVICE-FORMAT.md)) is optional — add it only for non-trivial services.

- **{{buildingBlockName}}** (`{{mermaidComponentName}}`) — {{shortDescription}} <!-- terse, concise, optimized for agent navigation -->. {{optionalLinkToFullDoc}}
- **[Order Service](docs/services/order-service.md)** (`orders`) - Order API: cart, checkout, fulfillment. [API Contracts](docs/services/order-service.swagger.json). Reports checkout and inventory analytics to Google Analytics.

#### Interactions *(optional)*

One-directional, surface communication between the building blocks — one line per dependency arrow, mapped to building blocks.

\```mermaid
{{buildingBlock1}} --> {{buildingBlock2}}   ← {{whatMapsOntoIt}}
\```

### Codebase Structure

The top-level folders and what each contains, one line per folder, with nested modules grouped under their parent.

- `{{folder}}/` — {{whatLivesHere}}
- `{{folder}}/` — {{whatLivesHere}}
  - `{{folder}}/{{module}}/` — {{whatThisModuleIsResponsibleFor}}

## Deployment View *(optional)*

Documents where the building blocks run (environments, hosts, containers) and the infrastructure elements connecting them, illustrated with a diagram.

[Deployment view](https://docs.arc42.org/section-7/)

## Architecture Decision Records *(optional)*

An ADR records a point-in-time, localized decision — hard to reverse, non-obvious, and the result of a real trade-off. See [ADR-FORMAT.md](./ADR-FORMAT.md).

<!-- The index of ADRs. One row per ADR: {{nnnn}} is the sequential ADR number, {{slug}} its slug, {{decisionTitle}} its short title, {{triggerCondition}} one or more short phrases (comma-separated in the same cell if the ADR applies to more than one surface) naming the entity/data shape, endpoint, folder, or change type this row applies to (e.g. "new field on Task entity, new field on Order entity", "POST /orders/**", "src/payments/") — describe the structural condition(s) to match against the plan's touched surface, not a keyword the conversation must happen to say, {{summary}} a 1-3 sentence agent-optimized summary that may reference related Concepts or other ADRs. Scan this table during design and modeling; open the full record only when its Trigger condition matches the kind of change in scope. -->

| # | Decision | Trigger condition | Summary |
|---|----------|--------------------|---------|
| [{{nnnn}}](docs/adr/{{nnnn}}-{{slug}}.md) | {{decisionTitle}} | {{triggerCondition}} | {{summary}} |

## Crosscutting Concepts *(optional)*

This section describes crosscutting concepts (practices, patterns, regulations, recurring approaches). They preserve architectural consistency.

<!--
Topics: Architecture Patterns, Design & Coding Patterns, Logging & Tracing, Authorization & Authentication, Configuration, Integration & Communication, Exception & Error Handling, Parallel/Batch Processing
-->

<!-- The index of Concepts — the backbone rules of the solution. One row per concept: {{nnnn}} is the sequential Concept number, {{slug}} its slug, {{conceptTitle}} its title, {{triggerCondition}} one or more short phrases (comma-separated in the same cell if the Concept applies to more than one surface) naming the entity/data shape, endpoint, folder, or change type this row applies to, same style as the ADR table's Trigger condition (optional — Concepts are presumed in-scope by default since every feature is expected to follow them; fill this in only to narrow a Concept that applies under specific conditions), {{summary}} a terse, agent-optimized summary — enough to decide whether to open the full record, and may reference related concepts or ADRs. Scan this table during design and modeling; open the full record only when relevant. See [CONCEPT-FORMAT.md](./CONCEPT-FORMAT.md). -->

| # | Concept | Trigger condition | Summary |
|---|----------|--------------------|---------|
| [{{nnnn}}](docs/concepts/{{nnnn}}-{{slug}}.md) | {{conceptTitle}} | {{triggerCondition}} | {{summary}} |
```

## Rules

- **Shape, not steps.** Describe how the system is decomposed and the rules that hold it together. Step-by-step "how to build X" guidance belongs in a Concept (`docs/concepts/`) or the code, not here.
- **One directional layering.** State the dependency direction explicitly and the prohibited references. The arrows are the contract.
- **Index every concept.** The `Crosscutting Concepts` table is the entry point a reader (or agent) scans before designing. Every record in `docs/concepts/` appears here with a matching Trigger condition and summary; nothing is added or retired without updating this table.
- **Link, don't inline.** Backbone decisions live in `docs/concepts/` and are *linked* from the index — keep their full content out of `ARCHITECTURE.md` so the map stays scannable.
- **Index every ADR.** The `## Architecture Decision Records` table is the entry point a reader (or agent) scans before designing. Every record in `docs/adr/` appears here with a matching Trigger condition and summary; nothing is added or retired without updating this table.
- **Link, don't inline.** Localized decisions live in `docs/adr/` and are *linked* from the index — keep their full content out of `ARCHITECTURE.md` so the map stays scannable.
- **Keep it current.** When the structure or layering changes, update this file in the same change; a stale architecture map is worse than none.

## Relationship to the other documents

- **`CONTEXT.md`** — the glossary (the *language*). `ARCHITECTURE.md` is the *structure*.
- **`docs/concepts/` (Concepts)** — the backbone concepts, indexed in the `Crosscutting Concepts` section. Use [CONCEPT-FORMAT.md](./CONCEPT-FORMAT.md).
- **`docs/adr/` (ADRs)** — localized, often non-obvious decisions, indexed in the `Architecture Decision Records` table. Use [ADR-FORMAT.md](./ADR-FORMAT.md).
