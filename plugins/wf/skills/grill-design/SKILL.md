---
name: grill-design
description: A relentless interview and domain-modeling probe set that sharpens a plan or design while surfacing terms, feature decisions, and assumptions. Use when the user wants to stress-test a plan or design, get grilled, pin down domain terminology, or uses any 'grill design', 'grilling design' trigger phrases.
---

# Grill Design

Own the interview and the session's design state — *when* to look up, log, ask, or write. Every *how* is delegated: ledger grammar → `/track-ledger`; index scan/sync → `/index-docs`; doc creation → `/bootstrap-docs`; term writes → `/record-term`; Concept repairs → `/record-concept`; codebase lookups → `/explore-codebase`. Call them; never restate their rules.

## Scope

The grill produces exactly two things: **questions** and **records**. Writable surface for the whole session — `CONTEXT.md`, `ARCHITECTURE.md`, `docs/concepts/**`, `docs/services/**`, and the ledger. Source code, tests, configuration, and scaffolding are **read-only** for the entire session: reading them is the job (`/explore-codebase`), changing them is a different session.

**Concepts are consumed, not discovered.** The grill matches, opens, and applies recorded Concepts, and repairs the ones this session proves wrong — a wrong `default`, a drifted key, a missing trigger clause. It never counts a rule's occurrences in the repo and never authors a record: a reusable-looking rule no recorded Concept covers stays a ledger line, and writing it up is a different session's job.

**A finished record is not a finished session.** A term, Concept, or service row resolves one branch of the decision tree and nothing more. The turn a write lands, return to the interview — the write is a side effect of the interview, never its exit.

**Only the user ends the grill.** An empty question frontier, a clean closing sweep, and a full doc set are mid-session states, not stop conditions. When you believe the tree is resolved, say so, ask, and wait for the answer.

**Implementation is a handoff, not a next step.** The user asks to build it → state that the grill is closing, run the closing sweep, then hand off: `/to-tickets` for backlog items, `/to-zdesign` for a design doc, `/prototype` for a throwaway spike. Inside a grill turn, production code stays untouched — including the one-line change the answer you just got seems to imply.

## Session start

1. **Docs exist** — existence check only on `ARCHITECTURE.md` and `CONTEXT.md`; either missing → Run `/bootstrap-docs`' skill **Mandatory creation**.
2. **Load the index** — read `ARCHITECTURE.md` in full: `Building blocks` services and every row of the `Crosscutting Concepts` table. Both sections are optional — absent is not a gap. Multi-part sections need multiple ranged reads; never stop at a partial read.
3. **Claim the ledger** — read `/track-ledger`'s ledger if it exists and confirm it belongs to this session; otherwise start fresh. An inherited `opened` line suppresses a guardrail re-scan for the rest of the session.
4. **Seed the surface** — extract the touched surface from the initial request — terms **and** any concrete file/folder paths it names — and run *Scan and match* once; its normal trigger — a user answer — doesn't exist yet.
5. **Interview.**

## Interview

Interview me relentlessly about every aspect of this until we reach a shared understanding. Map the decisions as a tree and work it in rounds. Before each round, find the **frontier**: every decision whose prerequisites are settled. Apply the fact lookup and evidence rules below before asking; decisions resolved as Feature Assumptions never enter the question frontier. Ask the entire remaining frontier in one round, numbering each question and giving your recommended answer. A question whose answer depends on another unresolved question in the same round belongs to a later round. Wait for the user's answers, reshape the tree, and recompute the frontier.

Format every question in the round like so:

```
Q1: <question body, might be multiple paragraphs, including multiple choices>

> <your recommended answer>
```

**Turn shape** — every turn ends on one of two moves: the next question round, or the explicit ask to close the session. Lookups, ledger lines, and record writes are the middle of a turn; a turn that ends on a write is unfinished, so name the branches it opened or closed and ask the next question round in that same turn.

If a *fact* is discoverable in the environment (filesystem, tools), look it up rather than asking. If a *decision* clears the evidence checklist below, take it as a Feature Assumption rather than asking; if any part fails, put it to me and wait.

Before confirming we've reached a shared understanding, report every Feature Decision and Feature Assumption made this session — one bullet each, 1-3 sentences on what was decided/assumed and why, tagged so the two are never confused: `- [decided] {{item}}: {{explanation}}` / `- [assumed] {{item}}: {{explanation}}`. This is a **report, not a gate**: nothing waits on it, everything recorded is already on disk, and `git diff` is the review surface.

