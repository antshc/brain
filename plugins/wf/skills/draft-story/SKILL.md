---
description: Draft one standalone, atomic, testable, implementation-agnostic **User story** body beginning with a formatted Title and carrying Requirements, Acceptance Criteria, and optional Technical notes. Use when the user asks to write, draft, or format one User story, or when another skill needs one story's content.
name: draft-story
---

Draft and print one standalone **User story** body that advances one **Functional slice**. Own the formatted Title, Requirements, Acceptance Criteria, Implementation Decisions, Contracts Delta, and Technical notes for that body.

**Input:** an optional Initiative tag, required Deployable kind (`[FE]` or `[BE]`), Feature, Functional slice, verbatim Stakeholder requirement, Functional requirements addressed, and any source Business rules, Edge cases, error conditions, and Acceptance criteria needed to draft the story. Anything absent is derived from the standalone requirement text in context.

**Verbatim rule:** when a prior source artifact supplies a Feature, Functional slice, Stakeholder requirement, or Functional requirement, copy it **verbatim**. Derive only fields the source omits.

When available, use `CONTEXT.md` for project-specific domain language and `ARCHITECTURE.md` for module placement. The definitions below make this skill independently runnable.

## Vocabulary

- An **Initiative tag** is an optional SCREAMING_SNAKE_CASE label that groups stories under an Initiative.
- A **Deployable kind** is the `[FE]` or `[BE]` prefix that identifies the Deployable owning a Functional slice.
- A **Functional slice** is a deployable-local, end-to-end implementation of one distinct behavior or outcome.

## Principle
Describe system behavior, not implementation. Name the **entity and behavior**, never a widget, screen element, or technical artifact. If the input requirement already leaks a solution, raise it to the behavior it enables before writing the story; `normalize-requirements` skill owns that rule.

## Workflow
1. **Assemble the body** → write the exact Title line, then list the verbatim Functional requirements addressed. *Done when* the User story is one Functional slice owned by the named Deployable kind and contains no unrelated behavior.
2. **Derive Acceptance Criteria** → apply Acceptance Criteria below. *Done when* every applicable Business rule, Edge case, and error condition in the source lands in its own criterion, and input, processing, integration, state, and failure are covered.
3. **Verify** → Run `/normalize-requirements` skill over the Title, Requirements, and Acceptance Criteria, passing `CONTEXT.md` as the domain glossary when it exists, then confirm each criterion implies concrete code changes and maps to the Functional slice's responsibility. *Done when* Quality Check passes line by line.
4. **Contracts Delta (optional)** → if the User story changes an API, GUI, Database, Resource, or other contract, Run `/doc-contracts` skill for each touched contract kind and append its output to the optional Contracts Delta appendix. *Done when* every changed contract kind passes `/doc-contracts`' skill own done conditions.

## Acceptance Criteria
<acceptance-criteria-rule>
- Each criterion is a single, self-contained pass/fail check, verifiable without reading code.
- Phrase as: `{{outcome}} when {{condition}}` for behaviors; `If {{condition}}, {{actor}} must {{outcome}}` for invariants/edge cases. Vary the subject (entity, actor, outcome) — don't force "The system" every time.
- Cover: input, processing, integration, state, failure — one criterion each, not a labeled section.
- Use domain language (`CONTEXT.md`); state behavior, not implementation — no file paths, class/variable names, widget/screen, or other implementation details. Run `/normalize-requirements` skill to raise any leaked artifact to the behavior and entity it enables.
- State the exact outcome — never "works", "correctly", "properly", "as expected".
- Fold every applicable Business Rule, Edge Case, and relevant error condition from the source requirement into its own criterion here — do not create separate sections for them.
</acceptance-criteria-rule>

## Quality Check

- The first line matches `**Title:** {{[initiativeTag]|optional}}{{deployableKind|[FE] or [BE]}} {{stakeholderRequirement|verbatim Stakeholder requirement}}` exactly.
- With an Initiative tag, the Title begins like `**Title:** [NOTIFICATIONS][BE] Notify an account owner`; without one, it begins like `**Title:** [FE] Notify an account owner`.
- The Initiative tag, when supplied, is SCREAMING_SNAKE_CASE and sits immediately before the Deployable kind with no intervening space.
- The Stakeholder requirement portion of the Title is verbatim.
- The story is atomic and behavior-focused, constituting exactly one Functional slice owned by one Deployable.
- Requirements lists the Functional requirements addressed.
- Supplied Feature, Functional slice, Stakeholder requirement, and Functional requirements remain verbatim.
- Feature, Functional slice, and Stakeholder requirement name behavior and entities, not widgets, screens, or components; `/normalize-requirements` skill reported no remaining leak.
- Each criterion implies clear code changes and a QA can confirm pass or fail by testing.
- Implementation Decisions may name classes, types, objects, or endpoints for navigation, but never a file path or line number.
- Every changed contract kind has a complete delta that passes `/doc-contracts`' skill own done conditions.

## Output Format

Write the body for Product Owners and QA in plain business language, without code, class names, or technical jargon; each criterion is a clear, testable statement of expected behavior. The optional appendices are technical and live inside the collapsed **Technical notes** block.

- **Implementation Decisions** — omit unless the story requires a specific implementation decision. Class, type, object, and endpoint names are allowed for navigation; omit file paths and line numbers.
- **Contracts Delta** — omit unless this User story changes an API, GUI, Database, Resource, or other contract. Order its blocks API → Database → Resource → other → GUI.

```
**Title:** {{[initiativeTag]|optional}}{{deployableKind|[FE] or [BE]}} {{stakeholderRequirement|verbatim Stakeholder requirement}}

**Requirements:**
- {{functionalRequirement|verbatim reference or statement}}
- {{functionalRequirement|verbatim reference or statement}}

**Acceptance Criteria**
- {{outcome}} when {{condition}}.
- If {{condition}}, {{actor}} must {{outcome}}.
- ...

---
<details>
<summary>Technical notes</summary>

**Implementation Decisions** 
<!-- Omit this section unless an implementation decision is required. -->
- {{implementationDecision}}

**Contracts Delta**
<!-- Omit this section unless a contract changes. -->
{{contractsDeltaOutput|sections}}

</details>
```
