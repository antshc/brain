---
description: Draft one atomic, testable, implementation-agnostic **user story** — capability title, stakeholder requirement, functional requirements, acceptance criteria, Jira-sync metadata, and optional Technical notes appendices. Use when the user asks to write, draft, or format a user story, or wants acceptance criteria for a single capability; `/to-stories` runs it to format each story it slices.
name: draft-story
---

Draft **one** user story for **one capability on one technology layer** (`FE` or `BE`). Owns the story format and the rules every story obeys; callers that slice a requirement set into many stories run this skill once per story.

**Input:** a capability title, its stakeholder requirement, the functional requirements it covers, and the technology layer. A caller may also supply a story number, a feature slug, and a Blocked-by list. Anything the caller does not supply is derived from the requirement text in context.

**Verbatim rule:** when a prior requirement set is in context, copy the capability title, stakeholder requirement, and functional-requirements list **verbatim**; otherwise derive each from the standalone requirement text.

Ground the story in the project's own language and structure: read `CONTEXT.md` for the domain glossary and `ARCHITECTURE.md` for the module layout.

## Principle
Describe system behavior, not implementation. Name the **entity and behavior**, never a widget, screen element, or technical artifact. If the input requirement already leaks a solution, raise it to the behavior it enables before writing the story — `solution-agnostic` owns that rule.

## Workflow
1. **Assemble the reference block** → capability title, stakeholder requirement, functional-requirements list, under the verbatim rule. *Done when* the story covers exactly one capability on exactly one layer, with nothing from a neighbouring capability folded in.
2. **Attach sync metadata** → directly under the heading, add Jira ID / Epic ID / Blocked by. Values are placeholders (`TBD`) unless the caller supplies real ones; Blocked-by names only stories the caller listed, else `None`. This block sits outside the story body — never scrubbed, never counted as a criterion. *Done when* all three lines are present.
3. **Derive acceptance criteria** → apply the Acceptance Criteria rule below. *Done when* every Business Rule, Edge Case, and error condition in the source requirement lands in its own criterion, and each of input, processing, integration, state, and failure is covered.
4. **Scope to the layer** → a **BE** story's criteria cover API/data/contract/business-rule behavior; an **FE** story's cover presentation/interaction behavior. *Done when* no criterion tests the other layer's behavior.
5. **Verify** → Run `/solution-agnostic` skill over the capability title, stakeholder requirement, functional requirements, and acceptance criteria only, passing `CONTEXT.md` as the domain glossary — never the sync-metadata block or the Technical notes appendix — then confirm each criterion implies concrete code changes and maps to a responsibility. *Done when* the Quality Check below passes line by line.
6. **Contracts Delta (optional)** → if the capability changes an API, Database, or Resource contract, Run `/draft-contract-delta` skill **Assemble and write a contract delta** once per touched contract kind and append its output as the story's optional Contracts Delta appendix. For an `[FE]` story that adds or changes a surface, GUI component, or interaction, also Run that skill's **Assemble and write a GUI delta** and append its output as the **GUI delta** block closing that same appendix — a `[BE]` story never carries one. This appendix is technical, sits outside the Capability/Acceptance Criteria body, and is exempt from the scrub in step 5.

## Acceptance Criteria
<acceptance-criteria-rule>
- Each criterion is a single, self-contained pass/fail check, verifiable without reading code.
- Phrase as: `{{outcome}} when {{condition}}` for behaviors; `If {{condition}}, {{actor}} must {{outcome}}` for invariants/edge cases. Vary the subject (entity, actor, outcome) — don't force "The system" every time.
- Cover: input, processing, integration, state, failure — one criterion each, not a labeled section.
- Use domain language (`CONTEXT.md`); state behavior, not implementation — no file paths, class/variable names, widget/screen, or other implementation details. Run `/solution-agnostic` skill to raise any leaked artifact to the behavior and entity it enables.
- State the exact outcome — never "works", "correctly", "properly", "as expected".
- Fold every applicable Business Rule, Edge Case, and relevant error condition from the source requirement into its own criterion here — do not create separate sections for them.
</acceptance-criteria-rule>

