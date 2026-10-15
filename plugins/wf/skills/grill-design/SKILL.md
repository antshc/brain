---
name: grill-design
description: Stress-tests a plan or design through a relentless interview, surfacing domain terminology, feature decisions, assumptions, and ADRs. Use for grill design, grilling design, or domain-modeling probes. Not for implementation; closes with a spec or design handoff.
---

# Grill Design

Own the interview and session design state: when to look up, log, ask, or write. Delegate mechanics through the skill contracts below; apply their procedures without restating them.

## Scope

Produce **questions** and **records**. Writable surface: `GLOSSARY.md`, `ARCHITECTURE.md`, `docs/adr/**`, `docs/concepts/**`, `docs/building-blocks/**`, and the session ledger. Source code, tests, configuration, and scaffolding **MUST remain read-only** throughout the grill.

**Concepts are consumed, not discovered.** Match, open, and apply existing Concepts; repair wrong defaults, drifted keys, and missing trigger clauses during closing. MUST NOT author or offer new Concepts, or count rule occurrences to discover them. Rules with no existing owner stay in the ledger.

**ADRs are recorded, not offered.** An explicit user answer passing the loaded `adr` mode's gate authorizes its same-turn write. A user reversal rewrites that ADR in place through the same mode, preserving the previous decision as a rejected option.

**Only the user ends the grill.** The grill MUST end only on a user request or confirmation, not a finished record, empty frontier, or clean sweep. When the tree appears resolved, report it, ask to close, and wait.

**Implementation is a handoff.** When the user asks to build, including a one-line fix, announce closing and run the closing sweep. Then route the saved context to the requested output: *Run `to-spec` skill to synthesize the conversation into a spec published as a GitHub issue or offline Markdown*; or *Run `to-zdesign` skill to capture a completed design conversation as an authoritative feature design*. Execution belongs to the handoff, outside the grill.

## Session start

1. **Claim state** — load [track-ledger.md](./references/track-ledger.md) before ledger access. Resolve session storage and ownership using its protocol; restore the frontier, answers, pending writes, and blockers. An unknown owner starts fresh without overwriting the old ledger.
2. **Check docs** — existence-check `ARCHITECTURE.md` and `GLOSSARY.md`. If either is missing, *Run `bootstrap-docs` skill to create missing ARCHITECTURE.md and GLOSSARY.md from bundled formats*, using **Mandatory creation**. Proceed only when both exist; otherwise apply *Gotchas*.
3. **Load the index** — *Run `index-docs` skill to load the full ARCHITECTURE.md index of Trigger condition tables*, using **Load index** on `ARCHITECTURE.md` with `Summary` omitted; this covers every row of `Deployables`, `Architecture Decision Records`, and `Crosscutting Concepts`. MUST use that operation's Python loader and consume every returned row; MUST NOT substitute manual reads, search, or counts-only output, even if simpler. Rationale: script counts and validation make completeness observable. Log per-table total/loaded counts and source in the ledger's `Index loaded` header. MUST NOT scan/match until every row is loaded; script unavailable or incomplete output → Index failure. Missing sections are optional, not gaps.
4. **Seed the surface** — extract terms and concrete file/folder paths from the initial request; run *Scan and match*. On resume, apply only newly surfaced inputs; retain same-session match history, reloading needed evidence absent from context.
5. **Interview** — restore or construct the dependency tree and its ready questions; apply *Decision states*, persist the ledger, and use the pre-question status below.

## Skill contracts

| Operation | Invocation and inputs | Required result |
|---|---|---|
| Code/test lookup | Read `explore-codebase` skill's **Request**; form the bounded question, target, depth, and output shape. Spawn one read-only subagent per independent track (dependent tracks sequential) with that request verbatim, instructing it to *run `explore-codebase` skill for read-only lookups locating symbols, tests, or how a flow works*. Skill unavailable → explore agent with the same request. | Findings with `path:line` or symbol evidence, unknowns, and completion/blocker status. |
| Index load/scan/sync | *Run `index-docs` skill for full index load, scan/match, and row-sync of Markdown Trigger condition tables.* Supply the operation and its required metadata. | Per-table counts and every row, matched/checked clauses and rationale, or the updated row/sync result; explicit errors. |
| Record | *Run `record-architecture` skill for settled architecture ADRs, Concepts, and glossary terms.* Select `term`, `adr`, or `concept-record`; load the mode before checking its gate. | Gate result, written path, and required index/pointer result, an explicit blocker, or an ADR scope question — ask it next; keep the write pending until answered. |

