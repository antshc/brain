# Domain business process — body template

One page covers a **process family**: exactly one main process owning the end-to-end trigger and the shared outcome, the subprocesses it delegates to, and every separately triggered process — stop, commit, rollback, cancellation, compensation — that carries its own trigger and outcome.

```md
## Purpose
<Shared business outcome in one sentence; the role, bounded context, or service accountable end to end.>

## Definition
- **Actors:** <Only those that initiate work, own a responsibility, or perform an external operation.>
- **Main process:** <The single end-to-end business process.>
- **Subprocesses:** <Its direct subprocesses, or None.>
- **Starts:** <Actor-visible triggers entering the family.>
- **Ends:** <Every valid terminal business state, and where operation outcomes are recorded.>

## Process Matrix
| Level | Process | Parent | Actor | Trigger | Available when | Main stages | Outcome | Failure behavior |
|---|---|---|---|---|---|---|---|---|
| Main process | <Verb-object name, e.g. Commit Failover> | None | <Initiator> | <Event or explicit action> | <Permissions, lifecycle state, required data, concurrency> | <Stage> → <subprocess or stage> → <resulting state> | <Business-visible result> | <Persisted failure evidence, cleanup, retry, partial success, or compensation> |
| Subprocess | <Verb-object name> | <Parent process> | <Initiator or parent process> | <Parent invocation or internal condition> | <Permissions, lifecycle state, required data, concurrency> | <Stage> → <stage> → <result> | <Contribution to the parent outcome> | <Persisted failure evidence, cleanup, retry, partial success, or compensation> |

## Variants
| Parent process | Variant | Selected when | Behavioral difference |
|---|---|---|---|
| <Process> | <Variant> | <Data or state condition> | <Only the stages, rules, outcome details, or failure behavior that differ from the parent.> |

## Rules
- **Ownership:** MUST <command intake, orchestration, and execution responsibility>.
- **State:** MUST <valid transitions across the family, keeping lifecycle state, execution status, and completion status distinct>.
- **Concurrency:** MUST <mutual exclusion and conflict behavior>.
- **Finalization:** MUST <explicit terminal choice or completion rule>.
- **Recovery:** MUST <cleanup, retry, resume, rollback, or compensation>.
- **Evidence:** MUST <state, progress, metadata, result, and recovery context that survives failure or restart>.

## Relationships
<Mermaid flowchart.>

<One sentence defining any non-obvious edge notation.>

## Violation signals
- <Observable breach — a process reached without its availability condition, a terminal state written twice; omit if none.>

## Exceptions
- <Permitted variation and its condition; omit if none.>

## Examples
- <One concrete run with trigger, stages, and resulting state; cite code/test if present.>

## Consequences
- <Material trade-off; omit if none.>
```

`Level` is `Main process`, `Subprocess`, or `Independent process`, and `Parent` is `None` for all but a subprocess. Give the matrix one row per process — the main one, each subprocess, and each separately triggered process — and keep every cell compact; a constraint shared by two rows belongs in `Rules`, which holds cross-process invariants and responsibility boundaries only.

A **subprocess** is a distinct business responsibility the main process delegates, with its own stages or failure behavior, reached through its parent rather than triggered on its own. A **variant** is the same process taking different stages or rules because data or state selected them, under the parent's trigger, owner, and business outcome — so it never gets a matrix row. Drop the `Variants` section when nothing has one, and promote a variant to a subprocess or process the moment it gains its own trigger, owner, outcome, or failure lifecycle.

Draw `Relationships` by running `/doc-behavior-diagram` skill **Flowchart**, labelling each data- or state-selected branch with its variant name and showing a domain state as a node wherever it enables or prevents another process.
