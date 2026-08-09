---
name: grill-design
description: A relentless interview and domain-modeling probe set that sharpens a plan or design while surfacing terms, decisions, and assumptions the moment they crystallise. Use when the user wants to stress-test a plan or design, get grilled, pin down domain terminology, record an architectural decision or assumption, or uses any 'grill', 'grilling' trigger phrases.
---

# Grill Design

Own the interview and the session's design state — *when* to look up, log, ask, or write. Every *how* is delegated: ledger grammar → `/track-ledger`; index scan/sync → `/index-docs`; doc creation → `/bootstrap-docs`; writes → `/record-term`, `/record-adr`, `/record-concept`, `/record-service`; codebase lookups → `/delegate-explore`. Call them; never restate their rules.

## Session start

1. **Docs exist** — existence check only on `ARCHITECTURE.md` and `CONTEXT.md`; either missing → run `/bootstrap-docs`' **Mandatory creation**.
2. **Load the index** — read `ARCHITECTURE.md` in full: `Building blocks` services and every row of the `Crosscutting Concepts` / `Architecture Decision Records` tables. All three sections are optional — absent is not a gap. Multi-part sections need multiple ranged reads; never stop at a partial read.
3. **Claim the ledger** — read `/track-ledger`'s ledger if it exists and confirm it belongs to this session; otherwise start fresh. An inherited `opened` line suppresses a guardrail re-scan for the rest of the session.
4. **Seed the surface** — extract the touched surface from the initial request — terms **and** any concrete file/folder paths it names — and run *Scan and match* once; its normal trigger — a user answer — doesn't exist yet.
5. **Interview.**

## Interview

Interview me relentlessly about every aspect of this until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. Ask **one question at a time** and wait for the answer — multiple questions at once are bewildering. Give your recommended answer with each question.

If a *fact* is discoverable in the environment (filesystem, tools), look it up rather than asking. If a *decision* clears the evidence checklist below, take it as a Feature Assumption rather than asking; if any part fails, put it to me and wait.

Before confirming we've reached a shared understanding, list every Feature Decision and Feature Assumption made this session for me to *veto* — one bullet each, 1-3 sentences on what was decided/assumed and why: `- {{item}}: {{explanation}}`. Do not act until I confirm.

## Decision states

Evidence checklist — all three → Feature Assumption; any miss → ask.

* **Single authoritative source** — exactly one matched record's `owns` covers the decision area. Zero owners, or two or more, → ask.
* **Direct answer (no analogy)** — a matched record carries a `default` for this decision, or a `Rules` line that answers it normatively. A `Reference:` / "follow its shape" pointer never clears this gate.
* **No genuine alternative** — the record's `default` names the choice to take when the design doesn't state one. Alternatives listed without a default don't clear it.

| State | Resolved by | Home | Durable write |
|---|---|---|---|
| Feature Assumption | model, via the checklist | ledger only | only after the veto sweep clears it — it is then a Decision. Never a *new* ADR/Concept: the record whose `owns`/`default` cleared the checklist already covers it |
| Feature Decision | user, feature-scoped (fails the ADR/Concept gate, resolves no term) | ledger only | never |
| Offered record | you, pending the user's reply to a specific offer | ledger only | on the user's yes, same turn |
| Decision | user | ledger + document | same turn it's approved |
| Rejected option | user | ledger only | never |

Log every state and every change of state via `/track-ledger`' **Log decision**, the turn it happens. Every question you ask *because a gate missed* is logged the same turn via that skill's gate-miss form — it is the closing sweep's harvest input, and an unlogged miss is a lost repair. **Every question you ask is by definition a gate miss** (a cleared checklist never asks), so every question MUST get a gate-miss line naming which gate failed and the nearest source — even when it also produces a Feature Decision. A `decided by user, feature decision` line is **not** a substitute for the gate-miss line and never replaces it: a feature-scoped decision that no record `owns` is *both* a Feature Decision *and* a `gate miss: single-authoritative-source, nearest source: none` (a new-record candidate), so log both lines. Only decisions you never had to ask (checklist cleared → Feature Assumption) carry no gate-miss line. Authoring choices made while writing docs (synonym lists, term placement, section names, prose wording) are none of these — don't log or list them.

## Context economy

