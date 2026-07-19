---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when the user wants to pin down domain terminology or a ubiquitous language, record an architectural decision, or when another skill needs to maintain the domain model.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## Managing the docs

All doc reads, creates, and updates go through `/manage-docs` — it owns the templates for **documents**, and the rules for where each file lives, when to create it (lazily), and how to keep the `ARCHITECTURE.md` indexes in sync. **Read `manage-docs/SKILL.md`** (and the relevant `*-FORMAT.md`) before creating or editing any of these documents, if it isn't already loaded this session — don't rely on recalling its rules from memory.

**Documents**:
- `CONTEXT.md` — the glossary (the *language*).
- `ARCHITECTURE.md` — the structural map, and the index of Concepts and ADRs.
- `docs/concepts/` — Crosscutting Concepts: the backbone rules.
- `docs/adr/` — Architecture Decision Records: localized decisions.

## Load strategy guardrails

Before designing or grilling:

1. If `ARCHITECTURE.md` doesn't exist yet, skip this load strategy — that's "not yet created" (see `/manage-docs` lazy-creation), not a gap to fill.
2. Read `ARCHITECTURE.md` in full: the `Building blocks` → Services list, and the *complete* `Crosscutting Concepts` and `Architecture Decision Records` index tables — every row, not a sample. All three sections are optional in the format (`ARCHITECTURE-FORMAT.md`) — skip gracefully if a section is absent rather than treating it as a gap. If a section spans more than one comfortable read, issue multiple ranged reads covering all of it — never stop at a partial read.
3. **Concepts are presumed in-scope by default** — a Concept is a pattern "every feature is expected to follow" (`CONCEPT-FORMAT.md`), so treat every indexed Concept as applicable to the current design; open its full record for implementation detail (e.g. Exceptions/Examples), not to decide whether it counts. If a Concept row's **Trigger condition** is filled in (narrowing it to specific conditions rather than blanket coverage), match against it the same way as an ADR's: the kind of change in scope (entity/data shape, endpoint, folder, change type) implied by the plan's touched surface, and a cell may list more than one condition (comma-separated) — a match on any one of them is enough to treat the Concept as in-scope. **ADRs are relevance-gated** — they're localized, point-in-time decisions, so open the full record (`docs/adr/{{n}}-{{slug}}.md`) only when relevant. Match primarily against its **Trigger condition** column: the kind of change in scope (entity/data shape, endpoint, folder, change type) implied by the plan's touched surface — not only a keyword the conversation happened to say. A cell may list more than one condition (comma-separated); a match on any one of them is enough to open the record. For rows without a Trigger condition (older index tables), fall back to matching title, summary, or linked module/keyword against a term, folder, or boundary already named in the current scope. This match is the relevance test, not a subjective read of the summary. Apply the same test to a Building-block service's full doc (linked from its Services bullet, `BUILDING-BLOCK-SERVICE-FORMAT.md`) if one exists — services without a linked doc are trivial and the one-line bullet is enough. Leave everything else index-only until it matches. Log each opened record in the session ledger (*Track opened records* below) the moment you open it.
4. Sections inside an opened record are themselves optional (a Concept's Exceptions/Examples; an ADR's Status/Considered Options/Consequences; a service doc's API Contracts/Tweaks/Persisted data/Key features) — a missing one means "not documented," not a gap to fill in during grilling.
5. Extract:
   * **Mandates** — required concepts, patterns and boundaries.
   * **Prohibitions** — explicitly rejected approaches, rejected considered options.
   * **Open space** — unconstrained choices.
6. Use these guardrails to frame questions, scenarios, and alternatives.
* A Concept-violating option must not be presented as equally valid — cite the Concept and surface the conflict.
* An option that contradicts a considered-and-rejected ADR alternative must not be presented as equally valid.

These rules stay active for the whole session, not just at load time — see *Continuously validate against Concepts and ADRs* and *Cross-reference with code* below.

### Track opened records

Persist a session ledger of every Concept/ADR/service doc opened so far via the memory tool, at `/memories/session/domain-model-ledger.md` — create it lazily on first open, one line per record (`{{path}} — opened for {{topic}}`).

Before discussing any module, boundary, or service, check the ledger:
* **Already listed** — its full record is loaded; don't re-open or re-scan the index for it.
* **Not listed** — this is a re-scope: re-run step 2's full index read (the in-context index may now be out of date), re-apply step 3's relevance test, and append the result to the ledger.

Once the ledger grows large, stop re-scanning everything on every re-scope: compress resolved terms and decisions into a short summary, rely on that plus the ledger, and re-open a full record only when a specific detail is needed again.

## During the session

Every probe below stays live for the whole session: re-check its trigger after each user answer, not just once — a later answer can retroactively put an earlier one in conflict.

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When a domain relationship, boundary, or invariant is stated as fact — not just discussed in the abstract — stress-test it with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Challenge which test categories must cover the change

Read the relevant `Testing strategy` section in `ARCHITECTURE.md`. No Testing strategy? Fall back to documented conventions (`Testing.md`, `README.md`) and existing tests in the codebase.

When the plan adds a REST endpoint, external-service integration, persisted entity, or new module, challenge which documented categories must cover it. Consult the `Testing strategy` (or fallback) and explore existing tests — don't default to unit tests. "This adds a repository against the database — your strategy mandates an integration-test category. Which category covers persistence round-trips and queries?"

### Continuously validate against Concepts and ADRs

After every user answer — not just at session start — check it for relevance against every Concept/ADR already known from Load strategy guardrails' index read. Open a full record the first time an entry becomes relevant. Re-read the full index tables only when re-scoping or right after a Concept/ADR is authored/edited — not on every turn. Where a proposal or decision conflicts, classify the gap:
* **Violation** — the proposal breaks a Concept, or repeats an ADR's rejected alternative. Do not present a Concept-violating or rejected-alternative option as equally valid — cite the Concept or ADR by number and surface the conflict.
* **Supersession** — the Concept/ADR is outdated and should be revised.
* **Out of scope** — the Concept/ADR does not apply here.

(Drift — implementation vs. Concept/ADR — is not classified here; it belongs to *Cross-reference with code* below, which already checks the code independently.)

### Surface design improvements

When a proposed structure has a narrower/deeper alternative implied by a loaded Concept, name that Concept and surface it: "This Concept mandates deep modules — could this be one deep module with a narrow interface, instead of three shallow modules that leak their internals to each other?" Once a Concept rules an option out, don't present it as equally valid alongside the compliant one.

### Trace through the layers

When a new flow crosses a layer or a transaction/process/network boundary defined by a loaded Concept, read the relevant `Building blocks` section in `ARCHITECTURE.md` (and the specific service's full doc if one is open, per Load strategy guardrails), then select one representative scenario and trace it end-to-end, naming each layer from the loaded Concept as you go: "Trace 'place order' from the API down to persistence: which layer owns validation, which owns pricing, and where does the transaction boundary sit?" If a shortcut would skip a mandated layer, cite the Concept and surface the conflict rather than presenting the shortcut as equally valid.

Then re-run *Continuously validate against Concepts and ADRs* against the trace.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?", "Must every persisted username be between 3 and 50 characters?". Look up (across user-facing, application, integration, and persistence boundaries): Validation rules, Constraints, Domain concepts, Data models, Contracts, Schemas, Relationships, Business logic.

When the code disagrees with a loaded Concept or ADR, classify it as **Drift** and surface the gap.

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

### Closing completeness sweep

Before concluding a session that opened at least one full Concept/ADR record, output one disposition line per row in the `Crosscutting Concepts` and `Architecture Decision Records` index tables — `Applied`, `Not applicable`, `Violated`, or `Superseded` — so every row gets an explicit verdict instead of silent omission. Skip this sweep for trivial sessions that only touched `CONTEXT.md` glossary terms and never opened a full Concept/ADR record.
