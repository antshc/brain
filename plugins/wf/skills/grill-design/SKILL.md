---
name: grill-design
description: A relentless interview that sharpens a plan or design while actively building the project's domain model — glossary, ADRs, Crosscutting Concepts, ARCHITECTURE.md — capturing terms, decisions, and assumptions the moment they crystallise. Use when the user wants to stress-test a plan or design, get grilled, pin down domain terminology, record an architectural decision or assumption, or uses any 'grill' trigger phrases.
---

# Grill Design

## Interview

Interview me relentlessly about every aspect of this until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.

If a *fact* can be found by exploring the environment (filesystem, tools, etc.), look it up rather than asking me.

For *decisions*: evaluate against the evidence checklist — single authoritative source, direct answer (no analogy), no genuine alternative, reversible if wrong. All four met → record as *feature assumption*. If any one fails, it's not strong enough — put it to me, wait for answer.

A Feature Assumption (model-resolved) and a Feature Decision (user-approved but feature-scoped) are both held in the session Ledger only — never written to `CONTEXT.md`, an ADR, or a Concept; only a Decision destined for a durable document is.

Before confirming we've reached a shared understanding, list every Feature Decision and Feature Assumption made this session for me to *veto*. Authoring/editorial choices made while writing docs (synonym lists, term placement, section names, prose wording) are neither and don't belong on this list.

Output format: one bullet per item, each a 1-3 sentence explanation of what was decided/assumed and why — `- {{item}}: {{explanation}}`.

Do not act on it until I confirm we have reached a shared understanding.

## Domain Modeling

Alongside the interview, actively build and sharpen the project's domain model as you design — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. Merely *reading* `CONTEXT.md`, `ARCHITECTURE.md`, Concepts, or ADRs for guardrails isn't enough here: grill-design changes the model, not just consumes it.

### Managing the docs

All doc reads, creates, and updates go through `/manage-docs` — it owns document templates, file locations, lazy-creation rules, and `ARCHITECTURE.md` index sync. **Invoke `/manage-docs`** (and the relevant `*-FORMAT.md`) before touching any of these documents, if not already loaded this session — don't recall its rules from memory.

**Documents**:
- `CONTEXT.md` — glossary (the *language*).
- `ARCHITECTURE.md` — structural map + Concepts/ADRs index.
- `docs/concepts/` — Crosscutting Concepts: backbone rules.
- `docs/adr/` — ADRs: localized decisions.

### Load strategy guardrails

Before designing or grilling:

1. If `ARCHITECTURE.md` doesn't exist yet, offer to create it right away, per `/manage-docs`'s `Lazy creation` rule — don't wait for a term, rule, Concept, or ADR to be ready to capture (that's a separate trigger; see *Update CONTEXT.md inline*, *Update ADRs and Concepts inline*, *Offer ADRs/Concepts sparingly*). Once created, skip *this load step only* — nothing beyond the required sections exists yet to read.
2. Read `ARCHITECTURE.md` in full: `Building blocks` → Services list, and the complete `Crosscutting Concepts`/`Architecture Decision Records` index tables — every row. All three sections are optional (`ARCHITECTURE-FORMAT.md`) — skip gracefully if absent, don't treat as a gap. Multi-part sections need multiple ranged reads — never stop at a partial read.
3. **Match applicable records via `/trigger-indexer` Scan and match** — indexing alone never implies relevance; delegate semantic Trigger-condition matching to `/trigger-indexer`, passing the caller-supplied table metadata, the current change's touched surface, grilling context, and glossary. Use it for Services, ADRs, Concepts, or any other indexed table; open a linked full record only when the returned verdict matches. Log every returned verdict in the session ledger's `Opened records` section (*Track opened records*): matches as `{{path}} — opened, trigger matched: "{{clause}}"`; non-matches as `{{path}} — skipped, checked "{{clause1}}", "{{clause2}}": no semantic match`.
4. Sections inside an opened record are themselves optional (a Concept's Exceptions/Examples; an ADR's Considered Options/Consequences; a service doc's API Contracts/Tweaks/Persisted data/Key features) — a missing one means "not documented."
5. Extract:
   * **Mandates** — required concepts, patterns and boundaries.
   * **Prohibitions** — explicitly rejected approaches, rejected considered options.
   * **Open space** — unconstrained choices.
6. Use these guardrails to frame questions, scenarios, and alternatives.
* A Concept-violating option must not be presented as equally valid — cite the Concept and surface the conflict.
* An option that contradicts a considered-and-rejected ADR alternative must not be presented as equally valid.

These rules stay active for the whole session, not just at load time — see *Continuously validate against Concepts and ADRs* and *Cross-reference with code* below.

#### Track opened records

Persist a session ledger via the memory tool, at `/memories/session/domain-model-ledger.md` — create it lazily on the first write of any kind. It has three sections; this subsection covers `Opened records` only.

One line per record, path-anchored (never a row number — numbers renumber on index sync and collide across tables), no ranges:
* `{{path}} — opened, trigger matched: "{{clause}}"`
* `{{path}} — opened, direct: {{topic}}`
* `{{path}} — skipped, checked "{{clause1}}", "{{clause2}}": no match`

Before discussing any module, boundary, or service, check the ledger:
* **Already listed** — its full record is loaded; don't re-open or re-scan the index for it.
* **Not listed** — see *Track the touched surface* below; whether this is a re-scope depends on whether the discussion introduces a new surface term.

Once the ledger grows large, stop re-scanning everything on every re-scope: compress resolved terms and decisions into a short summary, rely on that plus the ledger, and re-open a full record only when a specific detail is needed again.

#### Track the touched surface

The ledger's `Touched surface` section accumulates surface terms extracted from user answers: module, boundary, service, entity, data shape, behavior, interface, change type. This is the cache key that makes a `skipped` verdict re-checkable — it was only ever valid for the surface known at that turn.

On each triggering turn (user answer / new fact):
* **No new surface term** — reason over the in-context index copy; no scan, no write.
* **New term(s)** — append them to `Touched surface`, then run `/trigger-indexer` **Scan and match** passing only the new terms, against the not-yet-`opened` rows only. Update existing row lines in place; never append a duplicate.

#### Stage decisions and assumptions in the ledger

The moment grilling resolves a decision as a *feature assumption* (its evidence checklist is met, so no question asked), log it in the ledger's `Decisions / assumptions` section — `{{item}} — assumed, evidence: "{{source}}"`. This is its only home: a Feature Assumption is never written to `CONTEXT.md`, an ADR, or a Concept. It stays ledger-only until grilling's end-of-session veto list clears or vetoes it (see *Closing completeness sweep*) — clearing is what turns it into a Decision and triggers the durable write, not the feature assumption itself.

A user-approved Decision that is feature-scoped (a Feature Decision — fails the ADR/Concept gate, resolves no glossary term) is also ledger-only, permanently: log it `{{item}} — decided by user, feature decision, grounded: "{{source}}"`. A user-approved Decision destined for a durable document is logged and written the same turn it's approved: `{{item}} — decided by user, recorded: {{path}}` (per *Update CONTEXT.md inline* / *Update ADRs and Concepts inline* below). A rejected option is logged `{{item}} — rejected, reason: "{{source}}"`.

### During the session

Every probe below stays live for the whole session: re-check its trigger after each user answer, not just once — a later answer can retroactively put an earlier one in conflict.

#### Delegate code lookups to `explore`

Raw tool output re-bills every later turn. Default broad-sweep code checks (pattern exists elsewhere? who calls this? is the claim true across layers?) to the `explore` agent (`runSubagent`); consume only its verdict — don't re-`view`/`grep` files it reported. Reserve direct `view`/`grep` for anchor-precision: the exact line/signature/assertion to quote back. Governs *Cross-reference with code* and *Challenge which test categories must cover the change* below.

#### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

#### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

#### Discuss concrete scenarios

When a domain relationship, boundary, or invariant is stated as fact — not just discussed in the abstract — stress-test it with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

#### Challenge which test categories must cover the change

Always runs, every change. Check `Crosscutting Concepts` index in `ARCHITECTURE.md` for a testing/verification Concept. Match found → cross-reference it against existing tests and test conventions via `explore` (per *Delegate code lookups* above), reserving direct reads for citing the exact test file/assertion; propose add/update/delete. No match → use the code alone.

"This adds a repository against the database — your testing Concept mandates an integration-test category. Which category covers persistence round-trips and queries?"

#### Scan and match (surface-driven)

Driven entirely by *Track the touched surface* above: a `/trigger-indexer` **Scan and match** call happens only when the touched surface gains a new term, scoped to that term, against not-yet-`opened` rows. This verdict is **monotonic** — once a row matches, it stays matched as the surface only grows; there's no need to re-check an already-`opened` row here.

#### Classify conflicts

Distinct from *Scan and match*: this operates on the full text of already-`opened` records already in context — no tool call — and re-runs every triggering turn, because it is **non-monotonic**: a later answer can retroactively put an earlier design in conflict with a Concept or ADR that matched turns ago.

* **Violation** — breaks a Concept or repeats an ADR's rejected alternative. Never present as equally valid — cite the Concept/ADR number, surface the conflict.
* **Supersession** — Concept/ADR is outdated, needs revision.
* **Out of scope** — Concept/ADR doesn't apply.

(Drift — code vs. Concept/ADR — handled by *Cross-reference with code* below, not here.)

#### Re-fetch rule

Applies to every durable artifact (`ARCHITECTURE.md`, an ADR, a Concept, `CONTEXT.md`): fetch when you first need it, or when you need it and cannot quote the needed part verbatim from context. Never on a schedule, never "just in case," and never right after your own write — every write path already returns its result.

#### Source-authority precedence

Resolve authority disagreements — including the evidence checklist's *single authoritative source* test — in this order: `CONTEXT.md`/`ARCHITECTURE.md`/ADR/Concept > code > external sources. A lower-ranked source never outweighs a higher-ranked one; conflict against a higher-ranked source must be asked, not assumed.

#### Cross-reference with code

When the user states how something works, check whether the code agrees. Default that lookup to `explore` (per *Delegate code lookups* above); reserve direct reads for the exact contradicting line to quote. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?", "Must every persisted username be between 3 and 50 characters?". Look up (across user-facing, application, integration, and persistence boundaries): Validation rules, Constraints, Domain concepts, Data models, Contracts, Schemas, Relationships, Business logic.

When the code disagrees with a loaded Concept or ADR, classify it as **Drift** and surface the gap.

#### Cross-reference with external source

If the session was seeded from a link or explicit reference to an external source (Jira work item, Confluence page, GitHub issue) at session start, track it for the rest of the session.

When a user statement, decision, or resolved term contradicts that source, surface it immediately: "The Jira ticket says X, but you just said Y — which is right?"

Once resolved, offer to fix the source immediately — never batch it. Detect whether a write-capable tool for that source type is available; if so, apply the fix after the user confirms wording; if not, tell the user the source is now stale and let them update it.

#### Update CONTEXT.md inline

When a term is resolved by explicit user answer: if `CONTEXT.md` doesn't exist yet, create it via `/manage-docs` (per its `## Lazy creation` rule), then capture the term right there — don't batch these up, capture them as they happen.

When resolved by a feature assumption instead, follow *Stage decisions and assumptions in the ledger*: it stays ledger-only, not written here, until the closing veto sweep clears it into a Decision — that clearing is the write trigger.

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

#### Update ADRs and Concepts inline

When an ADR or Concept is resolved by explicit user answer: if `ARCHITECTURE.md` (or `docs/adr/` / `docs/concepts/`) doesn't exist yet, create it via `/manage-docs` (per its `## Lazy creation` rule) first, then capture it in `ARCHITECTURE.md` right there via `/manage-docs` skill `Inline-update discipline` — don't batch these up, capture them as they happen.

When resolved by a feature assumption instead, follow *Stage decisions and assumptions in the ledger*: it stays ledger-only until the closing veto sweep clears it into a Decision — that clearing is the write trigger, not the feature assumption itself.

#### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR; otherwise the offer itself is the approval gate — draft it, present it, and only capture it via `/manage-docs` skill `Inline-update discipline` (which owns the ADR template) once the user explicitly responds to that specific offer. If `docs/adr/` (or `ARCHITECTURE.md`) doesn't exist yet, that capture step creates it first, per `/manage-docs`' `## Lazy creation` rule.

#### Offer Concepts sparingly

A Concept captures a *backbone* decision: the top-level decomposition, or a mandated architectural/design pattern that every feature of a given kind must follow. Write one (instead of, or in addition to, an ADR) only when all three are true:

1. **Structural** — it shapes the top-level decomposition or mandates a pattern, rather than settling one local question.
2. **Reusable** — future features of the same kind are expected to follow it every time.
3. **Backbone-defining** — it is the set of foundational decisions that hold the architecture together and constrain everything built on top of them.

If any of the three is missing, skip the Concept; otherwise the offer itself is the approval gate — draft it, present it, and only capture it via the `manage-docs` skill `Inline-update discipline` section once the user explicitly responds to that specific offer. If `docs/concepts/` (or `ARCHITECTURE.md`) doesn't exist yet, that capture step creates it first, per `/manage-docs`' `## Lazy creation` rule.

#### Closing completeness sweep

Before concluding a session that opened at least one full Concept/ADR record, output one disposition line per row in the `Crosscutting Concepts` and `Architecture Decision Records` index tables — `Applied`, `Not applicable`, `Violated`, or `Superseded` — so every row gets an explicit verdict instead of silent omission. Skip this sweep for trivial sessions that only touched `CONTEXT.md` glossary terms and never opened a full Concept/ADR record.

Also resolve every entry logged under *Stage decisions and assumptions in the ledger* against the Interview section's end-of-session veto list:
* **Cleared** — it becomes a user-approved Decision; write it to its durable document now (per *Update CONTEXT.md inline* / *Update ADRs and Concepts inline*) and update its ledger line to `decided by user, recorded: {{path}}`.
* **Vetoed** — delete its ledger line; nothing changes on disk, because a Feature Assumption was never written to a durable document.

A Recorded decision is not vetoable — the user approved it before it was written.

Per row, also check the **Trigger condition** cell for a gap this session exposed (missed clause, summary-based match, blank cell). If found, refine the clause and apply it via `/trigger-indexer` **Keeping the indexes in sync**.