- Broad-sweep code and test lookups → run `/delegate-explore`; direct reads only to quote an exact line.
- Re-fetch a durable artifact when you first need it, or when you need it and can't quote it verbatim from context — never on a schedule, never "just in case", never right after your own write.
- Authority order: `CONTEXT.md`/`ARCHITECTURE.md`/ADR/Concept > code > external sources. A conflict against a higher-ranked source is asked, never assumed.

## Probes

Alongside the interview, build and sharpen the project's domain model — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. Merely *reading* `CONTEXT.md`, `ARCHITECTURE.md`, Concepts, or ADRs for guardrails isn't enough here: this changes the model, not just consumes it.

Every probe stays live for the whole session: re-check its trigger after each user answer, not just once — a later answer can retroactively put an earlier one in conflict.

**Glossary conflict** — the user's term clashes with the existing language in `CONTEXT.md`: call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

**Fuzzy language** — vague or overloaded term: propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

**Concrete scenarios** — when a domain relationship, boundary, or invariant is stated as fact — not just discussed in the abstract — invent edge-case scenarios that force precision about the boundaries between concepts.

**Test coverage** — runs on every change. Check the `Crosscutting Concepts` index for a testing/verification Concept. Match → cross-reference it against existing tests and test conventions via `/delegate-explore`, propose add/update/delete. No match → use the code alone. "This adds a repository against the database — your testing Concept mandates an integration-test category. Which category covers persistence round-trips and queries?"

**Scan and match** — on each triggering turn (user answer / new fact), run `/track-ledger`' **Append surface term** with any new surface terms **and any concrete file/folder paths** newly surfaced — by the user, by *Code cross-reference*, or by a `/delegate-explore` result. Paths go in verbatim and repo-relative; they are what lets a record's `applies_to` globs participate in the verdict.
* **Nothing new** — reason over the in-context index copy; no scan, no write.
* **New term(s) or path(s)** — run `/index-docs`' **Scan and match** passing only those, against the not-yet-`opened` rows only.

This verdict is **monotonic** — once a row matches it stays matched as the surface only grows; never re-check an already-`opened` row here. A match earned from `applies_to` rather than a trigger clause is a signal the row's Trigger condition cell has a gap — carry it to the closing sweep's *Trigger-condition refinement*.

**Open and extract** — open a linked record's **body** only on a matching verdict; indexing alone never implies relevance. (Its frontmatter is not gated — `/index-docs` reads that during the scan itself.) Log every record you open or skip via `/track-ledger`' **Log opened record**, and check the ledger before discussing any module, boundary, or service — listed means its full record is already loaded, don't re-open or re-scan for it. A section absent from an opened record means "not documented", never "not applicable". Extract **mandates** (required concepts, patterns, boundaries), **prohibitions** (explicitly rejected approaches and considered options), **open space** (unconstrained choices), **defaults** (the `default` and `owns` frontmatter keys — the choice to take when the design doesn't state one, and the decision areas this record has sole authority over) — and frame every question, scenario, and alternative against them.

**Classify conflicts** — over the full text of already-`opened` records in context; no tool call; re-runs every triggering turn because it is **non-monotonic**: a later answer can retroactively put an earlier design in conflict with a Concept or ADR that matched turns ago.
* **Violation** — breaks a Concept or repeats an ADR's rejected alternative. Never present as equally valid — cite the Concept/ADR number, surface the conflict.
* **Supersession** — the Concept/ADR is outdated, needs revision.
* **Out of scope** — the Concept/ADR doesn't apply.

**Code cross-reference** — when the user states how something works, check whether the code agrees, across user-facing, application, integration, and persistence boundaries: validation rules, constraints, domain concepts, data models, contracts, schemas, relationships, business logic. Contradicts the user → surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?" Contradicts a loaded Concept or ADR — its rules, or its `default`/`owns` keys — → classify it as **Drift**, log it via `/track-ledger`' drift form, and surface the gap.

**External-source cross-reference** — if the session was seeded from a link or explicit reference to an external source (Jira work item, Confluence page, GitHub issue), track it for the rest of the session. When a statement, decision, or resolved term contradicts it, surface it immediately: "The Jira ticket says X, but you just said Y — which is right?" Once resolved, offer to fix the source at once — never batch: write-capable tool available → apply the fix after the user confirms wording; otherwise tell the user the source is now stale.

