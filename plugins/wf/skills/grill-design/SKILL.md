---
name: grill-design
description: A relentless interview to sharpen a plan or design, which also creates docs (ADRs, SSRs, and glossary) as we go.
disable-model-invocation: true
---

# Grill Design

Run a `/grilling` session — interview the user relentlessly, one question at a time, walking every branch of the design tree and giving your recommended answer for each. As decisions crystallise, write them down immediately: sharpen the glossary, challenge the architecture, and pin down the testing strategy, capturing each in the right document (`CONTEXT.md`, `ARCHITECTURE.md`, and `docs/ssr/` or `docs/adr/`) inline.

This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. Merely *reading* `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.

## SSR vs ADR

Rule of thumb: if a future engineer should follow it **every time** they build something of this kind, it's an SSR. If it explains why **one** thing was done a surprising way, it's an ADR.

| | **SSR** (`docs/ssr/`) | **ADR** (`docs/adr/`) |
|---|---|---|
| Scope | Top-level decomposition; architectural/design pattern; the backbone | A single, localized decision |
| Altitude | High-level — a rule the whole system follows | Low-level — often non-obvious to a developer |
| Reuse | A template every new feature applies | A point-in-time choice for one area |
| Indexed in `ARCHITECTURE.md` | **Yes** — `## Solution Strategy` | **Yes** — `## Architecture Decision Records` |
| Example | "Every persisted entity is built as Model → Document → Mapping → Repository → Accessor" | "Task initiator is captured from the Keycloak `preferred_username` claim" |

## File structure

Where the domain-model files live and when to create them (single- vs multi-context repos, lazy creation rules): see [FILE-STRUCTURE.md](./FILE-STRUCTURE.md). Read it once when setting up the files or deciding where a new file belongs.

## Lines of inquiry

The grilling must cover **all three lines of inquiry** — Glossary, Architecture, and Testing strategy. Do not skip a line of inquiry, and do not skip any probe within one. These are not a batch to run top-to-bottom: they are the branches the interview walks, one question at a time.

### Coverage checklist

Keep this checklist alive throughout the grilling. Tick each probe off only once you have genuinely covered it, and do not conclude the grilling until every probe is checked (or explicitly ruled not-applicable, with a reason).

```
Grill-design coverage:
Glossary
- [ ] Challenge against the glossary
- [ ] Sharpen fuzzy language
- [ ] Discuss concrete scenarios
- [ ] Cross-reference with code
- [ ] Update CONTEXT.md inline
Architecture
- [ ] Challenge against the existing architecture
- [ ] Trace a concrete flow through the layers
- [ ] Pin down module boundaries and responsibilities
- [ ] Cross-reference against the actual code structure
- [ ] Probe dependency direction and layering
- [ ] Hunt for a deeper module
- [ ] Update ARCHITECTURE.md inline
- [ ] Offer Solution Strategy Records (SSRs) for backbone rules
- [ ] Offer ADRs sparingly
Testing strategy
- [ ] Locate the testing strategy (SSR or fallback)
- [ ] Challenge which test categories must cover the change
```

### Line of inquiry: Glossary (CONTEXT.md)

**Probe — Challenge against the glossary**

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

**Probe — Sharpen fuzzy language**

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

**Probe — Discuss concrete scenarios**

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

**Probe — Cross-reference with code**

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

**Probe — Update CONTEXT.md inline**

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Line of inquiry: Architecture (ARCHITECTURE.md + SSR/ADR)

**Probe — Challenge against the existing architecture**

Read `ARCHITECTURE.md` in full first. Absorb the codebase structure and the layered dependency model — layering direction and dependency rules — then scan the two index tables (`## Solution Strategy` for SSRs, `## Architecture Decision Records` for ADRs). Read only the summary rows in those tables, opening a full record in `docs/ssr/` or `docs/adr/` only when a row is relevant. If the plan conflicts with the documented structure, layering, or any record, call it out immediately: "Your architecture says the write model talks to Postgres directly, but your plan routes it through the cache — is that intentional?" If the plan is a deliberate architectural shift, surface it as a candidate for an ADR or an SSR.

