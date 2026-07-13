---
name: grill-requirements
description: A relentless interview that elicits and sharpens requirements while building the domain model — challenging fuzzy terms, inventing edge-case scenarios, and grounding every requirement in the project's approved language. Use before authoring formal requirement sets.
disable-model-invocation: true
---


# Domain glossary modeling

Actively build and sharpen the project's domain model as you grilling. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

All `CONTEXT.md` reads, creates, and updates go through `/manage-docs`, which owns the glossary template and the lazy-creation rules — create it only when you have something to write, and if no `CONTEXT.md` exists, create one when the first term is resolved.

# Ground the input

Load glossary from `CONTEXT.md` first use as the glossary of approved entity and behavior terms; ground every requirement in its exact terms over synonyms. Restate the idea or business need in the approved domain terms.

# During the session

## Run /grilling

**Facts** to look up (across user-facing, application, integration, and persistence boundaries): Validation rules, Constraints, Domain concepts, Data models, Contracts, Schemas, Relationships, Business logic.

Run `/grilling` — interview one question at a time, giving your recommended answer for each, and keep the *Grilling coverage* checklist below alive until every probe is checked (or explicitly ruled not-applicable, with a reason). If a *fact* can be found in the codebase, look it up rather than asking; the *decisions* are the user's. Explore the existing solution for the **Facts**, then treat each as evidence for discovering implicit requirements, not as an implementation prescription. Use the (directory, solution, project, code) structure and module definitions defined in the docs (check `README.md`, `ARCHITECTURE.md`) during the exploration.

```
Grilling coverage:
Glossary:
- [ ] Challenge terms against CONTEXT.md (if it exists)
- [ ] Sharpen fuzzy or overloaded language into precise canonical terms
- [ ] Stress-test domain relationships with concrete scenarios
- [ ] Cross-reference stated behavior against the actual code
- [ ] Offer to update `CONTEXT.md` inline as terms sharpen via `/manage-docs` — capture each resolved term as it happens, never batched.

Requirements:
- [ ] Surface every actor and their goal
- [ ] Surface the behaviors the system must perform (functional requirements)
- [ ] Surface the invariants that must always hold (business rules)
- [ ] Surface boundary and failure conditions (edge cases)
- [ ] Probe degraded behavior — what still works when a dependency is slow or fails
```

Use [references/requirement-types.md](references/requirement-types.md) to keep probing until no open ambiguity remains: drive out the actors, functional requirements, business rules, edge cases, and failure paths behind every stated behavior. Explore the existing solution for the **facts** listed above and treat them as evidence for discovering implicit requirements, not as implementation prescriptions.

## Verify

Before concluding, run `/solution-agnostic` over the sharpened requirements to scrub any implementation artifacts (widget, screen, table, endpoint, flag) — raise each leaked term to the behavior and entity it enables.

## Output

A sharpened, shared understanding of the requirements — actors, behaviors, business rules, and edge cases — expressed in approved domain terms, plus an optionally-updated existing `CONTEXT.md` glossary. This skill does **not** author formal requirement sets and does **not** create a new `CONTEXT.md`.