**Record inline** — resolved by explicit user answer → run `/record-term`, `/record-adr`, `/record-concept`, or `/record-service` that same turn; the answer is the approval. Resolved by you → it's a Feature Assumption, ledger only (see *Decision states*).

**Offer a record** — you spot an ADR- or Concept-worthy decision no user answer asked you to record. Run the target skill's own gate; it passes → offer that same turn, before your next interview question, as one bullet: `Offer — {{ADR|Concept}} "{{title}}": {{one sentence on what it pins down}}. Record it now?`. Draft nothing until the reply. **Yes** → run `/record-adr` or `/record-concept` immediately. **Not yet / no** → log it via `/track-ledger`' **Log decision** and move on. One open offer at a time — wait for the reply, same as interview questions. Never carry a candidate past the turn it crystallised, never bundle two offers, never make a first-time offer in the closing sweep.

## Closing sweep

Four parts, each with its own trigger. The sweep **repairs** existing records; it never authors a design record — those are written inline the turn they crystallise, and a candidate that never got its inline offer is a miss, not sweep work.

**1. Per-row disposition.** If the session opened at least one full Concept/ADR record, emit one verdict per row in the `Crosscutting Concepts` and `Architecture Decision Records` index tables — `Applied`, `Not applicable`, `Violated`, or `Superseded` — so no row is silently omitted. Skip for trivial sessions that only touched glossary terms.

**2. Veto resolution.** Never skipped — it is the only check on an assumption before it reaches disk, and part 3 reads its outcome. Resolve every staged item against the Interview's end-of-session veto list:
* **Cleared** — it is now a Decision: write it to its durable document and update its ledger line via `/track-ledger`' **Log decision**.
* **Vetoed** — nothing changes on disk. Rewrite its ledger line via `/track-ledger`' **Log decision**: the veto form when the assumption stood on a record's `default`/`owns` (part 3 repairs that key), a deletion otherwise.

A recorded Decision is not vetoable — the user approved it before it was written. An offer never made inline is a miss, not an agenda item — the sweep may re-raise a *deferred* offer, never introduce a new one.

**3. Assumption-gap harvest.** Never skipped, and never reported "no gaps" without the reconciliation below — it runs after part 2, so it sees its outcomes. Every question asked, wrong default, and drifted key marks a gap in the source behind it — close it now, or the next session asks the same question.

**Reconciliation first (the anti-skip guard).** Before repairing anything, enumerate *every* user-answered question logged this session and map each to exactly one of: (a) a checklist-cleared Feature Assumption you never asked — no gap; (b) a question an existing record's `default`/`owns` answered directly — cite `path#key`, no gap; (c) a logged gate-miss line. Any question that lands in none of the three is an **unlogged miss** (the ask-time gate-miss line was dropped) — reconstruct its gate-miss line now, then repair it like the rest. An empty gap-form list is a valid outcome only *after* this enumeration confirms every question is an (a) or (b); reaching "no repairs" without enumerating the questions is itself the skip this step exists to prevent.

Then repair the record behind each of the ledger's three gap forms:
* **Gap miss** (`asked, gate miss:`) — the answer had no source. Fix: add the missing `default` or `owns` to the record named as nearest source; no record can host it → log it via `/track-ledger`' **Log decision** as a next-session candidate and stop — authoring it here is the first-time offer *Offer a record* forbids.
* **Veto** (`vetoed, evidence was:`) — a `default`/`owns` produced an assumption you struck; the key is wrong or too broad. Fix: correct that key. This is the only signal a *wrong* default ever produces — it yields a confident assumption, never a question.
* **Drift** (`drift, code contradicts:`) — a key the code contradicts. Fix: correct it, or mark the anchor "verify — may drift".

Write the fix without a second approval when its content is an answer the user already gave this session — the answer was the approval, same as *Record inline*. Everything else — a key change no answer covers — goes through *Offer a record*'s one-open-offer rule, which here may only re-raise an offer deferred inline. Apply each write via `/record-concept` or `/record-adr`, resync the row via `/index-docs`' **Sync index row**, and mark the ledger line resolved.

**4. Trigger-condition refinement.** Runs last, so it also covers any row part 3 just resynced. Per row, check the **Trigger condition** cell for a gap this session exposed (missed clause, summary-based match, `applies_to`-only match, blank cell). If found, refine the clause and apply it via `/index-docs`' **Sync index row**.
