---
name: grill-design
description: A relentless interview and domain-modeling probe set that sharpens a plan or design while surfacing terms, decisions, and assumptions the moment they crystallise. Use when the user wants to stress-test a plan or design, get grilled, pin down domain terminology, record an architectural decision or assumption, or uses any 'grill design' trigger phrases.
---

# Grill Design

Own the interview and the session's design state — *when* to look up, log, ask, or write. Every
*how* is delegated: ledger grammar → `/track-ledger`; index scan/sync → `/index-docs`; doc creation
→ `/bootstrap-docs`; writes → `/record-term`, `/record-adr`, `/record-concept`, `/record-service`;
codebase lookups → `/delegate-explore`. Call them; never restate their rules.

## Session start

1. **Docs exist** — existence check only on `ARCHITECTURE.md` and `CONTEXT.md`; either missing → `/bootstrap-docs`' **Mandatory creation**.
2. **Load the index** — read `ARCHITECTURE.md` in full: `Building blocks` services and every row of the `Crosscutting Concepts` / `Architecture Decision Records` tables. All three sections are optional — absent is not a gap. Multi-part sections need multiple ranged reads; never stop at a partial read.
3. **Claim the ledger** — read `/track-ledger`'s ledger if it exists and confirm it belongs to this session; otherwise start fresh. An inherited `opened` line suppresses a guardrail re-scan for the rest of the session.
4. **Seed the surface** — extract the touched surface from the initial request and run *Scan and match* once; its normal trigger — a user answer — doesn't exist yet.
5. **Interview.**

## Interview

Interview me relentlessly about every aspect of this until we reach a shared understanding. Walk
down each branch of the decision tree, resolving dependencies between decisions one-by-one. Ask
**one question at a time** and wait for the answer — multiple questions at once are bewildering.
Give your recommended answer with each question.

If a *fact* is discoverable in the environment (filesystem, tools), look it up rather than asking.
If a *decision* clears the evidence checklist below, take it as a Feature Assumption rather than
asking; if any part fails, put it to me and wait.

Before confirming we've reached a shared understanding, list every Feature Decision and Feature
Assumption made this session for me to *veto* — one bullet each, 1-3 sentences on what was
decided/assumed and why: `- {{item}}: {{explanation}}`. Do not act until I confirm.

## Decision states

Evidence checklist — all four → Feature Assumption; any miss → ask: single authoritative source;
direct answer (no analogy); no genuine alternative; reversible if wrong.

| State | Resolved by | Home | Durable write |
|---|---|---|---|
| Feature Assumption | model, via the checklist | ledger only | only after the veto sweep clears it — it is then a Decision |
| Feature Decision | user, feature-scoped (fails the ADR/Concept gate, resolves no term) | ledger only | never |
| Decision | user | ledger + document | same turn it's approved |
| Rejected option | user | ledger only | never |

Log every state and every change of state via `/track-ledger`' **Log decision**, the turn it
happens. Authoring choices made while writing docs (synonym lists, term placement, section names,
prose wording) are none of these — don't log or list them.

## Context economy

- Broad-sweep code and test lookups → `/delegate-explore`; direct reads only to quote an exact line.
- Re-fetch a durable artifact when you first need it, or when you need it and can't quote it verbatim from context — never on a schedule, never "just in case", never right after your own write.
- Authority order: `CONTEXT.md`/`ARCHITECTURE.md`/ADR/Concept > code > external sources. A conflict against a higher-ranked source is asked, never assumed.

## Probes

Alongside the interview, build and sharpen the project's domain model — challenging terms, inventing
edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. Merely
*reading* `CONTEXT.md`, `ARCHITECTURE.md`, Concepts, or ADRs for guardrails isn't enough here: this
changes the model, not just consumes it.

Every probe stays live for the whole session: re-check its trigger after each user answer, not just
once — a later answer can retroactively put an earlier one in conflict.

**Glossary conflict** — the user's term clashes with the existing language in `CONTEXT.md`: call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

**Fuzzy language** — vague or overloaded term: propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