Integrate lookup evidence into the frontier and touched surface; integrate record/index results into the ledger. Mark a record written only after the returned result confirms its persistence and required sync.

## Interview

Probe the design until the user confirms shared understanding. Maintain the full **decision tree** and **frontier** internally: every unresolved question whose prerequisites are settled. Hold questions with pending prerequisites.

Before selecting the next question, look up facts available from the environment and apply *Decision states*: a checklist-backed Feature Assumption leaves the frontier. Select one ready question with its stable ID, descriptive title, and recommended answer with reasoning. Phrase it so **"yes" accepts its recommendation**; allow disagreement or another choice without treating silence as approval.

Before **every question**, including fact-gap, term, ADR-scope, and close questions, persist updated state and print Concept/ADR index coverage (loaded/total rows), opened Deployable/Concept/ADR record counts, and a clickable ledger link. Example: `Index: Concepts 42/42, ADRs 18/18 rows loaded. Opened records: Deployables 2, Concepts 7, ADRs 3. [Assumptions and feature decisions](<ledger-location>)`. Index coverage is per source when block indexes are loaded; opened counts follow the ledger's deduplicated body-read history. Print known partial counts as incomplete on failure; never claim full coverage. Reuse confirmed counts/history without reloading unchanged indexes or bodies merely to print status. Use the host-supported clickable link for the actual persisted ledger; missing storage follows its failure protocol. MUST NOT reproduce assumptions or feature decisions before questions; the ledger is their review surface.

**MUST ask one question at a time in ordinary conversation; MUST NOT use question/input tools.** Keep the current format:

```markdown
❓ **Q1** - **<title>**: <question phrased so yes accepts the recommendation>

- **A** (Recommended) <option>
- **B** <option>
- **C** <option>

➡️ <recommended answer and reason>
```

After every answer, record it and perform required inline writes; re-check triggered probes and affected decision keys. When the answer changes evidence or dependencies, rebuild assumptions and the frontier before selecting the next question. Withdraw obsolete questions, defer blocked ones, and preserve stable IDs. Unanswered questions remain pending, never implicitly accepted. Newly unblocked dependents become eligible immediately; do not wait for other frontier questions to be answered.

Use the code-lookup contract to obtain environmental facts rather than asking the user to research them. Running lookups are unsettled prerequisites: hold their dependent questions and select one other ready question without waiting. If a lookup fails or stays inconclusive, follow *Gotchas* rather than inventing a fact. Index loading, lookups, and ledger/record writes still use their required tools.

Before ending each turn, persist frontier changes, answers, evidence, blockers, and next action. During an active interview, end on the next question or explicit request to close; after a write, name the affected branches and return to questioning. If only running prerequisites remain, persist and report the wait without claiming the tree is resolved. An empty frontier is resolved only when no blocked prerequisites or unanswered questions remain.

At closure, report every Feature Decision, ADR decision, and Feature Assumption: one bullet each, 1–3 sentences explaining what and why, tagged `[decided]` or `[assumed]`. Include model-authored Concept repairs as assumptions. This report adds no approval gate; identify pending writes explicitly instead of implying everything is on disk. `git diff` is the record review surface.

## Decision states

Evaluate each independently answerable **decision key**; use the record's key when supplied, otherwise name the choice being settled. All four checks pass → Feature Assumption; any miss → keep only that key unresolved.

* **Direct policy** (`direct-policy`) — at least one opened Concept or ADR directly settles the key through its default, normative rule, or decision. A reference, analogy, recommendation, or code observation alone fails.
* **Established applicability** (`applicability`) — evidence establishes the governing scope and branch conditions. Apply a settled exception when its condition holds; unknown conditions require fact lookup, then a fact-gap question if unresolved. MUST NOT widen scope from similarity or treat an unknown exception as absent.
* **Unambiguous answer** (`agreement`) — applicable clauses agree, govern different keys, or have an explicit recorded override. Multiple records and documented alternatives do not fail by themselves; unresolved competing answers do. MUST NOT invent precedence from specificity, record type, or recency. A default may select among genuine alternatives; an open menu without a selection rule fails.
* **No explicit contradiction** (`contradiction`) — the current user choice and available evidence do not contradict the applicable policy. Surface a user-policy conflict for explicit resolution; MUST NOT replace an explicit answer with a default or use a default to bypass known drift.