## Decision states

Evidence checklist — all three → Feature Assumption; any miss → ask.

* **Single matching record** — exactly one Concept row matched by *Scan and match* covers the decision area. Zero matches, or two or more, → ask.
* **Direct answer (no analogy)** — a matched record carries a `default` for this decision, or a `Rules` line that answers it normatively. A `Reference:` / "follow its shape" pointer never clears this gate.
* **No genuine alternative** — the record's `default` names the choice to take when the design doesn't state one. Alternatives listed without a default don't clear it.

| State | Resolved by | Home | Durable write |
|---|---|---|---|
| Feature Assumption | model, via the checklist | ledger only | never — the record whose `default` cleared the checklist already covers it; a gap in that record is closing-sweep work |
| Feature Decision | user, resolving no term — feature-scoped or reusable alike | ledger only | never |
| Rejected option | user | ledger only | never |

Log every state and every change of state via `/track-ledger`' skill **Log decision**, the turn it happens. When I correct an assumption you made — at any point in the session — rewrite its ledger line that turn: the correction form when it stood on a Concept's `default` (the closing sweep repairs that key), a deletion otherwise. Every question you ask *because a gate missed* is logged the same turn via that skill's gate-miss form — it is the closing sweep's harvest input. **Every question you ask is by definition a gate miss** (a cleared checklist never asks), so every question in a round MUST get its own gate-miss line naming which gate failed and the nearest source — even when it also produces a Feature Decision. A `decided by user, feature decision` line is **not** a substitute for the gate-miss line: a feature-scoped decision that no Concept row matches is both a Feature Decision and a `gate miss: single-matching-record, nearest source: none`. The sweep resolves that miss as feature-scoped, without creating a Concept. Only decisions you never had to ask (checklist cleared → Feature Assumption) carry no gate-miss line. Authoring choices made while writing docs (synonym lists, term placement, section names, prose wording) are none of these — don't log or list them.

## Context economy

- Broad-sweep code and test lookups → Run `/explore-codebase` skill; direct reads only to quote an exact line.
- Re-fetch a durable artifact when you first need it, or when you need it and can't quote it verbatim from context — never on a schedule, never "just in case", never right after your own write.
- Authority order: `CONTEXT.md`/`ARCHITECTURE.md`/Concept > code > external sources. A conflict against a higher-ranked source is asked, never assumed.

## Probes

Alongside the interview, build and sharpen the project's domain model — challenging terms, inventing edge-case scenarios, and writing the glossary down the moment a term crystallises. Every other decision stays in the ledger. Merely *reading* `CONTEXT.md` for guardrails isn't enough here: the glossary changes as the session goes, even where the Concepts are only read, applied, and repaired.

Every probe stays live for the whole session: re-check its trigger after each user answer, not just once — a later answer can retroactively put an earlier one in conflict.

**Glossary conflict** — the user's term clashes with the existing language in `CONTEXT.md`: call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

**Fuzzy language** — vague or overloaded term: propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

**Concrete scenarios** — when a domain relationship, boundary, or invariant is stated as fact — not just discussed in the abstract — invent edge-case scenarios that force precision about the boundaries between concepts.

**Test coverage** — runs on every change. Check the `Crosscutting Concepts` index for a testing/verification Concept. Match → Run `/explore-codebase` skill to cross-reference it against existing tests and test conventions, then propose add/update/delete. No match → use the code alone. "This adds a repository against the database — your testing Concept mandates an integration-test category. Which category covers persistence round-trips and queries?"

**Scan and match** — on each triggering turn (user answer / new fact), Run `/track-ledger`' skill **Append surface term** with any new surface terms **and any concrete file/folder paths** newly surfaced — by the user, by *Code cross-reference*, or by an `/explore-codebase` result. Paths go in verbatim and repo-relative.
* **Nothing new** — reason over the in-context index copy; no scan, no write.
* **New term(s) or path(s)** — Run `/index-docs`' skill **Scan and match** passing only those, against the not-yet-`opened` rows only.

This verdict is **monotonic** — once a row matches it stays matched as the surface only grows; never re-check an already-`opened` row here.

