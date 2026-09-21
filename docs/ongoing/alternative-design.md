# Alternative Design Workflow

Status: proposal / ongoing

## Goal

Produce an evidence-backed, decision-complete ZDesign with four composable stages:

1. `wayfinder` finds the path to the solution.
2. `research-*` establishes facts and constraints.
3. `grill-design` challenges the solution and resolves decisions.
4. `to-zdesign` synthesizes the authoritative design.

This replaces a mandatory chain of narrow design skills with an iterative decision workflow.

## Workflow

```text
Loose feature or problem
          |
          v
      wayfinder
  Find the solution path
  and unresolved decisions
          |
          v
     research-*
  Establish facts, constraints,
  current behavior, and options
          |
          v
    grill-design
  Challenge options, resolve
  decisions, and expose gaps
          |
          v
     to-zdesign
  Synthesize the authoritative
  implementation-ready design
```

Research and grilling are iterative:

```text
research-* -> grill-design
    ^             |
    | fact gap    | new research question
    +-------------+
```

If grilling exposes a prototype or manual prerequisite, Wayfinder adds the corresponding ticket before design synthesis continues.

## 1. `wayfinder` — Find the Solution Path

Destination: an evidence-backed, decision-complete ZDesign.

### Responsibilities

- define the destination, scope, goals, and non-goals;
- identify questions that block the design;
- classify each question as research, prototype, grilling, or task;
- order dependencies between questions;
- track decisions, remaining fog, and out-of-scope work;
- expand the frontier as answers expose new questions;
- determine when the path is clear enough for synthesis.

### Output

A Wayfinder map containing:

- destination;
- notes and governing constraints;
- decision tickets;
- decisions so far;
- unresolved fog;
- out-of-scope items.

Wayfinder plans and coordinates. It does not write the final design.

## 2. `research-*` — Build Evidence

Wayfinder routes each research ticket to the narrowest applicable skill.

| Skill | Responsibility |
|---|---|
| `research-capability` | Trace current behavior inside one deployable |
| `research-integrations` | Trace flows and integration contracts across deployables |
| `research-cloud` | Research AWS/Azure APIs, SDKs, permissions, networking, quotas, retries, and failures |
| `research-dotnet` | Research .NET runtime, BCL, language, async, and concurrency behavior |
| `research-aspnet-core` | Research hosting, middleware, DI, configuration, workers, health checks, and lifecycle |
| `research-sdk` | Research SDK packages, versions, clients, methods, pagination, retries, and errors |
| `research-library` | Research third-party library behavior, compatibility, and constraints |
| `research-protocol` | Research REST, messaging, transport, serialization, authentication, and protocol semantics |
| `research-data` | Research existing schemas, ownership, consistency, migrations, concurrency, and retention |
| `research-deployment` | Research topology, configuration, secrets, installation, upgrade, rollback, and cleanup |
| `research` | Handle other external research using authoritative primary sources |

Reliability, security, and observability are research dimensions applied wherever relevant rather than mandatory standalone stages.

### Output

- current-system facts;
- relevant flows and boundaries;
- APIs, events, and contracts;
- runtime and library behavior;
- cloud, data, and deployment constraints;
- viable options;
- limits and failure conditions;
- assumptions and unknowns;
- citations and evidence.

Research discovers facts and constraints. It does not choose the solution.

## 3. `grill-design` — Challenge and Resolve

Consume the Wayfinder path and research evidence.

### Responsibilities

- challenge goals, requirements, constraints, and assumptions;
- compare alternatives against evidence;
- resolve component responsibilities, ownership, and boundaries;
- test runtime, integration, data, cloud, and deployment decisions;
- cover reliability, security, observability, compatibility, and testability;
- send discoverable fact gaps back to research;
- add newly exposed questions to the Wayfinder map;
- record confirmed terminology, concepts, decisions, and assumptions;
- distinguish unresolved questions from accepted risks.

### Output

- feature decisions;
- feature assumptions;
- ADRs and concepts where durable records are required;
- rejected alternatives and rationale;
- accepted risks;
- remaining open questions.

Grilling is complete when the user ends the session after the decision tree is resolved. It does not compose the final ZDesign.

## 4. `to-zdesign` — Synthesize the Design

Run when the Wayfinder frontier is empty, or remaining questions and risks are explicitly accepted.

### Inputs

- Wayfinder map;
- resolved Wayfinder tickets;
- research documents;
- confirmed grill-design outcomes;
- existing architecture, concepts, ADRs, designs, and specifications.

### Responsibilities

- reconcile all evidence and decisions;
- preserve stronger and previously resolved content;
- map requirements to stable capabilities;
- produce a cohesive solution rather than concatenate research reports;
- include only applicable design areas;
- preserve unresolved conflicts as open questions;
- add evidence-triggered deltas and appendices;
- update an existing design incrementally when one already exists.

### Output

One authoritative `docs/designs/<feature>.md` containing, as applicable:

- requirements and current state;
- proposed solution and component changes;
- runtime and integrations;
- data and cloud;
- deployment, upgrade, migration, and rollback;
- reliability and failure handling;
- security and observability;
- compatibility;
- alternatives and risks;
- open questions;
- implementation plan;
- architecture decisions.

The result remains a draft while `Open Questions` is non-empty.

## Stage Gates

| From | Gate |
|---|---|
| Wayfinder → Research | A research question is sharp, scoped, and tied to a blocked decision |
| Research → Grill | Evidence can support a decision, or remaining unknowns are explicit |
| Grill → Research | A missing discoverable fact could change the decision |
| Grill → Wayfinder | A new independent or dependent decision is exposed |
| Grill → ZDesign | The decision tree is resolved and remaining risks are accepted |
| ZDesign → Implementation | The design is internally consistent and implementation-ready |

## Simplification

The previous `current-system`, `integration-design`, `runtime-design`, `cloud-design`, `deployment-design`, `reliability-design`, `security-design`, and `observability-design` responsibilities remain covered, but no longer require separate mandatory workflow stages:

- research establishes the relevant facts and constraints;
- `grill-design` makes and challenges decisions across those dimensions;
- `to-zdesign` assembles the applicable results into the final artifact.

Create a dedicated skill only when a dimension requires reusable domain-specific research behavior that the existing research skills cannot express.
