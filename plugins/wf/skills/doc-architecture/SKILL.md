---
name: doc-architecture
description: >-
  Record settled architecture and maintain its indexes and glossary. Use for 'record an ADR', 'add a glossary term', 'load an index', or 'initialize missing docs'. Not for open decisions → `design`; Concept interviews → `define`; diagrams → `doc-diagram`.
argument-hint: "route: adr | building-block | deployment-view | term | concept-body | concept-record | decision-bullet | initialize | index [action]"
---

# Document Architecture

Record settled knowledge, render an established body, or maintain architecture indexes. Discovery and interviews remain with the caller; recording never starts another interview.

## Select and load

1. Honor an explicit `route`; accept existing record `mode` values as aliases for the same routes. Otherwise select from the requested artifact, operation, and persistence intent. An unqualified architecture request has no default. Resolve ambiguous artifacts, conflicting selectors, or save/no-save intent before writes.
2. MUST read the selected playbook fully before checking its gate or acting. Read only resources selected below, resolving bundled paths from this skill's base directory. A playbook names actions and headings in already-loaded resources; return here for conditional loads or another route, never recursively invoke this skill.
3. Apply the procedure's evidence, authorization, output, and completion rules. A failed gate returns the miss and appropriate home; it never produces an unsupported record. Preserve caller inputs and authored-document paths.

| Route | Select when | Procedure |
|---|---|---|
| `adr` | Persist a hard-to-reverse choice, why it won, and rejected alternatives | [ADR](playbooks/adr.md) |
| `building-block` | Record one Deployable's responsibility, interfaces, and structure | [Building block](playbooks/building-block.md) |
| `deployment-view` | Record where production nodes and containers run | [Deployment view](playbooks/deployment-view.md) |
| `term` | Capture one resolved domain term | Record term below |
| `concept-body` | Render or revise a shared approach without saving | [Concept](playbooks/concept.md), Body through Quality gate only |
| `concept-record` | Persist or extend a settled shared approach and its index row | [Concept](playbooks/concept.md) |
| `decision-bullet` | Return one compact established decision | Decision bullet below |
| `initialize` | Create missing architecture and glossary files, only when requested | Initialize missing docs below |
| `index` | Load, match, generate triggers, or sync indexes | [Index](playbooks/index.md); select action below |

- `concept-body` and `decision-bullet` MUST NOT write files, name records, sync indexes, or switch to persistence. Return output to the caller.
- Both Concept routes share body rules. `concept-record` reuses a compliant supplied body without rendering or interviewing again.
- Persist one record at a time, when settled. Grouping adds no approval, publication, execution, or discovery steps.
- A Deployable describes what a block is; topology describes where it runs. Load both only when both artifacts are requested or topology requires a missing Deployable. Apply each prerequisite's gate before continuing.
- Record routes author body-grounded index values; index actions perform mechanics. Record and index changes belong in the same change; never invent policy to fill a row.
- *Load and follow the `doc-diagram` skill to create Mermaid flowchart, swimlane, or sequence diagrams* for diagrams. For code inspection, *Load and follow the `research` skill to investigate primary sources and return cited findings* and send its Explore request to `hunter`. Access other skills through invocation, never their private resources.

## Index actions

Load the index playbook for `index`, `adr`, `building-block`, `deployment-view`, and `concept-record`. Record routes use its named operations directly; external index requests supply `action` or the exact operation name. Infer only an unambiguous operation; otherwise ask. `load` and `scan` are read-only and never initialize files.

| Action | Operation |
|---|---|
| `load` | Load index |
| `scan` | Scan and match |
| `trigger` | Generate trigger condition |
| `ensure-section` | Ensure section exists |
| `sync-row` | Sync index row |
| `sync-deployment` | Sync Deployment View reference |

For `sync-row`, pass mutation as `rowAction` = `add`, `supersede`, or `retire`; legacy `action` values remain accepted when they are not route actions. Keep route action and row mutation distinct.