**Open and extract** — open a linked Concept's **body** only on a matching verdict; indexing alone never implies relevance. Log every Concept you open or skip via `/track-ledger`' skill **Log opened record**, and check the ledger before discussing any module, boundary, or service — listed means its full record is already loaded, don't re-open or re-scan for it. A section absent from an opened record means "not documented", never "not applicable". Extract **mandates** (required concepts, patterns, boundaries), **prohibitions** (explicitly rejected approaches and considered options), **open space** (unconstrained choices), **defaults** (the matched row's Default cell — the choice to take when the design doesn't state one) — and frame every question, scenario, and alternative against them.

**Classify conflicts** — over the full text of already-`opened` Concepts in context; no tool call; re-runs every triggering turn because it is **non-monotonic**: a later answer can retroactively put an earlier design in conflict with a Concept that matched turns ago.
* **Violation** — breaks a Concept. Never present as equally valid — cite the Concept number, surface the conflict.
* **Supersession** — the Concept is outdated, needs revision.
* **Out of scope** — the Concept doesn't apply.

**Code cross-reference** — when the user states how something works, check whether the code agrees, across user-facing, application, integration, and persistence boundaries: validation rules, constraints, domain concepts, data models, contracts, schemas, relationships, business logic. Contradicts the user → surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?" Contradicts a loaded Concept — its rules, or its `default` cell → classify it as **Drift**, log it via `/track-ledger`' drift form, and surface the gap.

**External-source cross-reference** — if the session was seeded from a link or explicit reference to an external source (Jira work item, Confluence page, GitHub issue), track it for the rest of the session. When a statement, decision, or resolved term contradicts it, surface it immediately: "The Jira ticket says X, but you just said Y — which is right?" Once resolved, offer to fix the source at once — never batch: write-capable tool available → apply the fix after the user confirms wording; otherwise tell the user the source is now stale.

**Record inline** — nothing is ever batched to the end of the session. A term resolved by explicit user answer → Run `/record-term` that same turn; the answer is the approval. Resolved by you → it's a Feature Assumption, ledger only (see *Decision states*). Every other decision stays in the ledger, a reusable-sounding rule included: the only Concept writes this skill makes are the closing sweep's repairs to records that already exist.

## Closing sweep

Three parts, each with its own trigger. The sweep **repairs** existing records; it never authors a new one — a term is written inline by `/record-term`, and a rule no recorded Concept covers stays in the ledger.

**1. Per-row disposition.** If the session opened at least one full Concept, emit one verdict per row in the `Crosscutting Concepts` index table — `Applied`, `Not applicable`, `Violated`, or `Superseded` — so no row is silently omitted. Skip for trivial sessions that only touched glossary terms.

**2. Assumption-gap harvest.** Never skipped, and never reported "no gaps" without the reconciliation below. A wrong default or drifted key marks a gap in the Concept behind it. A question with no matched owner may be a feature-scoped decision; keep it in the ledger without manufacturing a Concept.

**Reconciliation first (the anti-skip guard).** Before repairing anything, enumerate *every* user-answered question logged this session and find its gate-miss line. Any question without one is an **unlogged miss** — reconstruct its gate-miss line now, then inspect it like the rest. An empty gap-form list is valid only when no question was asked; reaching "no repairs" without enumerating the questions skips this step.

Then inspect each of the ledger's three gap forms:
* **Gap miss** (`asked, gate miss:`) — if the answer establishes a reusable rule, add the missing `default` to the nearest Concept's index row. If no Concept can host it, leave the decision in the ledger and mark the miss resolved; authoring a brand-new record is never this skill's job. If the answer is feature-scoped, keep the Feature Decision in the ledger and mark the gate miss resolved without changing a record.
* **Correction** (`corrected, evidence was:`) — a `default` produced an assumption the user corrected mid-session; the key is wrong or too broad. Fix: correct that key. This is the only signal a *wrong* default ever produces — it yields a confident assumption, never a question.
* **Drift** (`drift, code contradicts:`) — a key the code contradicts. Fix: correct it, or mark the anchor "verify — may drift".

Write the Concept fix without a second approval when its content is an answer the user already gave this session — the answer was the approval, same as *Record inline*'s term writes. A key change no answer covers is your own call: write it, log it, and report it in the closing `[assumed]` list. Apply each Concept fix via `/record-concept`, resync the row via `/index-docs`' skill **Sync index row**, and mark the ledger line resolved.

**3. Trigger-condition refinement.** Runs last, so it also covers any row part 2 just resynced. Per row, check the **Trigger condition** cell for a gap this session exposed (missed clause, blank cell). If found, refine the clause and apply it via `/index-docs`' skill **Sync index row**.
