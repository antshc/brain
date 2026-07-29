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

## Building blocks

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

Table of the system's services/building blocks, each with a short description of its purpose and a reference to its API/config docs. The Trigger condition is a concise, comma-separated set of domain phrases that may be used during grilling; `index-docs` matches it semantically against the caller's touched surface and grilling context. A link to a full doc (built by the `record-service` skill) is optional — add it only for non-trivial services.

| Service | Trigger condition | Summary |
|---------|-------------------|---------|
| **[{{buildingBlockName}}](docs/services/{{buildingBlockName}}-service.md)** ({{mermaidComponentName}}) | {{triggerCondition}} | {{shortDescription}} <!-- terse, concise, optimized for agent navigation -->. Appendixes: [{{buildingBlockName}} API Contracts](docs/services/{{buildingBlockName}}-service.swagger.json) |

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

An ADR records a point-in-time, localized decision — hard to reverse, non-obvious, and the result of a real trade-off. See the `record-adr` skill.

<!-- The index of ADRs. One row per ADR: {{nnnn}} is the sequential ADR number, {{slug}} its slug, {{decisionTitle}} its short title, {{triggerCondition}} a concise, comma-separated set of domain phrases that would naturally arise while grilling the change, {{summary}} a 1-3 sentence agent-optimized summary. Callers pass this table's headers, Trigger condition column, row metadata, touched surface, grilling context, and glossary to `index-docs`; matching is semantic and does not depend on exact wording. -->

| # | Decision | Trigger condition | Summary |
|---|----------|--------------------|---------|
| [{{nnnn}}](docs/adr/{{nnnn}}-{{slug}}.md) | {{decisionTitle}} | {{triggerCondition}} | {{summary}} |

## Crosscutting Concepts *(optional)*

This section describes crosscutting concepts (practices, patterns, regulations, recurring approaches). They preserve architectural consistency.

<!--
Topics: Architecture Patterns, Design & Coding Patterns, Logging & Tracing, Authorization & Authentication, Configuration, Integration & Communication, Exception & Error Handling, Parallel/Batch Processing
-->

<!-- The index of Concepts — the backbone rules of the solution. One row per concept: {{nnnn}} is the sequential Concept number, {{slug}} its slug, {{conceptTitle}} its title, {{triggerCondition}} a concise, comma-separated set of domain phrases that would naturally arise while grilling the change, {{summary}} a terse, agent-optimized summary. Callers pass this table's headers, Trigger condition column, row metadata, touched surface, grilling context, and glossary to `index-docs`; blank cells never match. See the `record-concept` skill. -->

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

- **`CONTEXT.md`** — the glossary (the *language*). `ARCHITECTURE.md` is the *structure*. Owned by the `record-term` skill.
- **`docs/concepts/` (Concepts)** — the backbone concepts, indexed in the `Crosscutting Concepts` section. Owned by the `record-concept` skill.
- **`docs/adr/` (ADRs)** — localized, often non-obvious decisions, indexed in the `Architecture Decision Records` table. Owned by the `record-adr` skill.
