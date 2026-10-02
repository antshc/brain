# ARCHITECTURE.md Format
<!-- `ARCHITECTURE.md` is the map of the system: how the codebase is organized, the layering it follows, and the index of Crosscutting Concepts. It is the structural counterpart to `CONTEXT.md` (which is the glossary). Keep it about *shape and rules*, not implementation detail — the detail lives in the code and in the Crosscutting Concepts it links to. -->

## Structure
<!--
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

References the `CONTEXT.md` file that defines the shared language (terms and domain concepts) used throughout this document, and the `docs/building-blocks/system-context.md` file that holds the system context and solution container diagrams.

## Building blocks

Documents the system's Deployables and their responsibilities, how they interact, and where each lives.

[Building blocks](https://docs.arc42.org/section-5/)

#### Deployables

Table of the system's Deployables, each with a short description of its purpose, where it lives, and a reference to its own record. The Trigger condition is a concise, comma-separated set of domain phrases matched semantically against the caller's touched surface. The link is a full harness record under `docs/building-blocks/`, or the repository's own documentation when that repository documents itself — `record-building-block` owns which.

| Building block | Trigger condition | Summary | Location |
|---|---|---|---|
| **[{{buildingBlockName}}](docs/building-blocks/{{slug}}.md)** ({{mermaidComponentName}}) | {{triggerCondition}} | {{shortDescription}} <!-- terse, concise, optimized for agent navigation --> | `{{location}}` (e.g. `workspace/{{repo}}[/subpath]` or an absolute path) — `{{originUrl}}` |

#### Shared dependency ownership *(optional, hand-authored)*

A dependency more than one Deployable uses (a shared database, queue, cache, or package) and who owns it. Scanned and matched the same as any Trigger condition table; a blank cell never matches.

| Shared dependency | Trigger condition | Summary | Location |
|---|---|---|---|

#### Terminal infrastructure boundaries *(optional, hand-authored)*

Where codebase exploration stops — a managed service, a third-party SaaS, a registry, or a reverse proxy with no further source to read.

| Boundary | Responsibility | Navigation anchor |
|---|---|---|

## Deployment View *(optional)*

References the `DEPLOYMENT.md` file that documents where the building blocks run — nodes, containers, host paths, and the connections between them. `{{deploymentTriggerSummary}}` is 1-3 keyword-dense sentences naming the hosting model, node kinds, and runtime technologies, so an agent can decide whether to load the full document. `record-deployment-view` owns the content; this section is only the pointer.

[Deployment View](DEPLOYMENT.md) — {{deploymentTriggerSummary}}

[Deployment view](https://docs.arc42.org/section-7/)

## Crosscutting Concepts *(optional)*

This section describes crosscutting concepts (practices, patterns, regulations, recurring approaches). They preserve architectural consistency.

<!--
Topics: Architecture Patterns, Design & Coding Patterns, Logging & Tracing, Authorization & Authentication, Configuration, Integration & Communication, Exception & Error Handling, Parallel/Batch Processing
-->

<!-- One row per crosscutting Concept — shared business-process, structural, or operational rules. {{kind}}-{{slug}}: file identity, `{{kind}}` being `dom`, `str`, or `ops`. {{conceptTitle}}: title. {{triggerCondition}}: concise, comma-separated domain phrases that would naturally arise while questioning the change; a blank cell never matches. {{default}}: one sentence naming the choice to take when the design doesn't state one. See the `record-concept` skill. -->

| Concept | Trigger condition | Default |
|---------|-------------------|---------|
| **[{{conceptTitle}}](docs/concepts/{{kind}}-{{slug}}.md)** | {{triggerCondition}} | {{default}} |
```

## Rules

- **Shape, not steps.** Describe how the system is decomposed and the rules that hold it together. Step-by-step "how to build X" guidance belongs in a Concept (`docs/concepts/`) or the code, not here.
- **One directional layering.** State the dependency direction explicitly and the prohibited references. The arrows are the contract.
- **Index Concepts.** Every record in `docs/concepts/` appears in its table with a matching Trigger condition and summary. The table is the entry point an agent scans before designing; nothing is added or retired without updating it.
- **Link, don't inline.** Full Concept content stays in `docs/concepts/` and is *linked* from the index, so the map stays scannable.
