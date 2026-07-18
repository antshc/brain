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
# {System Name} Architecture Overview

## Project Overview

<!-- 1-3 sentences: what the system is, the architectural style (e.g. modular monolith,
volatility-based layering), and the core stack. -->

## Context

<!-- Reference the `CONTEXT.md` file(s) that define the language of the system. -->


## Building blocks

[Building blocks](https://docs.arc42.org/section-5/)

### High-Level Architecture Overview 
The section provides a high-level overview of the system's architecture, including its main components, their interactions, and the overall structure. It should include a diagram that illustrates the relationships between the building blocks.

\```mermaid
graph TD
    {Building Block} --> {Building Block}
    {Building Block} --> {Building Block}
\```

- **<[Building Block](reference to building block details md page)> (`<mermaid component name>`)** — <terse, concise, optimized for agent short description of the building blocks purpose and responsibilities. Reference to the API (swagger), configuration doc, etc.>
- **[Order Service](docs/services/order-service.md)** (`orders`) - Order API: cart, checkout, fulfillment. [API Contracts](docs/services/order-service.swagger.json). Reports checkout and inventory analytics to Google Analytics.

#### Interactions

{Optional section. The Interactions, the one-directional, surface communication between the building blocks. One line per
dependency arrow. Map each to building blocks.}

\```mermaid
{Building Block} --> {Building Block}   ← {what maps onto it}
\```

### Codebase Structure

{The top-level folders and what each contains. One line per folder. Group nested modules
under their parent.}

- `{folder}/` — {what lives here}
- `{folder}/` — {what lives here}
  - `{folder}/{module}/` — {what this module is responsible for}

{Optionally, per major area, a short "follows these principles" list — e.g. abstractions
first, dependency injection, shared foundation.}

## Architecture Decision Records
A short document that records an important architectural decision, its context, considered options.

**Cornerstone ADR**: Defines a fundamental architectural direction and belongs in the Crosscutting Concepts. Test questions: Does it shape the system’s overall structure or communication model? Does it affect multiple building blocks or key quality attributes?

**Local ADR**: Records a localized, often non-obvious decisions to one component, concern, or implementation area. Test questions: Is its impact confined to a small part of the system? Can it change without altering the overall Crosscutting Concepts?

<!--
The index of Architecture Decision Records (ADRs). One row per ADR. State that this table is the index: scan it during design and modeling, and open the full record only when a decision is relevant to the work at hand.
See [ADR-FORMAT.md](./ADR-FORMAT.md).}
-->

| # | Decision | Summary |
|---|----------|---------|
| [{NNNN}](docs/adr/<NNNN>-<slug>.md) | <Decision title> | <1-3 sentences summary of the decision, optimized for the agents. Relations to the crosscutting concepts, other ADRs.> |

## Crosscutting Concepts

This section describes crosscutting concepts (practices, patterns, regulations, recurring approaches). They preserve architectural consistency. 

<!-- 
Topics:
- Architecture Patterns
- Design & Coding Patterns
- Logging & Tracing
- Authorization & Authentication
- Configuration
- Integration & Communication
- Exception & Error Handling
- Parallel/Batch Processing

Examples:
- REST API Design: Common rules for versioning, authentication, errors, pagination, and idempotency.
- Module and Interface Design: Shared rules for dependency injection, small interfaces, and observable results.
- Logging and Observability: Common log format, correlation identifiers, metrics, tracing, and destinations.
-->

<!-->
{The index of Concepts — the backbone rules of the solution.
One row per concept. The Summary cell must be terse, concise, optimized for agents, must be enough to understand the concept and make a decision to read the whole concept. State
that this table is the index: scan it during design and modeling, and open the full record only when a concept is relevant to the work at hand. See [CONCEPT-FORMAT.md](./CONCEPT-FORMAT.md).}
-->

| # | Concept | Summary |
|---|----------|---------|
| [{NNNN}](docs/concepts/<NNNN>-<slug>.md) | <Concept title> | <1-3 sentences summary of the concept, optimized for the agents. Relations to other concepts.> |

## Testing Strategy
{The test categories that must be present for any change, and — for each — how to detect whether it applies and how to run its tests. **Load the categories from the Testing strategy Concept (`docs/concepts/`) if one exists** and link it here; otherwise fall back to the default list: Coding agent feedback loop, Database integration, External system / cloud integration, REST API E2E, Frontend E2E. Reference this section when designing or grilling a plan.}

#### {Category name} — e.g. Coding agent feedback loop, Database integration, External system / cloud integration, REST API E2E, Frontend E2E

{One line: what this category verifies, when it applies, and the skip condition.}

- **Prerequisite:** {infra needed, e.g. docker daemon running — or "none".}
- **Run mode:** {Per changed code | Health-check guard}

**Per changed code** — run only the tests that cover the changed source.

1. Map the change via the trigger table:

   | Changed source folder | Test project |
   | --- | --- |
   | `{path/*}` | `{test project}` |

2. Narrow to the covering test class(es) — note each changed file's **area**, then run only those:

   \```
   dotnet test <project> --filter "Category=<Category>&(FullyQualifiedName~<TestClassA>|FullyQualifiedName~<TestClassB>)"
   \```

**Health-check guard** — always-on; run the whole suite on every change regardless of which files changed (e.g. the coding agent feedback loop):

\```
dotnet test <project> --filter "Category=<Category>"
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
