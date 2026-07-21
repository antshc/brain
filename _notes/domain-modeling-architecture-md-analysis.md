# Analysis: `domain-modeling` skill × `ARCHITECTURE.md`

Scope: efficiency (token/tool-call cost) and predictability (reproducible agent behavior) of the load/read/update rules that touch `ARCHITECTURE.md`, per [plugins/wf/skills/domain-modeling/SKILL.md](../plugins/wf/skills/domain-modeling/SKILL.md) and its dependency [plugins/wf/skills/manage-docs/ARCHITECTURE-FORMAT.md](../plugins/wf/skills/manage-docs/ARCHITECTURE-FORMAT.md).

## Pros

| # | Behavior | Why it works |
|---|---|---|
| 1 | Index-first, open-full-record-only-if-relevant (`Load strategy guardrails` step 2) | Mirrors retrieval-augmented best practice — retrieve a cheap summary, expand only what's needed. Keeps the steady-state context budget small even as `docs/adr/`/`docs/concepts/` grow. |
| 2 | "*complete* index tables — every row, not a sample" | Removes sampling ambiguity for the one artifact that must stay small (the index). Gives a deterministic, reproducible baseline read across runs/models. |
| 3 | Format/ownership fully delegated to `manage-docs` (`ARCHITECTURE-FORMAT.md` owns structure, `domain-modeling` only consumes it) | Single source of truth — the two skills can't drift into conflicting rules about what `ARCHITECTURE.md` should look like. |
| 4 | Explicit invalidation triggers ("re-scope... re-run step 1's full index read"; "re-read... only when re-scoping or right after a Concept/ADR is authored/edited — not on every turn") | Avoids the two failure modes of caching: stale data (never refreshed) and thrash (refreshed every turn). |
| 5 | Conflict classification taxonomy (Violation / Supersession / Out of scope / Drift) | Gives the model a decision procedure instead of open-ended judgment when a proposal touches something in `ARCHITECTURE.md` — improves consistency of grilling output. |

## Cons (with reasoning)

1. **No size/chunking guidance for "read in full."** `read_file`-style tools require explicit line ranges; the skill never tells the agent what to do if `ARCHITECTURE.md`'s Building-blocks/Concepts/ADR tables exceed a single comfortable read. A large real-world file risks a silent partial/truncated read — which directly defeats the "every row, not a sample" guarantee it's trying to make predictable.
2. **"Whose index summary *looks relevant*" is a vibes-based test.** There's no concrete rubric (keyword/module/service-name match), so which full records get opened is not reproducible across runs or models — two agents on the same task could load different context and reach different conclusions. This is the single biggest predictability risk in the file.
3. **Re-scope trigger is self-reported, not gated.** "Re-scope when the module, boundary, integration, or responsibility changes" relies on the model noticing its own state transition mid-conversation — LLMs are known to be weak at tracking implicit state changes over long context without an explicit checkpoint/precondition. No session ledger of "already opened" records is mandated, so this recall itself degrades over a long grilling session (lost-in-the-middle effect).
4. **Per-turn probe cost compounds with no ceiling.** Every probe (glossary, fuzzy language, scenarios, testing categories, Concept/ADR validation, code cross-ref) must be rechecked "after each user answer," and re-scoping can re-trigger the full-file read — in a long session this grows unbounded with no summarization/budget strategy.
5. **`manage-docs` is soft-linked, not gated.** `manage-docs` has `disable-model-invocation: true` (won't auto-load via description matching) yet `domain-modeling` only says "Consult it" (weak verb) rather than a hard precondition before writing. If skipped under context pressure, edits to `ARCHITECTURE.md` can silently violate `ARCHITECTURE-FORMAT.md`'s index-sync rules.
6. **No existence check before the unconditional read.** Step 1 says "Read `ARCHITECTURE.md` in full" without first checking it exists — the lazy-creation fallback lives only in `manage-docs`, so a fresh repo could hit a tool error before the agent recalls that fallback.

## Suggested improvements

1. Add a chunking rule: *"If the index tables or Building-blocks section span more than one comfortable read, issue multiple ranged reads covering the entire file — never stop at a partial read."*
2. Replace "looks relevant" with a checkable test: *"Open the full record if its Concept/ADR/service name, module, or keyword matches the current scope's terms, folder path, or stated boundary — otherwise leave it index-only."*
3. Convert re-scope from a soft trigger to a gate: *"Before discussing any module/service/boundary not yet opened this session, check it against the last-read index; if absent, re-run step 1."* Pair with a short in-session "opened records" ledger the agent maintains explicitly, so validation checks a concrete list instead of memory recall.
4. Elevate the `manage-docs` reference to a mandate: *"Before creating or editing `CONTEXT.md`/`ARCHITECTURE.md`/a Concept/an ADR, read `manage-docs/SKILL.md` and the relevant `*-FORMAT.md` if not already loaded this session."* — necessary specifically because `disable-model-invocation: true` means it won't self-trigger.
5. Add an explicit existence check ahead of step 1: *"If `ARCHITECTURE.md` doesn't exist yet, skip step 1 (see manage-docs lazy-creation) rather than treating a missing file as an error."*
6. For long sessions, add a lightweight budget note: periodically compress resolved terms/decisions instead of re-scanning full index tables on every re-scope, bounding cumulative token growth as conversations lengthen.