Rationale: reuse settled policy per choice; overlapping records need not mean ambiguity. Keep covered keys assumed while uncovered keys remain in the frontier. Existing single-sentence defaults remain usable under these checks. A default applies only when the design is silent on that key.

| State | Resolved by | Home and write timing |
|---|---|---|
| Feature Assumption | model, checklist passed | Ledger only; applicable records already cover the key. |
| ADR decision | user, ADR gate passed | Ledger + ADR, same turn; the answer authorizes the write. |
| Feature Decision | user, ADR gate failed, not a term | Ledger only, whether feature-scoped or reusable. |
| Rejected option | user | Ledger only. |

Every decision question **MUST** get a gate-miss line per unresolved key that turn, identifying the failed gate(s) and relevant source anchors; preserve it alongside the resulting state:

| Outcome | Ledger entries |
|---|---|
| Feature Decision | Gate miss + decided by user; no policy uses `direct-policy`, source `none`. |
| ADR decision | Gate miss + recorded path, or pending write until persistence succeeds. |
| Feature Assumption | Assumed with key, applied condition, and governing source anchors; no gate miss. |

Log state changes that turn. When the user corrects an assumption, replace it with a correction line if based on a Concept default; otherwise remove the stale assumption, retaining the correction and new answer in the frontier history. Surface ADR corrections for explicit user resolution through `adr` mode.

Unknown applicability alone creates a fact-gap prerequisite, not a policy decision or gate-miss line; re-evaluate its decision key after the fact is established. Fact-gap questions, term clarifications, and close/authorization requests are not failed decision-checklist gates; record their kind and answer in the frontier instead. Documentation wording, synonyms, and section placement are authoring choices, not decisions.

## Context economy

- Communicate primarily through **context pointers**: linked record paths/anchors, code locations, source URLs, and ledger question/decision IDs.
- Do not duplicate information already available through those pointers. In questions, reports, lookup briefs, and handoffs, link the source and state only the new question, decision, change, or uncertainty; keep required recommendations and decision summaries concise.
- Prefer the code-lookup contract for broad code/test searches; use direct reads for a known evidence location.
- Re-fetch an artifact when first needed or when its required evidence is no longer available in context. Prefer reuse after a confirmed write; re-read when verification or a detected change requires it, not on a schedule.
- Authority: `GLOSSARY.md` / `ARCHITECTURE.md` / ADR / Concept > code > external sources. Surface unresolved conflicts, including conflicts within the same rank; apply only explicit recorded overrides, otherwise ask rather than silently choosing an authority.

## Probes

Re-check each probe's trigger after every user answer or new fact. A later answer can invalidate an earlier interpretation.

**Glossary conflict** — when the user's term clashes with `GLOSSARY.md`, cite the definition and ask which meaning applies.

**Fuzzy language** — when a term is vague or overloaded, propose a precise canonical term and resolve it with the user.

**Concrete scenarios** — when a domain relationship, boundary, or invariant is asserted as fact, invent edge cases that expose its limits.

**Verification scope** — when the design changes behavior, persistence, or an integration boundary, load [probes-verification.md](./references/probes-verification.md) and apply the coverage-category check.

**External source** — when seeded from an explicit external link or reference, load [probes-external-source.md](./references/probes-external-source.md); track and reconcile it throughout the session.

**Scan and match** — append newly surfaced terms and repo-relative verbatim file/folder paths to the ledger, including lookup results.
* Nothing new → reason over the current index; no scan or surface write.
* New terms/paths → use the index contract's **Scan and match** on not-yet-opened global ADR, Concept, and Deployable rows, passing only the new surface plus the required questioning context and glossary.
* Matched Deployable → open its record read-only, whether harness-owned under `docs/building-blocks/` or repo-owned documentation, and log it in `Opened records`. Load its Concepts and ADR tables via **Load index** with the record path, then scan them; for repo-owned blocks, use their own architecture indexes. Deduplicate records across global and block tables by path.