**Concrete scenarios** — when a domain relationship, boundary, or invariant is stated as fact — not just discussed in the abstract — invent edge-case scenarios that force precision about the boundaries between concepts.

**Test coverage** — runs on every change. Check the `Crosscutting Concepts` index for a testing/verification Concept. Match → cross-reference it against existing tests and test conventions via `/delegate-explore`, propose add/update/delete. No match → use the code alone. "This adds a repository against the database — your testing Concept mandates an integration-test category. Which category covers persistence round-trips and queries?"

**Scan and match** — on each triggering turn (user answer / new fact), pass any new surface terms to `/track-ledger`' **Append surface term**.
* **No new term** — reason over the in-context index copy; no scan, no write.
* **New term(s)** — run `/index-docs`' **Scan and match** passing only those terms, against the not-yet-`opened` rows only.

This verdict is **monotonic** — once a row matches it stays matched as the surface only grows; never re-check an already-`opened` row here.

**Open and extract** — open a linked full record only on a matching verdict; indexing alone never implies relevance. Log every record you open or skip via `/track-ledger`' **Log opened record**, and check the ledger before discussing any module, boundary, or service — listed means its full record is already loaded, don't re-open or re-scan for it. A section absent from an opened record means "not documented", never "not applicable". Extract **mandates** (required concepts, patterns, boundaries), **prohibitions** (explicitly rejected approaches and considered options), **open space** (unconstrained choices) — and frame every question, scenario, and alternative against them.

**Classify conflicts** — over the full text of already-`opened` records in context; no tool call; re-runs every triggering turn because it is **non-monotonic**: a later answer can retroactively put an earlier design in conflict with a Concept or ADR that matched turns ago.
* **Violation** — breaks a Concept or repeats an ADR's rejected alternative. Never present as equally valid — cite the Concept/ADR number, surface the conflict.
* **Supersession** — the Concept/ADR is outdated, needs revision.
* **Out of scope** — the Concept/ADR doesn't apply.

**Code cross-reference** — when the user states how something works, check whether the code agrees, across user-facing, application, integration, and persistence boundaries: validation rules, constraints, domain concepts, data models, contracts, schemas, relationships, business logic. Contradicts the user → surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?" Contradicts a loaded Concept or ADR → classify it as **Drift** and surface the gap.

**External-source cross-reference** — if the session was seeded from a link or explicit reference to an external source (Jira work item, Confluence page, GitHub issue), track it for the rest of the session. When a statement, decision, or resolved term contradicts it, surface it immediately: "The Jira ticket says X, but you just said Y — which is right?" Once resolved, offer to fix the source at once — never batch: write-capable tool available → apply the fix after the user confirms wording; otherwise tell the user the source is now stale.

**Record inline** — resolved by explicit user answer → run `/record-term`, `/record-adr`, `/record-concept`, or `/record-service` that same turn; the answer is the approval. Resolved by you → it's a Feature Assumption, ledger only (see *Decision states*). Proposing an ADR or Concept unprompted → check the target skill's own gate first, then *offer*, and run it only once the user explicitly responds to that offer.

## Closing sweep

Three parts, each with its own trigger.

**1. Per-row disposition.** If the session opened at least one full Concept/ADR record, emit one verdict per row in the `Crosscutting Concepts` and `Architecture Decision Records` index tables — `Applied`, `Not applicable`, `Violated`, or `Superseded` — so no row is silently omitted. Skip for trivial sessions that only touched glossary terms.

**2. Veto resolution.** Resolve every staged item against the Interview's end-of-session veto list:
* **Cleared** — it is now a Decision: write it to its durable document and update its ledger line via `/track-ledger`' **Log decision**.
* **Vetoed** — delete its ledger line via `/track-ledger`' **Log decision**; nothing changes on disk.

A recorded Decision is not vetoable — the user approved it before it was written.

**3. Trigger-condition refinement.** Per row, check the **Trigger condition** cell for a gap this session exposed (missed clause, summary-based match, blank cell). If found, refine the clause and apply it via `/index-docs`' **Sync index row**.