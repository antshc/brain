
---

the idea is to have the index.jsonl file waht model will load to the context and ("Track opened records").
have the Architecture.md tabel as human facing table, updated manually after the session to align with the index.
When inline capture happens add information directly to durable sources (index.jsonl, CONTEXT.md, ADR and Concepts files)
Track decisions and assumptions in the session ledger using the md fiel or jsonl, because no other durable place to store them.
---

Fuzzy point: The doc calls it one artifact — "the session ledger" at /memories/session/domain-model-ledger.md — but defines it via two independent triggers with two different line formats:

Track opened records: {{path}} — opened for {{topic}}
Stage assumptions in the ledger: {{decision}} — assumed, evidence: "{{source}}", pending veto


---

Opened record
What: A pointer to an existing Concept/ADR/service doc that was read into context this session because /trigger-indexer matched its trigger clause against the current topic.

Format: {{path}} — opened for {{topic}}

Purpose: Pure caching/avoidance — stop re-scanning the full ARCHITECTURE.md index and re-running the relevance check every time a module/boundary/service comes up. See SKILL.md:46-51 ("Track opened records").

Lifecycle: No status field, no veto, no promotion. It's either "already listed" (skip re-opening) or "not listed" (re-scope and append). It never gets rewritten later.

Decision / assumption pair
What: A new piece of domain content — a glossary term, an ADR, or a Concept — that grilling is in the process of resolving. Per the grilling skill's evidence checklist:

If the checklist is met (single authoritative source, direct answer, no genuine alternative) → resolved silently as an assumption, logged to the ledger as provisional.
If not met → put to the user as a question; once the user answers, it's resolved directly — written immediately to CONTEXT.md/ADR/Concept, and not staged in the ledger at all (see SKILL.md:124-127 and SKILL.md:133-136, "When a term/ADR/Concept is resolved by explicit user answer").
So only the assumption half of the pair ever reaches the ledger — "decision" here isn't a separate ledger entry type, it's the name for the resolution act; user-answered decisions bypass the ledger and go straight into the doc.

Format: {{decision}} — assumed, evidence: "{{source}}", pending veto

Purpose: Track provisional, unconfirmed writes so they can be reverted if the user vetoes them later.

Lifecycle: pending veto → at the Closing completeness sweep, checked against the grilling skill's end-of-session veto list → either:

Cleared: promote Status: proposed → accepted (ADR/Concept); glossary terms need no further action.
Vetoed: revert — undo the ADR/Concept status/record, delete the glossary term from CONTEXT.md.
Side-by-side
Opened record	Assumption
Subject	Existing doc read into context	New content authored this session
Written when	A Concept/ADR/service doc is matched relevant	A decision is resolved without asking (checklist met)
Status field	None	pending veto → accepted/reverted
Ends in a veto?	No	Yes, at closing sweep
Ever rewritten?	No (append-only)	Yes (status changes or line removed)
This confirms your instinct: the same ledger file is being asked to do two structurally different jobs with two different lifecycles, mixed into one flat list — which is exactly the ambiguity worth sharpening (e.g., does the closing sweep scan for pending veto as a bare substring to separate the two kinds, or is there a cleaner structural separation intended?).



---


So the real instruction should say
Not "re-open... at the start of every turn" (implying a fresh fetch every time) — that overstates the cost-saving and contradicts itself, as you spotted. It should instead distinguish:

Reasoning over the list happens every triggering turn (user answer / new fact) — using whatever copy is already in context, no tool call required if one's already present.
Re-fetching via memory view happens only on first use, or after a suspected compaction.
Re-writing via the memory tool (str_replace/append) happens every time a line's state actually changes — that's a write, not a read, and it's unavoidable regardless, since the durable copy must stay correct for the next session-restart or compaction recovery.
Does that three-way split (reason-over-existing-context / fetch-only-when-absent / write-on-every-change) match what you intended, or should the fetch trigger be broader than "suspected compaction" — e.g., always re-view at the very start of each new user turn as a cheap safety net, even though it's technically redundant if nothing was evicted?