**Probe — Trace a concrete flow through the layers**

Walk one real use-case end-to-end and force each step into a layer. Where does each step live, and where do the boundaries — transaction, process, network — fall? "Trace 'place order' from the API down to persistence: which layer owns validation, which owns pricing, and where does the transaction boundary sit?"

**Probe — Pin down module boundaries and responsibilities**

When a component's responsibility is vague or overlaps another's, force a crisp boundary. "Where exactly does the ordering module end and billing begin? Which one owns pricing?"

**Probe — Cross-reference against the actual code structure**

Check whether the proposed shape matches how the code is really laid out — folders, projects, and existing modules — not just what `ARCHITECTURE.md` claims. If they disagree, surface it: "Your plan adds a `Payments` module, but billing already lives inside `Ordering` in the code — are you splitting it out, or is the doc stale?"

**Probe — Probe dependency direction and layering**

Grill for dependency-rule and layering violations the plan sneaks in. "This makes the domain layer import the HTTP client — that inverts your documented dependency direction. Is that intentional, or should it go through a port?"

**Probe — Hunt for a deeper module**

Push for a deep module — a lot of functionality behind a simple, stable interface — over several shallow ones. "Could this be one deep module with a narrow interface, instead of three shallow modules that leak their internals to each other?"

**Probe — Update ARCHITECTURE.md inline**

When the structure or layering changes, update `ARCHITECTURE.md` right there. Don't batch these up — capture them as they happen. When a new SSR is created, add its summary row to the `## Solution Strategy` index in the same change. When a new ADR is created, add its summary row to the `## Architecture Decision Records` index in the same change. Use the format in [ARCHITECTURE-FORMAT.md](./ARCHITECTURE-FORMAT.md).

`ARCHITECTURE.md` should describe *shape and rules*, not implementation detail. Do not treat `ARCHITECTURE.md` as a spec, a scratch pad, or a place to inline backbone decisions — the step-by-step detail lives in the code and in the linked Solution Strategy Records. It is the structural map and nothing else.

**Probe — Offer Solution Strategy Records (SSRs) for backbone rules**

A **Solution Strategy Record** is different from an ADR. An SSR captures a *backbone* decision: the solution strategy, the top-level decomposition of the system, or a mandated architectural/design pattern that every feature of a given kind must follow. It is a **main architecture rule**.

Offer an SSR (instead of, or in addition to, an ADR) when all three are true:

1. **Structural** — it shapes the top-level decomposition or mandates a pattern, rather
   than settling one local question.
2. **Reusable** — future features of the same kind are expected to follow it every time.
3. **Backbone-defining** — it belongs in the `ARCHITECTURE.md` index where every
   contributor sees it.

If any of the three is missing, skip the SSR. When you write an SSR: put the full record in `docs/ssr/` and add a one-line summary row to the `## Solution Strategy` table in `ARCHITECTURE.md` (the summary must match the SSR's
`**Summary:**` line). Use the format in [SSR-FORMAT.md](./SSR-FORMAT.md).

**Probe — Offer ADRs sparingly**

ADRs are records of localized decisions that are often non-obvious to a developer but do not shape the whole system.

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. When you write an ADR: put the full record in `docs/adr/` and add a one-line summary row to the `## Architecture Decision Records` table in `ARCHITECTURE.md`. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

### Line of inquiry: Testing strategy

**Probe — Locate the testing strategy (SSR or fallback)**

The testing strategy is usually an SSR — look for it by scanning the `## Solution Strategy` index in `ARCHITECTURE.md` for a testing-strategy row and opening that record in `docs/ssr/`. It may not exist; if there's no SSR, fall back to other documented conventions (e.g. `Testing.md`, `README.md`) and the existing tests in the codebase.

**Probe — Challenge which test categories must cover the change**

When the plan adds a new REST API endpoint, external-service integration, persisted entity, or a new module, challenge which documented test categories must cover it — consult the testing-strategy SSR (or fallback) and explore the codebase to find existing tests rather than defaulting to unit tests. "This adds a new repository against the database — your testing strategy mandates an integration-test category for that. Which testing category covers persistence round-trips and queries?"
