# Track Ledger

The parent owns write timing; this reference owns storage and grammar.

## Storage and ownership

1. Resolve the host-provided session ID and persistent session storage. Prefer session-scoped memory at `/memories/session/domain-model-ledger.md` when the host exposes it. Otherwise use file tools at `<host-provided session folder>/files/domain-model-ledger.md`. Use only the location supplied by the host; do not guess a home path or write the ledger into the repository.
2. Read an existing ledger's header before reusing state. Require the same session ID, repository, and interview topic; topic/date alone do not prove ownership. Restore only a verified match.
3. Missing ledger → start fresh in memory. Ownership unknown/mismatched → leave the existing file untouched, select a fresh `domain-model-ledger-<session-id>-<n>.md` in the resolved session storage, and report/log which ledger was ignored and why. Reuse that selected path for the interview.
4. Create lazily on the first state write. Header: `Session ID`, `Repository`, `Topic`, `Started at` (ISO date/time), `Ledger location`, `Status` (active/closing/closed/incomplete), and optional `Ignored ledger` with reason.

If neither session memory nor a host-provided persistent folder is available, report the blocker and request a storage location. Keep read-only discussion possible, but block record writes and resumable/completed-session claims until state can be persisted. Do not silently fall back to an arbitrary file.

Use five sections: `Opened records`, `Touched surface`, `Decisions / assumptions`, `Open frontier`, and `Pending writes`.

## Log opened record

One entry per repo-relative record path; update in place. Paths, not row numbers or ranges, identify records.

* `{{path}} — opened, trigger matched: "{{clause}}"`
* `{{path}} — opened, direct: {{topic}}`
* `{{path}} — skipped, checked "{{clause1}}", "{{clause2}}": no match`

Return the written line. `opened` preserves match history, not a guarantee that the body remains in context.

## Append surface term

Accumulate unique modules, boundaries, services, entities, data shapes, behaviors, interfaces, change types, and concrete paths in `Touched surface`. Preserve repo-relative paths verbatim for path/glob matching, not semantic paraphrases.

Append only new terms/paths; return which were new. A skipped verdict is valid only for the surface checked then; new surface makes skipped rows eligible again.

## Log decision

Use stable item/question IDs. A decision and its gate miss are separate entries sharing an ID; update by ID **and entry kind**, not item text alone.

* `{{id}} {{item}} — assumed, key: {{decisionKey}}, condition: "{{establishedCondition}}", evidence: "{{governingSourceAnchors}}"`
* `{{id}} {{item}} — assumed, recorded: {{path}}#{{key}}, evidence: "{{source}}"`
* `{{id}} {{item}} — decided by user, feature decision, grounded: "{{source}}"`
* `{{id}} {{item}} — decided by user, recorded: {{path}}`
* `{{id}} {{item}} — rejected, reason: "{{source}}"`

Keep legacy entries readable; add key/condition/anchors when next evaluated. Conflicting clauses retain all source anchors; unknown applicability links to its fact-gap prerequisite. Multiple keys under one question share the question ID but use distinct decision keys; update by ID, entry kind, and key when present.

Gap forms:

* `{{id}} {{item}} — asked, key: {{decisionKey}}, gate miss: {{gates}}, nearest source: {{sourceAnchors|none}}`
* `{{id}} {{item}} — corrected, evidence was: {{path}}#{{key}}, answer: "{{userCorrection}}"`
* `{{id}} {{item}} — drift, code contradicts: {{path}}#{{key}}, code evidence: {{codePath:line|symbol}}, finding: "{{contradiction}}"`

For a suspected contradiction without proof, use `code evidence: unverified` and link a fact-gap frontier entry; this is not established Drift.

After confirmed resolution, append one:

* `, repaired: {{path}}#{{key}}` — record and required index sync confirmed.
* `, resolved: feature decision` — no reusable record change needed.
* `, resolved: recorded {{path}}` — answer persisted as an ADR.
* `, resolved: ledger only, no existing Concept owner` — reusable answer with no owner.
* `, resolved: {{reason}}, evidence: "{{source}}"` — evidenced dismissal, term write, or other non-repair resolution.

Deferred, unanswered, unverified, or failed work stays open; do not add a resolved suffix merely because it was reported. If later evidence invalidates a resolution, remove the stale suffix and reopen it.

Rewrite corrected assumptions or delete stale ones as directed by the parent, preserving the new answer and evidence in frontier history. Return the changed entry or deletion confirmation.

## Save frontier

Use session-stable IDs (`Q1`, `Q2`, ...), not numbering reset each round. Record every question, including decision, term, fact-gap, authorization, and close questions:

`{{id}} — round: {{roundId}}; kind: {{kind}}; question: "{{text}}"; recommendation: "{{answer|none}}"; prerequisites: {{ids|none}}; status: {{ready|asked|blocked|answered|deferred}}; answer: "{{answer|pending}}"; evidence: "{{source|unknown}}"; next: "{{action}}"`

Retain answered entries for closing reconciliation; a gate-miss line references the same decision-question ID. Track unresolved lookups and dependent questions as blocked with the operation/error. Store the current round's remaining IDs, planned next round, and next action; do not invent questions simply to fill these fields. Partial answers preserve the remaining round for batched follow-up; dependent questions stay in a later round.

On resume, use these entries and decision evidence to rebuild dependencies before asking again. A new answer may reopen a previously answered question.

## Pending writes

`{{id}} {{item}} — pending write, mode: {{term|adr|concept-record|index-sync|external-source}}, target: {{pathOrURL|unresolved}}, approved content: "{{answer}}", gate: {{passed|pending|not applicable}}, blocker: "{{error}}", next: "{{action}}"`

Keep partial-write paths and missing sync work. On recovery, inspect target state, apply only the missing operation through its owning skill, and replace pending status with the confirmed result. Report pending items at closure; never label them recorded.

## Compression

After a section exceeds ~20 lines, summarize it in conversational output rather than reproducing it in full. Persist exact record paths/statuses, surface terms/paths, question IDs/text/answers, decisions/evidence, and unresolved lines. Do not destructively compress away data needed for deduplication, resume, or reconciliation. Reload only the needed stored detail after context loss.
