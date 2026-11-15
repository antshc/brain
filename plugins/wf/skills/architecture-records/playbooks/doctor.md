# Architecture doctor

## Inputs and scope

Inputs: repository/docs root, optional paths or artifact kinds, optional report destination. Resolve an established docs root; ask only if ambiguous. Record the inspected revision and time.

Default scope: all architecture indexes, ADRs, Concepts, and building-block records under that root, including block-local indexes and linked records outside conventional folders. A subset includes its relevant index relationships; list exclusions. Ignore `_backup/` and `_in-progress/`, including links into them, unless explicitly requested.

Keep the repository read-only. A supplied report destination authorizes only writing that report; otherwise return inline. Never initialize missing docs, repair rows, rewrite policy, change code, run mutation-capable tests, or publish. Inspection of production/runtime systems requires independently authorized read-only access; its absence is not permission to probe.

Done when root, revision, scope, exclusions, and report destination are explicit.

## Inventory

Inventory filesystem records in `docs/adr/`, `docs/concepts/`, and `docs/building-blocks/` relative to the established root; honor repository-specific equivalents and caller paths. Also follow in-scope index links, including externally owned/self-documented blocks. Enumerate both directions so an unindexed record cannot disappear from coverage. Deduplicate normalized paths; retain every owning row/section locator.

Include system-context diagrams and deployment pointers referenced by inspected blocks/indexes. Full deployment auditing requires explicit scope. Missing expected documents are findings; optional absent sections and unused directories are valid. No ARCHITECTURE.md means an incomplete inventory and a missing-index finding, even if no record directories exist; never call that empty repository clean. Missing inaccessible external records remain unknown, not silently excluded.

Done when each record/index has an inventory entry or explicit exclusion; missing prerequisites and external access gaps are named.

## Load indexes

Return control to the router for **Index actions**; use **Load index** for every in-scope root/block index, preserving the loader's JSON, options, exit codes, and complete-row consumption rules. Load all applicable tables, not only rows matching the initial request. Scope exclusions remain in the ledger.

Malformed rows, marker mismatches, unreadable files, unavailable Python/script, and truncated/unconsumed rows block a complete verdict for that index. Save explicit errors and continue independent records; do not substitute manual parsing as a successful load. Keep script totals and consumed counts separately, including when re-running by table.

Done when every index has reconciled per-table counts or an explicit load blocker.

## Check records

Read every inventoried record in full. Extract checkable claims with record section/line evidence; distinguish approved intent, implemented behavior, and proposals. Inspect the relevant current contracts, source, configuration, tests, and deployment definitions read-only. Use bounded built-in `explore` subagent lookups when useful, with `path:line` evidence and explicit blockers. A passing test supports only its exercised behavior; syntax/link health alone cannot prove currency.

| Artifact | Check |
|---|---|
| ADR | Decision/scope applicability, named components and rejected alternatives, documented reversals, implementation disagreement. An approved decision awaiting implementation remains valid; report its implementation state separately |
| Concept | Rules/defaults, selection conditions, exceptions, examples, terminology, Implementation Map locators, overlapping or conflicting authority; keep observed behavior distinct from decided policy |
| Building block | Responsibility, ownership/location, dependencies/direction, interfaces, persisted data, configuration, folder structure, context/container/component/flow diagrams, nested indexes and external documentation |
| Index prose/pointers | Architecture decomposition, block locations, system-context relationships, and deployment links/summaries agree with owned records and available source |

An implementation contradiction establishes drift, not permission to reverse a decision. File age is a triage hint only. Removal/rename/obsolescence claims require affirmative retirement/supersession evidence or complete owning-repository search plus supporting sources; a bounded search miss is unknown.

Done when every in-scope claim has supporting evidence, contradicting evidence, or a precise reason it remains unknown.

## Check index consistency

Compare every loaded row with its linked body and owning scope: title, summary, Trigger/Default, applicability conditions, exceptions, row counts, duplicate/missing entries, orphan records, links and anchors. Preserve valid unlinked ADR rows whose Summary contains the decision; assess that row as the record instead of demanding a file. Optional missing sections and hand-authored tables without count markers are valid.

ADRs and Concepts belong in one owning index: system-wide or the single block they govern. Respect self-documented block ownership and already-marked retirements. Report inconsistent retirement markers/body claims without inventing a new status format. Triggers must expose the existing default's scope without widening policy.

Done when each row has an evidence-backed result or blocker and each record's expected owner is accounted for.

## Classify findings

Assign each claim/record one verdict; mixed records take the strongest supported issue (`obsolete`, then `drift`), otherwise `unknown` if any claim is unresolved, else `current`. Preserve unresolved claims even when the record has another verdict.

| Verdict | Evidence required |
|---|---|
| `current` | Applicable claims and index relationships agree with current evidence or an explicit approved decision awaiting implementation |
| `drift` | Cited contradiction, stale locator/row/link, conflicting authority, or required missing record/index |
| `obsolete` | Affirmative retirement, supersession, or removal evidence; identify replacement when known |
| `unknown` | Missing source/access, incomplete search, malformed/truncated index, or insufficient evidence; name the gap and resolution |

Aggregate outcome: `findings` when any drift/obsolete exists; otherwise `incomplete` when anything is unknown/blocked; otherwise `clean`. Coverage completeness is a separate reported value, including when findings coexist with blockers. Clean requires complete coverage and all-current verdicts.

Done when verdicts, impacts, cited comparisons, and unresolved coverage are explicit; no unsupported clean/obsolete conclusion remains.

## Report

Return control to the router for **Resource map** to load Doctor report; render its sections and field guidance. Recommend the owning route/action for each correction: `adr`, `concept-record`, `building-block`, `deployment-view`, or `index` with its action. Recommend `define-concept` only for unresolved shared-policy decisions; a glossary problem uses `term`. A recommendation never executes the correction.

Return the inline report or supplied report path. Do not add report content to the architecture index. Done when each finding includes the documented statement, observed evidence, impact, and next action, with coverage and blockers visible.

## Completion criteria

- Report separates approved intent from implementation and supplies evidence for current/drift/obsolete verdicts; unknowns state what would resolve them.
- Scope, exclusions, record verdicts, index totals/consumed counts, and coverage completeness are visible even with findings.
- Repository content is unchanged except an explicitly requested report; no repair, initialization, code mutation, or publication occurred.

## Closing completeness sweep

Run last. Re-read the request; reconcile every inventoried artifact and row against an assessed verdict, explicit blocker, or declared exclusion. Coverage is per artifact: `inventoried = assessed + blocked`, with assessed/blocked disjoint; partially assessed artifacts count blocked and retain their known findings. Track index rows separately; reconcile each table's consumed rows to its reported total. Account for ADRs, Concepts, blocks, nested indexes, orphan records, referenced context/deployment pointers, and requested subsets. Missing obligations remain explicit gaps; only full reconciled scope permits clean.
