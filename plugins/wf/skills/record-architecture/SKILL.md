---
name: record-architecture
description: Records settled architecture as ADRs, Concepts, Deployables, deployment topology, or glossary terms; renders concept bodies and decision bullets without persistence. Use to document architecture, not discover unresolved decisions.
argument-hint: "mode: adr | building-block | deployment-view | term | concept-body | concept-record | decision-bullet"
---

# Record Architecture

Record settled knowledge or render an established body. Discovery and interviews remain with the caller; recording a settled Concept never starts another interview.

## Select and load

1. Honor an explicit `mode: <mode>`. Otherwise select from the requested artifact and whether the caller wants persistence. If ambiguous, ask which artifact or mode is intended before acting; an unqualified "record architecture" has no default. Conflicting mode and save/no-save instructions require clarification before any write.
2. MUST load the selected procedure with the file-reading tool before acting, including when checking its gate or routing to another mode. Load only its required helpers and selected templates, resolved from this skill's base directory.
3. Apply that procedure's gates, evidence, approval, output, and completion rules. A failed gate reports the miss and appropriate home; it never produces an unsupported record.

| Mode | Select when | Procedure |
|---|---|---|
| `adr` | Persist a hard-to-reverse choice, why it won, and rejected alternatives | [adr.md](./references/adr.md) |
| `building-block` | Record one Deployable's responsibility, interfaces, and structure | [building-block.md](./references/building-block.md) |
| `deployment-view` | Record where production nodes and containers run | [deployment-view.md](./references/deployment-view.md) |
| `term` | Capture one resolved domain term in the glossary | [term.md](./references/term.md) |
| `concept-body` | Render or revise a shared business process, structural pattern, or operational policy without saving | [concept.md — Body](./references/concept.md#body) |
| `concept-record` | Persist or extend a settled shared approach with evidence and index metadata | [concept.md](./references/concept.md) |
| `decision-bullet` | Render one established architectural decision as a compact bullet | [decision-bullet.md](./references/decision-bullet.md) |

- `concept-body` and `decision-bullet` MUST NOT write files, name records, sync indexes, or switch to a persistence mode. Return their output to the caller.
- Both concept modes use the same procedure; `concept-record` accepts a body already rendered under its shared body rules without rendering or interviewing again.
- A Deployable describes what a building block is; deployment topology describes where it runs. Load both procedures only when both artifacts are requested or a deployment prerequisite requires a missing Deployable.
- Persist one record at a time, when settled. Grouping adds no approval, publication, execution, or discovery steps.
- Keep index mechanics with `index-docs`, diagram production with the diagram skills, and code inspection with `explore-codebase`. Invoke helpers; never access another skill's private resources.

## Resource map

Load a format only when its selected procedure needs it:

- [BUILDING-BLOCK-FORMAT.md](./templates/BUILDING-BLOCK-FORMAT.md)
- [DEPLOYMENT-VIEW-FORMAT.md](./templates/DEPLOYMENT-VIEW-FORMAT.md)
- [CONTEXT-FORMAT.md](./templates/CONTEXT-FORMAT.md)
- Index defaults for `adr` and `concept-record`: [defaults.md](./references/defaults.md).
- Concept templates: [domain](./templates/domain-business-process.md), [structure](./templates/structure-implementation.md), [operations](./templates/ops-policy.md).

## Completion criteria

- The selected artifact satisfies its procedure's gate and output contract.
- Persisted records and their required indexes or pointers agree; render-only modes returned output without writes.
- Report the written paths and index result, returned body and kind, compact bullet, or explicit gate miss as appropriate.
