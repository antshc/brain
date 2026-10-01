# Instruction Robustness

## Purpose

Write agent instructions that are executed as constraints instead of being restated, softened, reinterpreted, or ignored in favor of an apparently equivalent approach.

## Approach

Make the intended behavior directly executable. A critical instruction states **when it applies**, **what MUST happen**, and—when a plausible escape path exists—**what MUST NOT replace it**.

Add a terse rationale when the constraint protects something not obvious from the requested outcome. The rationale gives the agent the decision boundary behind the rule, so it is less likely to optimize the rule away while pursuing the same apparent result.

Close predictable reinterpretations explicitly. If an agent may choose a faster, simpler, smaller, or "equivalent" route, say that this does not relax the constraint. If the required behavior cannot be performed, define the failure path instead of leaving room for improvisation.

Compliance is observable behavior, not acknowledgement. Do not ask the agent to repeat, paraphrase, or explain the instruction as proof that it understood it.

## Rules

- MUST write critical instructions as direct, atomic, observable behavior.
- MUST state the trigger or condition when a rule is not universal.
- MUST use `MUST` / `MUST NOT` for hard constraints rather than preference language.
- MUST pair a critical `MUST` with the relevant `MUST NOT` when an obvious substitute could satisfy the outcome while violating the intended process.
- MUST add a terse rationale when the constraint protects a non-obvious property such as context, isolation, ownership, verification, safety, or ordering.
- MUST close predictable optimization paths with an explicit clause such as "even when faster, simpler, smaller, or apparently equivalent."
- MUST define what to do when a required action or mechanism is unavailable.
- MUST NOT rely on vague reinforcement such as "follow carefully", "make sure", or repeated wording of the same rule.
- MUST NOT require restating, paraphrasing, acknowledging, or explaining an instruction as evidence of compliance.
- MUST NOT mix optional guidance into the same sentence as a hard constraint when that weakens which part is mandatory.

## Pattern

```md
When <condition>, MUST <required behavior>.
MUST NOT <likely violating substitute>.

Rationale: <one terse sentence naming the property the constraint protects>.

Even when <likely optimization>, MUST still <required behavior>.
If <required behavior> cannot be performed, <explicit failure path>.
```

Use only the clauses needed for the instruction. Do not add ceremony when there is no plausible ambiguity or substitution.

## Example

```md
When codebase exploration is required, MUST invoke the exploration subagent.
MUST NOT explore the codebase directly in the parent agent.

Rationale: delegation preserves parent context for orchestration and isolates exploration responsibility.

Even when direct exploration appears faster or sufficient, MUST delegate it.
If the subagent cannot be invoked, stop and report the blocker.
```

The concept is the instruction-writing pattern; delegation is only one example of a constraint that benefits from it.
