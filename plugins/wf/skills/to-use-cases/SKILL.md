---
description: Write a **use case** — actor, preconditions, a 1-5 step main flow, alternate flows, postconditions. Use when the user wants to document how an actor interacts with the system to reach a goal, capture main/alternate flows, or turn a capability/story into a use case.
name: to-use-cases
---

Turn a capability, stakeholder requirement, or feature idea into one **use case**: a terse, flow-oriented account of how a **primary actor** reaches a goal, with its main flow, alternate flows, and outcome. One capability yields one use case; a capability with two unrelated actor goals yields one use case per goal.

## Workflow
1. **Name the actor and goal** → one primary actor, one goal sentence: `<Actor> wants to <goal>.` *Done when* the goal is a single outcome, not a bundle of goals.
2. **State preconditions** → the facts that must already hold before the flow starts (auth state, existing data, permissions). *Done when* every main-flow step relies on nothing left unstated.
3. **Write the main flow** → 1-5 numbered steps, alternating actor action / system response, each a single sentence, present tense. *Done when* the flow reaches the goal in 5 steps or fewer — a flow needing a 6th step is two use cases; split it.
4. **Write alternate flows** → one bullet per branch point in the main flow: the condition, then the deviation and its result. *Done when* every failure and decision point named in Business Rules or Edge Cases for this capability has a bullet.
5. **State postconditions** → the facts guaranteed true once the main flow completes. *Done when* every state change the main flow causes is named.
6. **Verify** → apply the Quality Check below.

## Quality Check (before output)
- Main flow is 1-5 steps; a longer flow is split into a base use case plus an `include`d/extension use case.
- Each step is one sentence, one actor, one action or response — no "and" chains, no implementation detail (no screen, button, endpoint).
- Every alternate flow names its trigger condition and its result; none left as "TBD" or "etc.".
- Postconditions state facts, not further actions.
- Steps use the domain's approved terms (`CONTEXT.md`) when it exists in the repo.

## Output Format

```
Use Case: {{title}}
Primary Actor: {{actor}}
Preconditions: {{fact1}}; {{fact2}}.
Main Flow:
1. {{actor action or system response}}.
2. ...
(up to 5)
Alternate Flows:
- {{condition}} → {{deviation and result}}.
- ...
Postconditions: {{fact1}}; {{fact2}}.
```