## Quality Check (before output)
- Story is atomic and behavior-focused, scoped to exactly one capability and one technology layer.
- The story names its **capability**, includes the **stakeholder requirement**, and lists the **functional requirements** it covers.
- When a prior requirement set is in context, the capability title, stakeholder requirement, and functional-requirements list are copied **verbatim**.
- Capability and stakeholder requirement name a behavior + entity, not a widget, screen, or component — `/solution-agnostic` reported no remaining leak.
- Each criterion implies clear code changes and a QA could confirm pass/fail by testing. If not, rewrite.
- Jira ID, Epic ID, and Blocked-by sit in a metadata block directly under the heading, outside the scrubbed body; Blocked-by lists only `(Story n, Jira ID placeholder)` pairs the caller supplied, or `None`.
- Implementation Decisions may name classes, types, objects, or endpoints for navigation, but never a file path or line number.
- An `[FE]` story that changes a surface or interaction carries a GUI delta block closing Contracts Delta, passing `/draft-contract-delta`'s own Done-when checks; a `[BE]` story carries neither.
- The `[SLUG]` feature tag is present in the heading only if the user asked for it, is SCREAMING_SNAKE_CASE, and — if already present on a story being edited — is kept unchanged.

## Output Format

Write the story body for Product Owners and QA in plain business language, without code, class names, or technical jargon; each criterion is a clear, testable statement of expected behavior. The sync-metadata block and the optional appendices (**Implementation Decisions**, **Contracts Delta**) are explicitly technical/mechanical and sit outside that plain-language body.

Both appendices are optional and live inside the collapsed **Technical notes** block:
- **Implementation Decisions** — omit unless this capability requires a specific implementation decision. Class, type, object, and endpoint names are welcome for navigation; never a file path or line number.
- **Contracts Delta** — omit unless this capability changes an API, Database, or Resource contract, or (FE stories only) a GUI surface. Order its blocks API → Database → Resource → other → GUI.

The heading may carry an optional feature slug, formatted `[SLUG]` in SCREAMING_SNAKE_CASE (uppercase words joined by underscores, e.g. `[NOTIFICATIONS]`), prepended before the `[{{technology}}]` tag. Add it **only when the user explicitly asks for a feature slug** — never by default. Once a slug is present in a title, preserve it verbatim on any later edit to that story; never strip or rename it.

For a standalone story, the heading is `## [{{technology}}] {{capabilityTitle}}`. When the caller supplies a story number, prefix it: `## Story {{n}} — [{{technology}}] {{capabilityTitle}}`. `{{technology}}` is `FE` or `BE`.

```
## Story {{n|omit the "Story {{n}} — " prefix for a standalone story}} — {{[SLUG]|optional, SCREAMING_SNAKE_CASE, only when user asked for it }}[{{technology|FE|BE}}] {{capabilityTitle}}

**Jira ID:** {{jiraId|TBD}}
**Epic ID:** {{epicId|TBD}}
**Blocked by:** {{blockedBy| (Story {{n}}, {{jiraId|TBD}}), (Story {{m}}, {{jiraId|TBD}}) | None}}

{{capabilityTitle|behavior + entity, no surface or placement}}

{{stakeholderRequirement| The <actor> needs to <behavior> <entity>, so <value>}}

### Acceptance Criteria
- {{outcome}} when {{condition}}.
- If {{condition}}, {{actor}} must {{outcome}}.
- ...

---
<details>
<summary>Technical notes</summary>

### Implementation Decisions 
<!-- technical tone -->
- {{implementationDecision1}}
- ...

### Contracts Delta
<!-- technical tone -->
{{contractsDeltaOutput| sections}}
{{guiDeltaOutput| FE stories only; omit for BE}}

</details>
```
