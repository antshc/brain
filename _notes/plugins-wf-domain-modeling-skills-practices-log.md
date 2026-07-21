# domain-modeling — applied agentic-retrieval practices

Cross-references [domain-modeling/SKILL.md](../plugins/wf/skills/domain-modeling/SKILL.md) against the practice catalogue in [rag-cheat-sheet-for-agentic-tools.md](rag-cheat-sheet-for-agentic-tools.md). Only practices with a concrete anchor in the skill's text are listed as applied.

## Applied

| Practice (cheat sheet) | Where in domain-modeling/SKILL.md |
|---|---|
| Progressive disclosure (index → detail) | [Load strategy guardrails](../plugins/wf/skills/domain-modeling/SKILL.md#L20) steps 2–3: read the full `Crosscutting Concepts`/`Architecture Decision Records` index tables, open a full record "only when relevant." |
| Link, don't inline | ["Managing the docs"](../plugins/wf/skills/domain-modeling/SKILL.md#L10) delegates all document content to `/manage-docs`, which keeps Concepts/ADRs linked from `ARCHITECTURE.md` rather than duplicated here. |
| Invalidation over blind caching | Step 3's index read is re-run "only when re-scoping or right after a Concept/ADR is authored/edited — not on every turn" (["Continuously validate against Concepts and ADRs"](../plugins/wf/skills/domain-modeling/SKILL.md#L70)); ["Track opened records"](../plugins/wf/skills/domain-modeling/SKILL.md#L38) re-runs the index read on a re-scope ("the in-context index may now be out of date"). |
| Classification over free-form judgment | `Violation` / `Supersession` / `Out of scope` taxonomy in ["Continuously validate against Concepts and ADRs"](../plugins/wf/skills/domain-modeling/SKILL.md#L70) (L73–75); `Drift` taxonomy in ["Cross-reference with code"](../plugins/wf/skills/domain-modeling/SKILL.md#L87) (L93). |
| Persistent structured indexes | Step 2 reads `ARCHITECTURE.md`'s index tables as the retrieval scaffold before any full record is opened. |
| Tiered long-term memory | ["Track opened records"](../plugins/wf/skills/domain-modeling/SKILL.md#L38) persists the session ledger at `/memories/session/domain-model-ledger.md` via the `memory` tool. |
| Chunking strategy | Step 2: "If a section spans more than one comfortable read, issue multiple ranged reads covering all of it — never stop at a partial read." |
| Chunk-size ceiling with explicit overflow handling | Same step 2 clause — names the overflow behavior (multiple ranged reads) instead of leaving it undefined. |
| Context compression | ["Track opened records"](../plugins/wf/skills/domain-modeling/SKILL.md#L38): "compress resolved terms and decisions into a short summary, rely on that plus the ledger" once it grows large. |
| Grounding & citation | "cite the Concept or ADR by number and surface the conflict" (L73); repeated in ["Surface design improvements"](../plugins/wf/skills/domain-modeling/SKILL.md#L79) and ["Trace through the layers"](../plugins/wf/skills/domain-modeling/SKILL.md#L83). |
| Iterative / multi-hop retrieval | ["Track opened records"](../plugins/wf/skills/domain-modeling/SKILL.md#L38): ledger check → re-scope (re-read index → re-apply relevance test → append) loop. |
| Deduplication | Ledger check: "Already listed — its full record is loaded; don't re-open or re-scan the index for it." (L43) |
| Don't over-explore once sufficient | ["Track opened records"](../plugins/wf/skills/domain-modeling/SKILL.md#L38) L46: once the ledger is large, stop re-scanning everything — rely on the compressed summary, re-open a full record only when a specific detail is needed again. |
| Explicit relevance rubric instead of "if relevant" | Step 3 (L26): matching Trigger condition / title / summary / linked module against the scope "is the relevance test, not a subjective read of the summary." |
| Structured trigger conditions bound to the change surface, not conversation wording | Step 3 (L26): ADRs (and narrowed Concepts) are matched primarily against their `Trigger condition` column — "the kind of change in scope … implied by the plan's touched surface — not only a keyword the conversation happened to say." This is the practice the cheat sheet flagged as "good to know, not yet used here" — now implemented via the `ARCHITECTURE-FORMAT.md` Trigger condition column plus this skill's relevance test. |

## Not applied / out of scope for this skill

| Practice (cheat sheet) | Why not here |
|---|---|
| Hybrid search, query expansion, re-ranking, precision-first tool ordering | General tool-selection guidance (`grep_search`/`semantic_search`/etc.); not something a domain-modeling-specific document would restate. |
| Corrective RAG self-check, avoid lost-in-the-middle, negative-result-as-signal, query decomposition | Environment-level agent behavior, not specific to the domain-model documents this skill owns. |
| Parallel independent retrieval | Already a system-level rule; domain-modeling doesn't need its own restatement. |
| Section 4 traps (prompt injection, stale mental cache, full-file-read limits) | Traps to avoid, not practices to apply — not the kind of thing a skill file asserts about itself. |
