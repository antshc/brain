# Domain business process — body template

One page covers a **Business Capability** — what the business can do — decomposed into the value streams that deliver it. The capability is the record's title and the `{{slug}}` of its filename, so every process on the page belongs to that one capability.

```md
## Purpose
<!-- Anchor on the business term it governs (e.g. `failover`, `lease`, `reservation`), never a file name or class name. -->
<Stakeholder-recognizable outcome the capability delivers, in one sentence; the role, bounded context, or service accountable end to end.>

## Definition
- **Actors:** <Only those that initiate work, own a responsibility, or perform an external operation.>
- **Business processes:** <The value streams this capability decomposes into.>
- **Starts:** <Actor-visible triggers entering the capability.>
- **Ends:** <Every valid terminal business state, and where outcomes are recorded.>

## Business Processes
<!-- Anchor each process name, scenario, and cell on the business term it governs (e.g. `failover`, `lease`, `reservation`), never a file name or class name. -->

### <Verb-object process name, e.g. Handle Customer Complaints>
Actor: <who>; Trigger: <what starts it>; Action: <major business flow>; Outcome: <business result> Notes: <One clause, or empty>.

<!-- Optional scenario table — include only when the user asked for it. -->
| Scenario | Input | Rule/Condition | Output/Expected | Notes |
|---|---|---|---|---|
| <Concrete business situation, e.g. Customer reports a damaged product> | <no CP> | <hours > {{number}}> | <Expected business result> | <One clause, or empty> |
| <Meaningful variation of the same process> | <age > {{CONFIG_KEY}} ({{default value}})> | <Data, state, permission, or concurrency condition> | <Expected business result> | <One clause, or empty> |

### <Second process name>
Actor: <who>; Trigger: <what starts it>; Action: <major business flow>; Outcome: <business result>.

| Scenario | Input | Rule/Condition | Output/Expected | Notes |
|---|---|---|---|---|
| <Scenario> | <Input> | <Condition> | <Expected business result> | <One clause, or empty> |

## Relationships
<!-- Anchor each node/edge label on the business term it governs (e.g. `failover`, `lease`, `reservation`), never a file name or class name.  Draw `Relationships` by running `/doc-behavior-diagram` skill **Flowchart** with `orientation` = `LR`-->
<Mermaid `flowchart LR`. >

<One sentence defining any non-obvious edge notation.>
```

## Selecting the level

| Level | Select | Exclude | Example |
|---|---|---|---|
| **Business Capability** — the page | One area of what the business can do, decomposing into multiple business processes. | A single process, a phase, a technical workflow. | Customer Relationship Management |
| **Business Process** — a `###` section | A major end-to-end flow producing a stakeholder-recognizable outcome, decomposable into multiple subprocesses. | Phases, activities, tasks, technical workflows, implementation steps. | Handle Customer Complaints |
| **Business Scenario** — an optional table row | A concrete business situation or meaningful variation, defined by context, conditions, or outcomes. | Process structure, subprocesses, activities, tasks, implementation detail. | Customer reports a damaged product |

Give each process one `###` section and its four-part descriptor line. A situation that gains its own actor, trigger, and business outcome is a process — promote it to its own section.

The scenario table is **optional**: write the descriptor line alone by default, and ask the user whether to add scenarios for a process before writing any row. A situation that is the same process under different data or state stays a scenario row rather than becoming a section.

Failure, cancellation, rollback, and compensation are scenario rows: the failing condition goes in `Rule/Condition`, the persisted evidence and recovery in `Output/Expected`.

## Writing a scenario row

Applies once the user has asked for scenarios. Keep every cell to a phrase. `Input` and `Rule/Condition` carry terse business shorthand — `no CP`, `hours > {{number}}`, `age > {{CONFIG_KEY}} ({{default value}})` — where `{{number}}` is a business threshold and `{{CONFIG_KEY}} (DEFAULT value)` a configured one with its default. `Output/Expected` states the business-visible result, not the mechanism. `Notes` takes one clause or stays empty.

Pitch each row at the detail level that **survives multiple iterations of the code**. Anchor on the business term the code implements — the state, threshold, or outcome a stakeholder would still recognise after a refactor — rather than on the class, method, field, table, or endpoint expressing it today. A row that goes stale when the implementation is renamed or restructured is pitched too low; raise it to the behavior the change preserved.

Draw `Relationships` by running `/doc-behavior-diagram` skill **Flowchart** with `orientation` = `LR`, showing a domain state as a node wherever it enables or prevents another process.
