---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when the user wants to pin down domain terminology or a ubiquitous language, record an architectural decision, or when another skill needs to maintain the domain model.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## Managing the docs

All doc reads, creates, and updates go through `/manage-docs` — it owns the templates for **documents**, and the rules for where each file lives, when to create it (lazily), and how to keep the `ARCHITECTURE.md` indexes in sync. Consult it when setting up the files or capturing a decision.

**Documents**:
- `CONTEXT.md` — the glossary (the *language*).
- `ARCHITECTURE.md` — the structural map, and the index of Concepts and ADRs.
- `docs/concepts/` — Crosscutting Concepts: the backbone rules.
- `docs/adr/` — Architecture Decision Records: fundamental or localized decisions.

## Load strategy guardrails

Before designing or grilling:

1. Read the `Building blocks`, `Crosscutting Concepts` and the `Architecture Decision Records` indexies in `ARCHITECTURE.md`.
2. Load only Building blocks, Concepts and ADRs relevant to the current scope.
3. Extract:
   * **Mandates** — required concepts, patterns and boundaries.
   * **Prohibitions** — explicitly rejected approaches, rejected concidered options.
   * **Open space** — unconstrained choices.
4. Use these guardrails to frame questions, scenarios, and alternatives.
* A Concept-violating option must not be presented as equally valid — cite the Concept and surface the conflict.
* An option that contradicts a considered-and-rejected ADR alternative must not be presented as equally valid.

Re-scope when the module, boundary, integration, or responsibility changes.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Challenge which test categories must cover the change

Read the relevant `Testing strategy` section in `ARCHITECTURE.md`. No Testing strategy? Fall back to documented conventions (`Testing.md`, `README.md`) and existing tests in the codebase.

When the plan adds a REST endpoint, external-service integration, persisted entity, or new module, challenge which documented categories must cover it. Consult the `Testing strategy` (or fallback) and explore existing tests — don't default to unit tests. "This adds a repository against the database — your strategy mandates an integration-test category. Which category covers persistence round-trips and queries?"

## Validate discovered decisions

When you spot a decision, don't take it at face value — validate it against reality. Check it against two sources of truth: the architecture map (does the intended structure hold?) and the code (does the implementation agree?). Where they diverge, surface the gap.

### Surface design improvements

When you spot a decision that would improve the design, surface it: "Could this be one deep module with a narrow interface, instead of three shallow modules that leak their internals to each other?"

### Surface strategy drift

Treat Concepts as intended architecture and code as implemented architecture.

When they conflict, classify the gap:

* **Violation** — the proposal breaks the fundamental concepts.
* **Drift** — the implementation diverges.
* **Supersession** — the Concept is outdated.
* **Out of scope** — the Concept does not apply.

### Trace through the layers

Read the relevant `Building blocks` section in `ARCHITECTURE.md`, then select one representative scenario and trace it end-to-end. Walk one real scenario end-to-end and force each step into a layer. Where does each step live, and where do the boundaries — transaction, process, network — fall? "Trace 'place order' from the API down to persistence: which layer owns validation, which owns pricing, and where does the transaction boundary sit?"

Validate the trace against the loaded Concept guardrails, architecture map, and code, then classify any mismatch using `Surface strategy drift`.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?", "Must every persisted username be between 3 and 50 characters?" Look up (across user-facing, application, integration, and persistence boundaries): Validation rules, Constraints, Domain concepts, Data models, Contracts, Schemas, Relationships, Business logic.

### Update CONTEXT.md inline

When a term is resolved, capture it in `CONTEXT.md` right there via `/manage-docs` — don't batch these up, capture them as they happen.

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Update ADRs and Concepts inline

When an ADR or Concept is resolved, capture it in `ARCHITECTURE.md` right there via `/manage-docs` skill `Inline-update discipline` — don't batch these up, capture them as they happen.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Capture it via `/manage-docs` skill `Inline-update discipline`, which owns the ADR template.

### Offer Concepts sparingly

A Concept captures a *backbone* decision: the top-level decomposition, or a mandated architectural/design pattern that every feature of a given kind must follow. Write one (instead of, or in addition to, an ADR) only when all three are true:

1. **Structural** — it shapes the top-level decomposition or mandates a pattern, rather than settling one local question.
2. **Reusable** — future features of the same kind are expected to follow it every time.
3. **Backbone-defining** — it is the set of foundational decisions that hold the architecture together and constrain everything built on top of them.

If any of the three is missing, skip the Concept. When you write one: use the `manage-docs` skill `Inline-update discipline` section.
