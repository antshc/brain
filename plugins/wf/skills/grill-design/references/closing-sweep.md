# Closing Sweep

Run after the user ends the grill or requests implementation. Repair existing records only; terms and ADRs are inline work, and rules without an existing Concept owner stay ledger-only.

## 1. Per-row disposition

If any full Concept or ADR was opened, emit a path-anchored verdict for every row in the session's global and discovered block ADR/Concept indexes: `Applied`, `Not applicable`, `Violated`, or `Superseded`. Deduplicate by record path; justify non-applicability from triggers and touched surface, not absence from context. Unresolved applicability is an explicit open item, not a guessed verdict. Skip this part for glossary-only sessions.

## 2. Assumption-gap harvest

Reconcile before repairing: enumerate all saved questions and available conversation answers. Each decision question needs its own gate-miss line; reconstruct missing lines from evidence. Fact-gap, term, authorization, and close questions use their frontier records instead. An empty gate-miss list is valid only when no decision question was asked.

Inspect each gap, including previously resolved gaps invalidated by later answers:

* **Gate miss** — confirmed ADR write → resolve with its path. Reusable answer with an existing Concept owner → repair that decision key's missing default through `concept-record`, preserving unrelated clauses, conditions, exceptions, and source anchors. Several owners → repair only an explicitly established owner; unresolved ownership stays open. No existing owner → resolve as ledger-only without creating a Concept. Feature-scoped answer → resolve as Feature Decision. Pending answer, classification, or write → keep open.
* **Correction** — user corrected an assumption based on a Concept default → repair that key. For ADR corrections, surface the conflict and use the user's resolution in `adr` mode; do not autonomously rewrite its decision.
* **Drift** — inspect both the record anchor and code evidence. Missing proof stays unverified/open. For a confirmed Concept discrepancy, correct the key or mark the anchor "verify — may drift"; that marker records uncertainty, not a completed repair. An ADR discrepancy needs the user's decision before rewrite.

A Concept repair covered by a user answer needs no second approval. A key change no answer covers remains the model's call: write it, log its evidence, and report it in the closing `[assumed]` list. *Run `record-architecture` skill for settled architecture Concepts* in `concept-record` mode; let it sync the index. Append `repaired:` only after both results are confirmed.

If the user corrects an answer after an ADR was written, reopen the linked question/gap and route the reversal through `adr` mode. Preserve the prior ADR choice as rejected; do not treat an earlier successful write as proof of the new decision.

## 3. Trigger-condition refinement

Run after repairs so newly synced rows are included. Check each relevant row for a missed clause or blank Trigger condition exposed this session, including discoverability of every repaired default's scope, branch conditions, and exceptions. Do not broaden policy to broaden matching. Supply an evidenced refinement through *Run `index-docs` skill for row-sync of Markdown Trigger condition tables*, using **Sync index row**. Preserve unaffected cells; pending sync remains open.

## Final reconciliation and handoff

Re-read the request and map every interview obligation to evidence: questions/answers, decisions/assumptions, inline records, corrections/drift, triggered verification and external-source probes, and index updates.

Every `asked`, `corrected`, or `drift` entry must have `repaired:` / `resolved:` evidence or appear in the open-items report with blocker and next action. Report pending writes separately; a failed write, unresolved question, or verification marker is not success.

Persist final status, frontier, evidence, blockers, and next action. Report the decisions/assumptions and outstanding work, then hand off as requested. Open items travel with the handoff; report closure as incomplete rather than hiding them or keeping the interview running against the user's request.
