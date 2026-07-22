---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when the user wants to pin down domain terminology or a ubiquitous language, record an architectural decision, or when another skill needs to maintain the domain model.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `CONTEXT.md`, `ARCHITECTURE.md`, Concepts, or ADRs for guardrails is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## Managing the docs

All doc reads, creates, and updates go through `/manage-docs` — it owns document templates, file locations, lazy-creation rules, and `ARCHITECTURE.md` index sync. **Invoke `/manage-docs`** (and the relevant `*-FORMAT.md`) before touching any of these documents, if not already loaded this session — don't recall its rules from memory.

**Documents**:
- `CONTEXT.md` — glossary (the *language*).
- `ARCHITECTURE.md` — structural map + Concepts/ADRs index.
- `docs/concepts/` — Crosscutting Concepts: backbone rules.
- `docs/adr/` — ADRs: localized decisions.

## Load strategy guardrails

Before designing or grilling:

1. If `ARCHITECTURE.md` doesn't exist yet, skip *this load step only* — nothing to load. Creation still applies once a term, rule, Concept, or ADR is ready to capture (`/manage-docs`'s `Lazy creation` rule; see *Update CONTEXT.md inline*, *Update ADRs and Concepts inline*, *Offer ADRs/Concepts sparingly*).
2. Read `ARCHITECTURE.md` in full: `Building blocks` → Services list, and the complete `Crosscutting Concepts`/`Architecture Decision Records` index tables — every row. All three sections are optional (`ARCHITECTURE-FORMAT.md`) — skip gracefully if absent, don't treat as a gap. Multi-part sections need multiple ranged reads — never stop at a partial read.
3. **Match Concepts/ADRs mechanically via the Trigger condition column** — indexing alone never implies relevance. Blank cell = documentation gap, not universal coverage. Per row: split the cell on commas into clauses; check literally against the current change's touched surface (entity/data shape, endpoint, folder, change type); any single clause match opens the full record (`docs/concepts/{{n}}-{{slug}}.md` or `docs/adr/{{n}}-{{slug}}.md`). Never substitute the title/summary for this test. Apply the same test to a Building-block service's full doc if one is linked (`BUILDING-BLOCK-SERVICE-FORMAT.md`) — unlinked services are trivial, the one-line bullet suffices. Non-matching rows stay index-only. Log every check in the session ledger (*Track opened records*): matches as `{{n}} — opened, trigger matched: "{{clause}}"`; non-matches as `{{n}} — skipped, checked "{{clause1}}", "{{clause2}}": neither touched`.
4. Sections inside an opened record are themselves optional (a Concept's Exceptions/Examples; an ADR's Status/Considered Options/Consequences; a service doc's API Contracts/Tweaks/Persisted data/Key features) — a missing one means "not documented."
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

### Delegate code lookups to `explore`

Every turn resends the whole transcript — raw tool output pulled into this context gets re-billed on every later turn. Default broad-sweep code checks (does this pattern/behavior exist elsewhere? who calls this? is the code's claim true across files/layers?) to the `explore` agent (`runSubagent`); consume only its condensed verdict, don't re-`view`/`grep` files it already reported. Reserve direct reads (targeted `view`/`grep`) for anchor-precision — the exact line, signature, or assertion needed to quote back to the user. Governs *Cross-reference with code*, *Trace through the layers*, and *Challenge which test categories must cover the change* below.

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When a domain relationship, boundary, or invariant is stated as fact — not just discussed in the abstract — stress-test it with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Challenge which test categories must cover the change

Always runs, every change. Check `Crosscutting Concepts` index in `ARCHITECTURE.md` for a testing/verification Concept. Match found → cross-reference it against existing tests and test conventions via `explore` (per *Delegate code lookups* above), reserving direct reads for citing the exact test file/assertion; propose add/update/delete. No match → use the code alone.

"This adds a repository against the database — your testing Concept mandates an integration-test category. Which category covers persistence round-trips and queries?"

### Continuously validate against Concepts and ADRs

After every user answer, re-run step 3's Trigger-condition match against every known Concept/ADR row (index read, or compressed summary + ledger once threshold hit) — mandatory, not optional; a later answer can newly touch a clause a row names. First time a row becomes relevant this way: open it, log the matched clause per step 3. No match: log checked-no-match per step 3. Re-read full index tables only on re-scope (per *Track opened records*) or right after authoring/editing a Concept/ADR — not every turn. Classify conflicts:
* **Violation** — breaks a Concept or repeats an ADR's rejected alternative. Never present as equally valid — cite the Concept/ADR number, surface the conflict.
* **Supersession** — Concept/ADR is outdated, needs revision.
* **Out of scope** — Concept/ADR doesn't apply.

(Drift — code vs. Concept/ADR — handled by *Cross-reference with code* below, not here.)

### Surface design improvements

When a proposed structure has a narrower/deeper alternative implied by a loaded Concept, name that Concept and surface it: "This Concept mandates deep modules — could this be one deep module with a narrow interface, instead of three shallow modules that leak their internals to each other?" Once a Concept rules an option out, don't present it as equally valid alongside the compliant one.

### Trace through the layers

When a new flow crosses a layer or a transaction/process/network boundary defined by a loaded Concept, read the relevant `Building blocks` section in `ARCHITECTURE.md` (and the specific service's full doc if one is open, per Load strategy guardrails), then select one representative scenario and trace it end-to-end, naming each layer from the loaded Concept as you go: "Trace 'place order' from the API down to persistence: which layer owns validation, which owns pricing, and where does the transaction boundary sit?" If a shortcut would skip a mandated layer, cite the Concept and surface the conflict rather than presenting the shortcut as equally valid.

When the trace needs to confirm what the code actually does at a layer (not just what `ARCHITECTURE.md` says), default that confirmation to `explore` (per *Delegate code lookups* above); reserve direct reads for anchoring the exact boundary line.

Then re-run *Continuously validate against Concepts and ADRs* against the trace.

### Cross-reference with code

When the user states how something works, check whether the code agrees. Default that lookup to `explore` (per *Delegate code lookups* above); reserve direct reads for the exact contradicting line to quote. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?", "Must every persisted username be between 3 and 50 characters?". Look up (across user-facing, application, integration, and persistence boundaries): Validation rules, Constraints, Domain concepts, Data models, Contracts, Schemas, Relationships, Business logic.

When the code disagrees with a loaded Concept or ADR, classify it as **Drift** and surface the gap.

### Cross-reference with external source

If the session was seeded from a link or explicit reference to an external source (Jira work item, Confluence page, GitHub issue) at session start, track it for the rest of the session.

When a user statement, decision, or resolved term contradicts that source, surface it immediately: "The Jira ticket says X, but you just said Y — which is right?"

Once resolved, offer to fix the source immediately — never batch it. Detect whether a write-capable tool for that source type is available; if so, apply the fix after the user confirms wording; if not, tell the user the source is now stale and let them update it.

### Update CONTEXT.md inline

When a term is resolved: if `CONTEXT.md` doesn't exist yet, create it via `/manage-docs` (per its `## Lazy creation` rule), then capture the term right there — don't batch these up, capture them as they happen.

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Update ADRs and Concepts inline

When an ADR or Concept is resolved: if `ARCHITECTURE.md` (or `docs/adr/` / `docs/concepts/`) doesn't exist yet, create it via `/manage-docs` (per its `## Lazy creation` rule) first, then capture it in `ARCHITECTURE.md` right there via `/manage-docs` skill `Inline-update discipline` — don't batch these up, capture them as they happen.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR; otherwise the offer itself is the approval gate — draft it, present it, and only capture it via `/manage-docs` skill `Inline-update discipline` (which owns the ADR template) once the user explicitly responds to that specific offer. If `docs/adr/` (or `ARCHITECTURE.md`) doesn't exist yet, that capture step creates it first, per `/manage-docs`' `## Lazy creation` rule.

### Offer Concepts sparingly

A Concept captures a *backbone* decision: the top-level decomposition, or a mandated architectural/design pattern that every feature of a given kind must follow. Write one (instead of, or in addition to, an ADR) only when all three are true:

1. **Structural** — it shapes the top-level decomposition or mandates a pattern, rather than settling one local question.
2. **Reusable** — future features of the same kind are expected to follow it every time.
3. **Backbone-defining** — it is the set of foundational decisions that hold the architecture together and constrain everything built on top of them.

If any of the three is missing, skip the Concept; otherwise the offer itself is the approval gate — draft it, present it, and only capture it via the `manage-docs` skill `Inline-update discipline` section once the user explicitly responds to that specific offer. If `docs/concepts/` (or `ARCHITECTURE.md`) doesn't exist yet, that capture step creates it first, per `/manage-docs`' `## Lazy creation` rule.

### Closing completeness sweep

Before concluding a session that opened at least one full Concept/ADR record, output one disposition line per row in the `Crosscutting Concepts` and `Architecture Decision Records` index tables — `Applied`, `Not applicable`, `Violated`, or `Superseded` — so every row gets an explicit verdict instead of silent omission. Skip this sweep for trivial sessions that only touched `CONTEXT.md` glossary terms and never opened a full Concept/ADR record.

Per row, also check the **Trigger condition** cell for a gap this session exposed (missed clause, summary-based match, blank cell). If found, refined clause and apply it via `manage-docs` inline-update discipline.
