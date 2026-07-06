---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when the user wants to pin down domain terminology or a ubiquitous language, record an architectural or design decision (ADR/SDR), or when another skill needs to maintain the domain model.
---

# Domain Modeling

Actively build and sharpen the project's domain model and design decisions. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## SDR vs ADR
Rule of thumb: if a future engineer should follow it **every time** they build something of this kind, it's an SDR. If it explains why **one** thing was done a surprising way, it's an ADR.

| | **SDR** (`docs/sdr/`) | **ADR** (`docs/adr/`) |
|---|---|---|
| Scope | Top-level decomposition; architectural/design pattern; the backbone | A single, localized decision |
| Altitude | High-level — a rule the whole system follows | Low-level — often non-obvious to a developer |
| Reuse | A template every new feature applies | A point-in-time choice for one area |
| Indexed in `ARCHITECTURE.md` | **Yes** — `## Solution Design Strategy` | **Yes** — `## Architecture Decision Records` |
| Example | "Every persisted entity is built as Model → Document → Mapping → Repository → Accessor" | "Task initiator is captured from the Keycloak `preferred_username` claim" |

## File structure

Most repos have a single context:

```
/
├── ARCHITECTURE.md                      ← also indexes the Solution Design Strategy (SDRs)
├── CONTEXT.md
├── docs/
│   ├── sdr/                             ← Solution Design Records (backbone rules)
│   │   └── 0001-persisted-domain-model-repository.md
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── ARCHITECTURE.md
├── CONTEXT-MAP.md
├── docs/
│   ├── sdr/                             ← Solution Design Records (backbone rules)
│   │   └── 0001-persisted-domain-model-repository.md
│   └── adr/                          ← system-wide ADRs (docs/sdr/ holds system-wide SDRs)
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily — only when you have something to write. 

If no `CONTEXT.md` exists, create one when the first term is resolved. 

If no `ARCHITECTURE.md` exists, create one when the first term is resolved. .

If no `docs/adr/` exists, create it when the first ADR is needed, then add it to the `## Architecture Decision Records` index in `ARCHITECTURE.md`. 

If no `docs/sdr/` exists, create it when the first SDR is needed, then add it to the `## Solution Design Strategy` index in `ARCHITECTURE.md`.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Challenge against the existing architecture

Scan `ARCHITECTURE.md` first — the codebase structure, the layered dependency model and its rules, and the index tables (`## Solution Design Strategy` for SDRs and `## Architecture Decision Records` for ADRs). Read the structure and layering directly; from the index tables read only the summary rows, opening a full record in `docs/sdr/` or `docs/adr/` when a row is relevant. When the plan conflicts with the documented structure, layering, or a record, call it out immediately. "Your architecture says the write model talks to Postgres directly, but your plan routes it through the cache — is that an intentional change?" If the plan is a deliberate architectural shift, surface it as a candidate for an ADR or a Solution Design Record.

### Challenge against the testing strategy

The testing strategy is usually an SDR — look for it by scanning the `## Solution Design Strategy` index in `ARCHITECTURE.md` for a testing-strategy row and opening that record in `docs/sdr/`. It may not exist; if there's no SDR, fall back to other documented conventions (e.g. `Testing.md`, `README.md`) and the existing tests in the codebase. When the plan adds a new REST API endpoint, external-service integration, persisted entity, or a new module, challenge which documented test categories must cover it — consult the testing-strategy SDR (or fallback) and explore the codebase to find existing tests rather than defaulting to unit tests. "This adds a new repository against the database — your testing strategy mandates an integration-test category for that. Which testing category covers persistence round-trips and queries?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Update ARCHITECTURE.md inline

When the structure or layering changes, update `ARCHITECTURE.md` right there. Don't batch these up — capture them as they happen. When a new SDR is created, add its summary row to the `## Solution Design Strategy` index in the same change. When a new ADR is created, add its summary row to the `## Architecture Decision Records` index in the same change. Use the format in [ARCHITECTURE-FORMAT.md](./ARCHITECTURE-FORMAT.md).

`ARCHITECTURE.md` should describe *shape and rules*, not implementation detail. Do not treat `ARCHITECTURE.md` as a spec, a scratch pad, or a place to inline backbone decisions — the step-by-step detail lives in the code and in the linked Solution Design Records. It is the structural map and nothing else.

### Offer ADRs sparingly
ADRs are records of localized decisions that are often non-obvious to a developer but do not shape the whole system.

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. When you write an ADR: put the full record in `docs/adr/` and add a one-line summary row to the `## Architecture Decision Records` table in `ARCHITECTURE.md`. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

### Offer Solution Design Records (SDRs) for backbone rules

A **Solution Design Record** is different from an ADR. An SDR captures a *backbone* decision: the solution strategy, the top-level decomposition of the system, or a mandated architectural/design pattern that every feature of a given kind must follow. It is a **main architecture rule**. 

Offer an SDR (instead of, or in addition to, an ADR) when all three are true:

1. **Structural** — it shapes the top-level decomposition or mandates a pattern, rather
   than settling one local question.
2. **Reusable** — future features of the same kind are expected to follow it every time.
3. **Backbone-defining** — it belongs in the `ARCHITECTURE.md` index where every
   contributor sees it.

If any of the three is missing, skip the SDR. When you write an SDR: put the full record in `docs/sdr/` and add a one-line summary row to the `## Solution Design Strategy` table in `ARCHITECTURE.md` (the summary must match the SDR's
`**Summary:**` line). Use the format in [SDR-FORMAT.md](./SDR-FORMAT.md).