---
description: Write a **Use case** for one actor goal within a Feature — actor, preconditions, a 1-5 step main flow, alternate flows, and postconditions. Use when the user wants to document how an actor reaches a goal, capture main/alternate flows, or turn requirements or a User story into a Use case.
name: to-use-cases
---

Turn requirement text or a User story into one **Use case**: a terse, flow-oriented account of how a primary actor reaches one goal within a Feature.

## Workflow
1. **Identify the Feature** → name the user-meaningful behavior containing the actor's goal. *Done when* the Feature is narrower than a Capability and independent of screens, endpoints, or other implementation artifacts.
2. **Name the actor and goal** → one primary actor, one goal sentence: `<Actor> wants to <goal>.` *Done when* the goal is a single outcome within the Feature, not a bundle of goals.
3. **State preconditions** → the facts that must already hold before the flow starts (auth state, existing data, permissions). *Done when* every main-flow step relies on nothing left unstated.
4. **Write the main flow** → 1-5 numbered steps, alternating actor action / system response, each a single sentence, present tense. *Done when* the flow reaches the goal in 5 steps or fewer — a flow needing a 6th step is two Use cases; split it.
5. **Write alternate flows** → one bullet per branch point in the main flow: the condition, then the deviation and its result. *Done when* every failure and decision point named in Business rules or Edge cases for this Feature and actor goal has a bullet.
6. **State postconditions** → the facts guaranteed true once the main flow completes. *Done when* every state change the main flow causes is named.
7. **Verify** → apply the Quality Check below.

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
