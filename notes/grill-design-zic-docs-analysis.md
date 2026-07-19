# Analysis: `grill-design` skill × zic-docs (dynamic Concept/ADR coverage)

Scope: does `grill-design` (→ `grilling` + `domain-modeling`) reliably surface every *relevant*
Concept/ADR during feature design on zic-docs, given that the Concept/ADR list is dynamic and
project-specific (different repos will have entirely different lists/architectures)?

## How grill-design resolves

`grill-design/SKILL.md` is a one-line pointer: run `/grilling` using `/domain-modeling`. The
actual mechanics live in `domain-modeling/SKILL.md`'s **Load strategy guardrails**, backed by
`manage-docs/ARCHITECTURE-FORMAT.md`, `CONCEPT-FORMAT.md`, `ADR-FORMAT.md`. For zic-docs this
means the 9-row Concepts table and 5-row ADR table in `zic-docs/ARCHITECTURE.md`.

## Pros

- **Dynamic by construction, not hardcoded.** Nothing names a fixed Concept/ADR list — it reads
  whatever `ARCHITECTURE.md` contains at session time. Works identically on a repo with a
  completely different architecture, since it only consumes the two generic index tables.
- **Two-tier retrieval** (index scan → open-full-only-if-relevant) keeps context budget flat as
  `docs/concepts/`/`docs/adr/` grow — relevant since zic-docs already has 14 records.
- **"Every row, not a sample"** plus chunked-read fallback avoids a silent partial/truncated
  index read on a long table.
- **Continuous re-validation** ("stays live for the whole session... a later answer can
  retroactively put an earlier one in conflict") — coverage isn't a single upfront pass.
- **Session ledger** (`/memories/session/domain-model-ledger.md`) gives an inspectable record of
  which Concepts/ADRs were opened and why.
- **Conflict taxonomy** (Violation / Supersession / Out-of-scope / Drift) avoids flattening every
  mismatch into "you're wrong."
- **Test-category challenge** ties into zic-docs' own `Testing Strategy`/Concept 0004, not a
  generic "write unit tests" assumption.

## Cons / gaps

1. **Relevance test is keyword/scope-gated, and that's circular for the things it should catch.**
   A full record opens only when its title/summary/module/keyword "matches a term, folder, or
   boundary already named in the current scope." If a feature design never says "DynamoDB,"
   "task metadata," or "bulk," Concepts/ADRs like 0009 (DynamoDB placement) or 0005/0006 (task
   metadata) can silently never trigger, even if the feature structurally touches them.
2. **No distinction between "backbone, always-applies" Concepts and "conditional" ones.** By
   `CONCEPT-FORMAT.md`'s own definition, a Concept is a pattern "every feature is expected to
   follow" — so Concepts 0001–0003/0008 (layering, module design, feature-module boundaries)
   should be unconditionally in-scope for any zic-docs feature touching code structure, not
   keyword-matched into relevance like an ADR.
3. **The `Cornerstone`/`Local` ADR tag defined in `ARCHITECTURE-FORMAT.md` is unused in
   zic-docs.** The format says ADRs should be tagged Cornerstone (affects multiple building
   blocks/structure) vs Local, but zic-docs' actual table is only `# | Decision | Summary` — no
   tag column. That tag is exactly the signal needed to force-check structurally significant
   ADRs regardless of keyword match.
4. **No closing completeness audit.** Continuous per-turn validation exists, but nothing
   requires a final pass down the full Concept/ADR index before the grill session concludes.
   Coverage is emergent from conversation drift, not gated at the end.
5. **`grill-design` itself is pure composition** — auditing "will this cover the full backbone"
   requires tracing two hops deep (`grill-design` → `domain-modeling` → `manage-docs` formats),
   and today the guarantee stops at "index-scanned," not "every row explicitly ruled in or out."

## Verification against zic-docs' actual list

Walking the 9 Concepts + 5 ADRs in `zic-docs/ARCHITECTURE.md`:

- **Reliably swept** (universal/backbone, near-certain to be named in any feature scope): 0002
  (deep modules), 0003 (IDesign layering), 0008 (feature-module horizontal split), 0004 (testing
  strategy — explicitly re-triggered by its own probe).
- **At risk of being skipped** unless the conversation happens to name the right term: 0009
  (DynamoDB placement), 0007 (config tweaks), 0006 (bulk ops), ADR 0004 (tasks retention), ADR
  0005/0006 (task metadata/Initiator capture), ADR 0008 (ScaleAccounts) — all narrow/localized
  and easy to miss if the feature touches them implicitly (e.g. adding a task field without
  saying "metadata blob").
- 0005 (Keycloak auth) is likely safe since "auth"/"authorize" tends to surface naturally in
  REST feature design.

So: universal Concepts have reasonably reliable coverage today. Localized ADRs and conditional
Concepts genuinely depend on the conversation surfacing the matching keyword — the dynamic,
project-specific risk isn't fully closed.

## Suggested improvements

1. **Split the relevance rule by kind.** In `domain-modeling`'s Load strategy guardrails, add:
   "Every Concept row is presumed in-scope unless clearly inapplicable — Concepts are backbone
   rules every feature must follow, per `CONCEPT-FORMAT.md`. Apply the keyword/module relevance
   test only to ADRs (localized decisions)."
2. **Adopt the `Cornerstone`/`Local` ADR tag** in zic-docs' `ARCHITECTURE.md` (already defined in
   the format, just unused) and have `domain-modeling` force-check Cornerstone-tagged ADRs the
   same way it force-checks Concepts, gating only Local ADRs behind keyword relevance.
3. **Add a closing completeness sweep** to `grilling`/`domain-modeling`: before concluding a
   grill session, output a one-line disposition per index row (Applied / Not applicable /
   Violated / Superseded) for the full Concepts+ADR table.
4. **Give each index row an explicit "applies-when" trigger**, generalizing what Concept 0004
   already does ("Scoped via source-folder → test-project trigger map") to every row, so
   relevance-matching stops depending on the conversation happening to use the right word.
