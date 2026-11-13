# Index Defaults

Use when authoring or repairing an ADR or Concept index row. Keep the existing `**Trigger:** … **Default:** …` cell; no new columns or record-body sections.

## Contract

- One independently reusable choice → one **decision key**. Use the project's decision vocabulary; no numbering or invented taxonomy.
- One simple choice → a single sentence remains valid. Several choices or settled variants → keyed clauses separated by semicolons on one physical line.
- Each clause states checkable scope/selection conditions, the choice when the design is silent, settled exceptions if any, and its governing body anchor. Scope already explicit in the body may be referenced; never leave the applicable variant ambiguous.
- Format: `{{key}} — when {{condition}}, {{choice}}; except {{settledException}}; source: [{{anchorTitle}}]({{recordPath}}#{{anchor}})`. Omit the exception segment when none is documented; repeat the keyed clause for another settled branch.
- Derive every choice, condition, and exception from settled rules or decisions. Keep code observations, proposals, and open menus out of defaults. MUST NOT widen scope, invent policy, or pick an arbitrary fallback to increase assumption coverage, even if it avoids a question.
- Different answers for overlapping conditions need explicit settled precedence; otherwise return the conflict to the caller. A narrower scope, newer record, or ADR label alone does not establish an override.
- The body remains authoritative. Keep row clauses consistent with its decisions, rules, variants, and scope; anchor links are evidence pointers, not substitutes for the direct choice.
- Existing single-sentence defaults remain compatible; do not bulk-migrate records. Add keys/anchors when repairing or extending the affected choice. Preserve unrelated defaults and caller-confirmed wording.

Rationale: make settled choices directly reusable without turning indexing into policy discovery.

## Completion criteria

- Each clause directly selects a choice within established scope; every condition and exception has a settled source.
- Applicable overlapping clauses agree or name an explicit settled override.
- Trigger generation received the authored default; each clause's applicability is discoverable through domain phrases.
- Record and index agree; unresolved policy or a caller-confirmed mismatch is reported, not silently repaired.