Matches are monotonic as surface grows: an opened record needs no matching re-scan. Skipped rows remain candidates when new surface arrives.

**Open and extract** — open linked bodies on a match; indexing alone does not imply relevance. Log opened and skipped verdicts. Before discussing a module, boundary, or service, check its ledger status: only `opened` confirms a previous body read; `skipped` does not. Reload previously opened evidence if needed after context loss, without repeating the matching scan. Missing sections mean "not documented", not "not applicable".

Extract mandates, prohibitions, open choices, and default clauses from the body and the matched row's `**Default:**` cell. Group by decision key; retain scope, selection conditions, exceptions, and body anchors. A trigger match opens a candidate, not every default's applicability. Frame questions and alternatives against them.

**Classify conflicts** — re-evaluate already-opened records after every answer/new fact; use in-context evidence, reloading only missing details.
* Violation → cite the rule or ADR rejected option; present the conflict, not an equally valid alternative.
* Supersession → identify the outdated rule; repair a Concept during closing, or rewrite a user-reversed ADR inline.
* Out of scope → explain why the record does not apply.

**Code cross-reference** — when the user states how something works, use the lookup contract to check user-facing, application, integration, and persistence boundaries: validation, constraints, models, schemas, contracts, relationships, and logic. Surface contradictions with both the claim/record anchor and code `path:line` or symbol evidence. A contradiction against a Concept/ADR is Drift; log both sources. Missing proof → label `unverified`, retain the fact gap, and avoid presenting it as an established contradiction.

**Record inline** — resolve terms and architectural decisions in the turn answered, before the next question:
* Explicitly resolved term → use the record contract's `term` mode.
* Explicitly resolved decision → load `adr` mode and check its gate; pass → write; miss → Feature Decision in the ledger.
* Model resolution → Feature Assumption in the ledger, not an ADR.

Existing Concept repairs belong to closing; other reusable rules remain ledger-only. Apply *Gotchas* when a write is blocked. Question sequencing does not delay authorized inline writes.

## Gotchas

- Required skill/tool unavailable or operation failed → report the operation, target, and error; block only dependent work. Retry a classified transient error at most twice. Missing skills, invalid inputs, and inconclusive evidence require resolution, not repeated identical calls.
- Bootstrap failure → keep existing files, report partial creation, and block index-dependent assumptions and record writes until both docs exist. Continue only independent questioning.
- Lookup failure/inconclusive result → ask for the missing fact, labelled **fact gap**. Record user-supplied evidence as such; conflicting or unverified facts remain blocked. An unknown fact is not a design decision.
- Incomplete index load (Python loader unavailable/not run, **Load index** errors, truncated output, unread rows, or missing total/loaded counts) → Index failure; recover through **Load index** before matching. Manual reads and counts-only output cannot clear the blocker.
- Index failure → treat matching/sync as incomplete, not "no matches". Block affected assumptions; preserve partial writes as pending sync.
- Record failure/unavailable → persist the answer, intended mode/target, and blocker as `pending write`. If the ADR gate was unavailable, mark classification pending rather than assuming a Feature Decision. Resume the owning procedure after recovery; check existing state first to avoid duplicate records.
- Missing session storage → apply the ledger's storage failure protocol; do not substitute an arbitrary repository file.

## Closing sweep

When the user asks to close, confirms closure, or requests implementation, load [closing-sweep.md](./references/closing-sweep.md). Complete its reconciliation, repairs, and trigger refinement before handoff. If the user resumes questioning, persist outstanding work and return to the interview.

## Completion criteria

- The user ended the grill; the sweep accounts for every question, decision, gap, and triggered probe.
- Each `asked`, `corrected`, or `drift` line is repaired/resolved with evidence, or explicitly reported open with a blocker and next action.
- Required records and indexes are confirmed written, or individually reported pending; source code, tests, configuration, and scaffolding remain unchanged.
- The persisted ledger and handoff identify decisions, assumptions, evidence, unanswered questions, verification scope, blockers, and next action. Report closure as incomplete when storage, writes, or checks remain blocked.