## Resource map

Read selected resources fully; all links resolve from this skill's base directory. The index loader runs with the caller's repository root as CWD.

| Resource | Load when |
|---|---|
| [Index defaults](references/defaults.md) | `adr` or `concept-record` authors or repairs a row |
| [Architecture format](templates/ARCHITECTURE-FORMAT.md) | Ensure section exists needs a skeleton or section position; includes record-route index prerequisites |
| [Architecture bootstrap](templates/ARCHITECTURE-BOOTSTRAP-FORMAT.md) | `initialize` finds ARCHITECTURE.md missing |
| [Glossary bootstrap](templates/GLOSSARY-BOOTSTRAP-FORMAT.md) | `initialize` finds GLOSSARY.md missing |
| [Building block format](templates/BUILDING-BLOCK-FORMAT.md) | `building-block` writes a full record |
| [Deployment format](templates/DEPLOYMENT-VIEW-FORMAT.md) | `deployment-view` creates or updates topology |
| [Glossary format](templates/GLOSSARY-FORMAT.md) | `term` captures a resolved term |
| [Domain body](templates/domain-business-process.md) | Concept Body selects `dom`, business capabilities and processes |
| [Structure body](templates/structure-implementation.md) | Concept Body selects `str`, structural patterns and implementation rules |
| [Operations body](templates/ops-policy.md) | Concept Body selects `ops`, operational policies |
| [Index loader](scripts/load_index.py) | Execute for Load index; preserve its JSON, options, exit codes, and completeness checks |

Select the Concept kind using Body before loading exactly one body template; skip rendering resources when reusing a compliant body. For conditional resource needs, return control to the router for **Resource map**, load the required resource, then resume the named action. A route change returns to **Select and load**.

## Initialize missing docs

Run only when requested. Use the caller's docs root; for a direct request use the established repository docs root or ask if unclear. Check each file independently, create missing files immediately using established context, and preserve existing files byte for byte.

- ARCHITECTURE.md: render only the system overview and Context from the architecture bootstrap. Add optional sections later through Ensure section exists when content exists.
- GLOSSARY.md: render the glossary bootstrap's context heading and empty Language section. Settled terms require the separate `term` route.

Create only these two files. Record routes create docs/adr/, docs/concepts/, and docs/building-blocks/ lazily. Done when both files exist under the supplied root and every pre-existing file is unchanged.

## Record term

Capture one resolved term in the existing GLOSSARY.md in the same turn it crystallises; never batch. Apply the glossary format's context, terminology, and definition rules. Keep implementation detail and implementation decisions out of the glossary. Missing glossary → report the prerequisite; initialize only when requested. Done when the resolved term appears in its context and unrelated content is preserved.

## Decision bullet

Render one established architectural decision as a single bullet; return only the bullet. Use caller-established or source-grounded facts.

```md
- **{{decisionTitle}}**: {{context}}. {{decision}} {{rationale}}.
```

- Title states the decision, not the problem; context explains why a decision is required.
- Decision states the choice and important implementation boundary. Include concrete abstractions, contracts, classes, events, fields, claims, services, topics, components, and high-level details only when architecturally significant.
- Rationale explains why the choice fits this context, rather than repeating it. Add rationale, alternatives, consequences, or implementation steps only when explicitly requested.
- Include external protocol, API, or schema details only when architecture depends on them. Prefer application abstractions when vendor details are inessential.
- Keep method bodies, local variables, exact algorithms, and details that can change without changing the decision outside the bullet.

Done when one grounded bullet matches the scaffold and these rules; no files or indexes changed.

## Completion criteria

- Selected artifact or index action satisfies its gate and output contract; missing metadata or evidence is explicit.
- Persisted records and required index rows or pointers agree; read-only and render-only routes made no writes.
- Report written paths and index result, returned body and kind, compact bullet, complete loaded/matched rows, or explicit gate/load failure as appropriate.
