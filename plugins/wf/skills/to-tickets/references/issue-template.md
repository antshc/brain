<issue-template>
## Parent Spec

#{{specIssueNumber}}

## What to build
<what-to-build-rule>
- State included outcome, explicit exclusions, and enough behavior context to understand the task; leave implementation discovery to the implementer.
- For functional changes, describe behavior across all touched integration layers, not a layer-by-layer breakdown. For structural changes, describe the complete relocation and required reference updates without introducing logic changes.
- Avoid specific file paths or code snippets — they go stale fast. Exception: structural relocation tasks must identify intended source and destination paths.
- Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it here and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.
</what-to-build-rule>

## Acceptance criteria
<acceptance-criteria-rule>
- Each criterion is a single, self-contained pass/fail check, verifiable without reading code or the spec.
- Phrase as an observable check: "When {{action}}, then {{observableOutcome}}" for behaviors; "If {{condition}}, then {{expectedOutcome}}" for invariants and boundary conditions. For structural work, include checks of intended locations, updated references, and unchanged regression behavior.
- Use the domain language of the spec or `GLOSSARY.md`; keep functional criteria solution-agnostic. Structural criteria may name exact source/destination paths, namespaces, symbols, and project references needed to prove the relocation.
- State the exact expected outcome — never vague words like "works", "correctly", "properly", "as expected".
- Fold every applicable Business Rule (`If {{condition}}, {{invariant}}`), Edge Case (`{{boundaryCondition}} → {{expectedHandling}}`), and relevant error condition into its own criterion here, rephrased per the format above — do not create separate sections for them.
</acceptance-criteria-rule>

- [ ] Acceptance criteria 1
- [ ] Acceptance criteria 2
- [ ] Acceptance criteria 3

## Requirements addressed
<requirements-addressed-rule>
- One bullet per addressed spec item: its number, then the spec's text copied verbatim — never numbers alone, never paraphrased, merged, or shortened.
- Omit a subsection if the spec has none of that kind, or none apply to this slice.
</requirements-addressed-rule>

**Functional Requirements:**

- {{number}}. {{verbatimSpecText}}
...

**Business Rule:**

- {{number}}. {{verbatimSpecText}}
...

**Edge cases:**

- {{number}}. {{verbatimSpecText}}
...

## Implementation Decisions
<implementation-decisions-rule>
- State producer contracts and supplying tickets when applicable, compatibility constraints, and assumptions; distinguish observed contracts from assumptions needing confirmation.
- Use short technical statements and implementation-oriented language.
- Avoid file paths or code snippets except exact structural relocation constraints.
</implementation-decisions-rule>

- {{implementationDecision1}}
- {{implementationDecision2}}

## Relevant Concepts
<relevant-concepts-rule>
- Mandatory whenever at least one Concept or ADR applies to this slice.
- One bullet per constraining Concept or ADR. Must carry enough detail to implement the rule without opening the file — the link back to the record is optional supporting context, not a substitute for the summary.
- Bullet must be self-explanatory — no further repo exploration needed to implement.
- No specific file paths or code snippets (they become outdated quickly).
</relevant-concepts-rule>

- {{ruleSummaryAsItAppliesToThisSlice}} ([{{conceptTitle}}](docs/concepts/{{kind}}-{{slug}}.md))
- {{ruleSummaryAsItAppliesToThisSlice}} ([{{decisionTitle}}](docs/adr/{{slug}}.md))

If a summary above isn't enough to implement its rule, open the linked record for full detail before implementing.

## Contracts Delta
<!-- Omit this section entirely if this slice touches no API, Database, or Resource contract. -->

*Run `doc-contracts` skill once per touched contract kind (API, Database, Resource) to write the REST endpoint, table schema, or resource contract delta as a terse diff;* inline its output verbatim here, one block per kind.

## Affected layers & modules
<affected-layers-rule>
- State which layers/modules this task touches (or relocates) and any Cross-Module Dependency Rules that constrain it, so the implementing agent doesn't need to rediscover placement in the repo.
- Source layer headings and Cross-Module Dependency Rules from the Concept or ADR opened in step 2. Fall back to `ARCHITECTURE.md`'s structural sections (Building blocks/layering) only if neither suffices to place the code.
- If the slice belongs to a specific building block, also scan the `Deployables` table (under `Building blocks` in `ARCHITECTURE.md`) and load the matching block's record (`docs/building-blocks/{{slug}}.md`) for its layer headings and Cross-Module Dependency Rules.
</affected-layers-rule>

- {{layerOrModuleName}}: {{crossModuleDependencyRule}}

## Verify section

List tests to add, update, and run for this task.
- *Mandatory*: The Verify section must be present in every issue. If a Concept about testing/verification exists in `docs/concepts/`, use it (and its link/summary above) to guide the verification. Include the commands that will run the integration or REST API automation tests.
- For functional changes, test external behavior, not implementation details. For structural tasks, verify intended paths/references and unchanged behavior using existing regression/API integration tests; add tests only where coverage is insufficient.
- Map every criterion to a concrete check, exact command/manual action, prerequisites, expected result, and retained evidence. Name affected test modules and prior art; report unavailable prerequisites, never invent commands.
- Default to existing API integration tests for API behavior; add focused contract, concurrency, retry, or boundary checks where the API seam cannot adequately expose the risk. For structural work, include deterministic location/reference checks and existing regression tests.

</issue-template>
