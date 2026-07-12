---
name: grill-requirements
description: A relentless interview that elicits and sharpens requirements while building the domain model — challenging fuzzy terms, inventing edge-case scenarios, and grounding every requirement in the project's approved language. Use before authoring formal requirement sets.
disable-model-invocation: true
---


# Domain glossary modeling

Actively build and sharpen the project's domain model as you grilling. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

Create files lazily using the [references/CONTEXT-FORMAT.md](references/CONTEXT-FORMAT.md) — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved.

# Ground the input

Load glossary from `CONTEXT.md` first use as the glossary of approved entity and behavior terms; ground every requirement in its exact terms over synonyms. Restate the idea or business need in the approved domain terms.

# During the session

## Run /grilling

Run `/grilling` — interview one question at a time, giving your recommended answer for each, and keep the coverage checklist below alive until every probe is checked (or explicitly ruled not-applicable, with a reason). If a *fact* can be found in the codebase, look it up rather than asking; the *decisions* are the user's.

```
Grilling coverage:
Glossary:
- [ ] Challenge terms against CONTEXT.md (if it exists)
- [ ] Sharpen fuzzy or overloaded language into precise canonical terms
- [ ] Stress-test domain relationships with concrete scenarios
- [ ] Cross-reference stated behavior against the actual code
- [ ] Offer to update it inline as terms sharpen, using the format in [references/CONTEXT-FORMAT.md](references/CONTEXT-FORMAT.md) — capture each resolved term as it happens, never batched.

Requirements:
- [ ] Surface every actor and their goal
- [ ] Surface the behaviors the system must perform (functional requirements)
- [ ] Surface the invariants that must always hold (business rules)
- [ ] Surface boundary and failure conditions (edge cases)
- [ ] Probe permissions — who may and may not perform each action
- [ ] Probe degraded behavior — what still works when a dependency is slow or fails
```

Use [references/requirement-types.md](references/requirement-types.md) to keep probing until no open ambiguity remains: drive out the actors, functional requirements, business rules, edge cases, and failure paths behind every stated behavior. Explore the existing solution for facts that inform requirements — validation rules, constraints, domain concepts, data models, contracts, schemas, relationships, and business logic across user-facing, application, integration, and persistence boundaries. Treat these as evidence for discovering implicit requirements, not as implementation prescriptions.

## Verify

Before concluding, run `/solution-agnostic` over the sharpened requirements to scrub any implementation artifacts (widget, screen, table, endpoint, flag) — raise each leaked term to the behavior and entity it enables.

## Output

A sharpened, shared understanding of the requirements — actors, behaviors, business rules, and edge cases — expressed in approved domain terms, plus an optionally-updated existing `CONTEXT.md` glossary. This skill does **not** author formal requirement sets and does **not** create a new `CONTEXT.md`.
