# ARCHITECTURE.md Format
<!-- `ARCHITECTURE.md` is the map of the system: how the codebase is organized, the layering it follows, and the index of backbone Crosscutting Concepts. It is the structural counterpart to `CONTEXT.md` (which is the glossary). Keep it about *shape and rules*, not implementation detail — the detail lives in the code and in the Crosscutting Concepts it links to. -->

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

Table of the system's services/building blocks, each with a short description of its purpose and a reference to its API/config docs. The Trigger condition is a concise, comma-separated set of domain phrases matched semantically against the caller's touched surface. The link to a full doc is optional — `record-service` owns when one is written.

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

References the `DEPLOYMENT.md` file that documents where the building blocks run — nodes, containers, host paths, and the connections between them. `{{deploymentTriggerSummary}}` is 1-3 keyword-dense sentences naming the hosting model, node kinds, and runtime technologies, so an agent can decide whether to load the full document. `record-deployment-view` owns the content; this section is only the pointer.

[Deployment View](DEPLOYMENT.md) — {{deploymentTriggerSummary}}

[Deployment view](https://docs.arc42.org/section-7/)

## Architecture Decision Records *(optional)*

An ADR records a point-in-time, localized decision — hard to reverse, non-obvious, and the result of a real trade-off. See the `record-adr` skill.

<!-- One row per ADR. {{nnnn}}/{{slug}}: file identity. {{decisionTitle}}: short title. {{triggerCondition}}: concise, comma-separated domain phrases that would naturally arise while grilling the change. {{summary}}: 1-3 agent-optimized sentences. See the `record-adr` skill. -->

| # | Decision | Trigger condition | Summary |
|---|----------|--------------------|---------|
| [{{nnnn}}](docs/adr/{{nnnn}}-{{slug}}.md) | {{decisionTitle}} | {{triggerCondition}} | {{summary}} |

## Crosscutting Concepts *(optional)*

This section describes crosscutting concepts (practices, patterns, regulations, recurring approaches). They preserve architectural consistency.

<!--
Topics: Architecture Patterns, Design & Coding Patterns, Logging & Tracing, Authorization & Authentication, Configuration, Integration & Communication, Exception & Error Handling, Parallel/Batch Processing
-->

<!-- One row per Concept — the backbone rules of the solution. {{nnnn}}/{{slug}}: file identity. {{conceptTitle}}: title. {{triggerCondition}}: concise, comma-separated domain phrases that would naturally arise while grilling the change; a blank cell never matches. {{summary}}: terse, agent-optimized. See the `record-concept` skill. -->

| # | Concept | Trigger condition | Summary |
|---|----------|--------------------|---------|
| [{{nnnn}}](docs/concepts/{{nnnn}}-{{slug}}.md) | {{conceptTitle}} | {{triggerCondition}} | {{summary}} |
```

## Rules

- **Shape, not steps.** Describe how the system is decomposed and the rules that hold it together. Step-by-step "how to build X" guidance belongs in a Concept (`docs/concepts/`) or the code, not here.
- **One directional layering.** State the dependency direction explicitly and the prohibited references. The arrows are the contract.
- **Index everything.** Every record in `docs/concepts/` and `docs/adr/` appears in its table with a matching Trigger condition and summary. The tables are the entry point an agent scans before designing; nothing is added or retired without updating them.
- **Link, don't inline.** Full record content stays in `docs/concepts/`/`docs/adr/` and is *linked* from the index, so the map stays scannable.
