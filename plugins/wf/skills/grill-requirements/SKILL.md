---
name: grill-requirements
description: A relentless interview that elicits and sharpens requirements while building the domain model — challenging fuzzy terms, inventing edge-case scenarios, and grounding every requirement in the project's approved language. Use before authoring formal requirement sets.
disable-model-invocation: true
---


# Domain glossary modeling

Actively build and sharpen the project's domain model as you grilling. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

All `CONTEXT.md` reads and updates go through `record-term`, which owns the glossary template and its content. `CONTEXT.md`'s existence is mandatory, not lazy: check whether it exists at session start; if not, call `bootstrap-docs` to create it immediately — don't wait for the first term to be ready.

# Ground the input

Load glossary from `CONTEXT.md` first use as the glossary of approved entity and behavior terms; ground every requirement in its exact terms over synonyms. Restate the idea or business need in the approved domain terms.

# During the session

## Run the interview

**Facts** to look up (across user-facing, application, integration, and persistence boundaries): Validation rules, Constraints, Domain concepts, Data models, Contracts, Schemas, Relationships, Business logic.

Interview the user relentlessly about every aspect of this until reaching a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide a recommended answer, ask one at a time, and wait for feedback before continuing — asking multiple questions at once is bewildering. If a fact can be found by exploring the environment (filesystem, tools, etc.), look it up rather than asking. Before confirming shared understanding, list every decision and assumption made this session for the user to veto.

Keep the *Grilling coverage* checklist below alive until every probe is checked (or explicitly ruled not-applicable, with a reason), revisit probe if conflict arises. When exploring the existing solution for the **Facts**, treat each as evidence for discovering implicit requirements, not as an implementation prescription. Use the (directory, solution, project, code) structure and module definitions defined in the  `README.md`, `ARCHITECTURE.md` docs.

```
Grilling coverage:
Glossary:
- [ ] Challenge terms against CONTEXT.md (if it exists)
- [ ] Sharpen fuzzy or overloaded language into precise canonical terms
- [ ] Stress-test domain relationships with concrete scenarios
- [ ] Cross-reference stated behavior against the actual code
- [ ] Offer to update `CONTEXT.md` inline as terms sharpen via `record-term` — capture each resolved term as it happens, never batched.

Requirements:
- [ ] Surface every actor and their goal
- [ ] Surface the behaviors the system must perform (functional requirements)
- [ ] Surface the invariants that must always hold (business rules)
- [ ] Surface boundary and failure conditions (edge cases)
- [ ] Probe degraded behavior — what still works when a dependency is slow or fails
```

These are not a batch to run top-to-bottom: they are the branches the interview walks, one question at a time. Do not skip a line of inquiry, and do not skip any probe within one.

### Line of inquiry: Glossary (CONTEXT.md)

**Probe — Challenge terms against CONTEXT.md**

When the user uses a term that conflicts with the approved language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'subscriber' as X, but you seem to mean Y — which is it?"

**Probe — Sharpen fuzzy or overloaded language**

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

**Probe — Stress-test domain relationships with concrete scenarios**

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

**Probe — Cross-reference stated behavior against the code**

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

**Probe — Update CONTEXT.md inline**

When a term is resolved, capture it in `CONTEXT.md` right there via `record-term` — don't batch, capture each as it happens. `CONTEXT.md` is a glossary and nothing else.

### Line of inquiry: Requirements

Use [references/requirement-types.md](references/requirement-types.md) to keep probing until no open ambiguity remains. Explore the existing solution for the **facts** listed above and treat them as evidence for discovering implicit requirements, not as implementation prescriptions.

**Probe — Surface every actor and their goal**

Drive out who (or what) initiates each behavior and what they are trying to achieve. "Who triggers this cancellation — the customer, an admin, or a scheduled job? What outcome are they after?"

**Probe — Surface the behaviors the system must perform**

For every stated need, pin down the concrete functional requirement behind it. "When the subscription lapses, what exactly must the system do — block access, send a notice, both? In what order?"

**Probe — Surface the invariants that must always hold**

Force out the business rules that must be true regardless of the path taken. "Can a Customer ever have two active subscriptions at once, or is that an invariant the system must guarantee?"

**Probe — Surface boundary and failure conditions**

Invent edge cases and failure scenarios and make the user rule on each. "What happens if the payment succeeds but the confirmation never arrives? What if the amount is zero, or negative?"

**Probe — Probe degraded behavior**

Challenge what still works when a dependency is slow or unavailable. "If the billing service is down when renewal is due, what happens — retry, queue, fail open, fail closed?"

## Verify

Before concluding, run `/solution-agnostic` over the sharpened requirements to scrub any implementation artifacts (widget, screen, table, endpoint, flag) — raise each leaked term to the behavior and entity it enables.

## Output

A sharpened, shared understanding of the requirements — actors, behaviors, business rules, and edge cases — expressed in approved domain terms, plus an optionally-updated existing `CONTEXT.md` glossary. This skill does **not** author formal requirement sets and does **not** create a new `CONTEXT.md`.
