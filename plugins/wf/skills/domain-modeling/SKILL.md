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
- `ARCHITECTURE.md` — the structural map, and the index of SSRs and ADRs.
- `docs/ssr/` — Solution Strategy Records: the backbone rules.
- `docs/adr/` — Architecture Decision Records: localized decisions.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Challenge against the Solution strategy Records (SSRs)

When the user states how something is designed, or which layer owns a responsibility, check it against the SSRs before accepting it. Scan the SSR index in the `ARCHITECTURE.md` `Solution strategy` section, and load only the SSRs relevant to the claim. If you find a contradiction, surface it: "Your SSR mandates that API logic lives in the controller, but you just said it belongs in the service layer — which is right?"

### Surface design improvements

When you spot a decision that would improve the design, explore the `ARCHITECTURE.md` `Solution strategy` section, for the index of existing decisions. Surface it: "Could this be one deep module with a narrow interface, instead of three shallow modules that leak their internals to each other?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

## Validate discovered decisions

When you spot a decision, validate it in the codebase. Explore the `ARCHITECTURE.md` `Building blocks` section, for layers. Walk one real use-case end-to-end and force each step into a layer. Where does each step live, and where do the boundaries — transaction, process, network — fall? "Trace 'place order' from the API down to persistence: which layer owns validation, which owns pricing, and where does the transaction boundary sit?"

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?", "Must every persisted username be between 3 and 50 characters?" Look up (across user-facing, application, integration, and persistence boundaries): Validation rules, Constraints, Domain concepts, Data models, Contracts, Schemas, Relationships, Business logic.

### Update CONTEXT.md inline

When a term is resolved, capture it in `CONTEXT.md` right there via `/manage-docs` — don't batch these up, capture them as they happen.

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Update ADRs and SSRs inline

When an ADR or SSR is resolved, capture it in `ARCHITECTURE.md` right there via `/manage-docs` skill `Inline-update discipline` — don't batch these up, capture them as they happen.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Capture it via `/manage-docs` skill `Inline-update discipline`, which owns the ADR template.

## Offer SSRs sparingly

An SSR captures a *backbone* decision: the solution strategy, the top-level decomposition, or a mandated architectural/design pattern that every feature of a given kind must follow. Write one (instead of, or in addition to, an ADR) only when all three are true:

1. **Structural** — it shapes the top-level decomposition or mandates a pattern, rather than settling one local question.
2. **Reusable** — future features of the same kind are expected to follow it every time.
3. **Backbone-defining** — it is the set of foundational decisions that hold the architecture together and constrain everything built on top of them.

If any of the three is missing, skip the SSR. When you write one: use the `manage-docs` skill `Inline-update discipline` section.
