---
description: Package a **single requirement** or a **list of requirements** into one or more atomic, testable, implementation-agnostic **user stories** — broken down by capability and technology layer (FE/BE), each carrying a capability reference, stakeholder requirement, functional-requirements list, acceptance criteria, and Jira-sync metadata (Jira ID, Epic ID, Blocked by) — that map to a production codebase. Use when the user has requirements and wants stories, backlog-ready items, acceptance criteria, or FE/BE-split tickets ready to sync with Jira.
name: to-stories
---

Package a **single requirement** or a **list of requirements** into one or more atomic, testable, implementation-agnostic **user stories**, broken down **by capability and technology layer (FE/BE)**. Each story carries four blocks: a **capability reference**, the **stakeholder requirement**, the **functional-requirements list** it covers, and the **acceptance criteria** — plus a **Jira-sync metadata** line (Jira ID, Epic ID, Blocked by) under its heading.

The input is typically a prior requirement set — a capability with its stakeholder requirement, functional requirements, business rules, and edge cases. It also works standalone on any requirement text.

**Input & output shape:**
- Produce **one story per capability per technology layer**. A capability touching only one layer → one story; a capability spanning both **FE** and **BE** → one story per layer, only after the user approves the breakdown (see Workflow). Split anything non-atomic; never merge unrelated behaviors into one story.
- When a prior requirement set is in context, **copy the capability title, stakeholder requirement, and functional-requirements list verbatim** into the story's reference blocks. When the input is standalone requirement text, derive them from that text.

Ground every story in the project's own language and structure: read `CONTEXT.md` for the domain glossary and `ARCHITECTURE.md` for the module layout.

This skill is self-contained: capability identification and the solution-agnostic/contracts-delta rules it needs live below and in [references/](references/) — it never has to invoke another skill to produce a story.

## Principle
Describe system behavior, not implementation. Name the **entity and behavior**, never a widget, screen element, or technical artifact. If the input requirement already leaks a solution, raise it to the behavior it enables before writing the story (see the solution-agnostic rule).

## Capability Identification
Before assembling a story, confirm each candidate is one **capability** — behavior the system provides independently of where it appears, that survives after the current change completes — never a one-off task.
- **Group by shared purpose.** One capability = one purpose statement covering all its requirements. Split when parts differ substantially in actor goals, business rules, permissions, lifecycle, failure handling, external contracts, ownership, or rate of change — that difference is the signal to split, not merge.
- **Strip placement first.** A candidate naming a surface ("show count in header") isn't a capability yet — rewrite it as pure behavior ("provide an active count summary") before judging its scope.
- **Test independence.** If one group's rules can change without touching the other's, they are separate capabilities, hence separate stories.
- **Don't atomize trivial output.** A single tiny output with no behavioral scope of its own belongs inside its broader stable capability, not alone.
- **Done when** every input requirement lands in exactly one capability and no capability bundles two independently-changing behaviors.

## Workflow
1. **Analyze input** → identify each distinct capability (apply Capability Identification above), its domain/module, actors, inputs, outputs, failure cases.
2. **Propose breakdown** → for each capability, classify which technology layer(s) it involves — **BE**: API/data/contract/business-rule behavior; **FE**: presentation/interaction behavior — from the acceptance-criteria evidence. Present a numbered breakdown table (capability → technology tag(s) → story count) to the user and wait for explicit approval; revise and re-confirm on requested merges/splits/reassignments. Do not draft any story before approval.
3. **Assemble the reference block** per story → copy the **capability title**, **stakeholder requirement**, and **functional-requirements list** verbatim from the prior requirement set when it is in context; otherwise derive each from the standalone requirement text. A capability spanning both layers keeps the same title/stakeholder requirement/functional-requirements list per story, one story per layer, with acceptance criteria scoped to that layer's behavior only.
4. **Attach sync metadata** → immediately under each story heading, add the Jira ID / Epic ID / Blocked-by metadata block (see Output Format). Values are placeholders only (`TBD`); Blocked-by lists only stories from this same batch. This block sits outside the story body — never scrubbed, never counted as a criterion.
5. **Derive acceptance criteria** per story as behavior rules (see below).
6. **Verify** → apply the scrub in [references/solution-agnostic.md](references/solution-agnostic.md) over the capability title, stakeholder requirement, functional requirements, and acceptance criteria only — never the sync-metadata block or the Implementation notes appendix — then confirm each rule implies concrete code changes and maps to a responsibility.
7. **Contracts Delta (optional)** → if the capability changes an API, Database, or Resource contract, follow [references/contracts-delta.md](references/contracts-delta.md) **Assemble the contract delta** once per touched contract kind and append the result as the story's optional Contracts Delta appendix. For an `[FE]` story that adds or changes a surface, GUI component, or interaction, also follow that file's **Assemble the GUI delta** and append its output as the **GUI delta** block at the end of that same appendix — a `[BE]` story never carries one. This appendix is technical and not part of the Capability/Acceptance Criteria body — it is exempt from the scrub in step 6.

## Acceptance Criteria
<acceptance-criteria-rule>
- Each criterion is a single, self-contained pass/fail check, verifiable without reading code.
- Phrase as: `{{outcome}} when {{condition}}` for behaviors; `If {{condition}}, {{actor}} must {{outcome}}` for invariants/edge cases. Vary the subject (entity, actor, outcome) — don't force "The system" every time.
- Cover: input, processing, integration, state, failure — one criterion each, not a labeled section.
- Use domain language (`CONTEXT.md`); apply the solution-agnostic rule — no file paths, class/variable names, widget/screen, or other implementation details. Apply the scrub in [references/solution-agnostic.md](references/solution-agnostic.md) to raise any leaked artifact to the behavior and entity it enables.
- State the exact outcome — never "works", "correctly", "properly", "as expected".
- Fold every applicable Business Rule, Edge Case, and relevant error condition from the source requirement into its own criterion here — do not create separate sections for them.
</acceptance-criteria-rule>

## Quality Check (before output)
- Story is atomic and behavior-focused, scoped to exactly one capability and one technology layer.
- Each story names its **capability**, includes the **stakeholder requirement**, and lists the **functional requirements** it covers.
- When a prior requirement set is in context, the capability title, stakeholder requirement, and functional-requirements list are copied **verbatim**.
- Capability and stakeholder requirement name a behavior + entity, not a widget, screen, or component. Apply the solution-agnostic rule.
- Each criterion implies clear code changes and a QA could confirm pass/fail by testing. If not, rewrite.
- The capability passed the Capability Identification grouping/independence checks before any story was drafted.
- The FE/BE breakdown table was presented and explicitly approved by the user before any story was drafted.
- Jira ID, Epic ID, and Blocked-by sit in a metadata block directly under the heading, outside the scrubbed body; Blocked-by lists only `(Story n, Jira ID placeholder)` pairs from this batch, or `None`.
- Implementation notes may name classes, types, objects, or endpoints for navigation, but never a file path or line number.
- Every `[FE]` story that changes a surface or interaction carries a GUI delta block at the end of Contracts Delta, with an `**API calls**` block closing each changed surface entry and showing request and response for each distinct call it fires; a `[BE]` story carries neither.
- The `[SLUG]` feature tag is present in the heading only if the user asked for it, is SCREAMING_SNAKE_CASE, and — if already present on a story being edited — is kept unchanged.

## Output Format

Each story starts with a heading tagging its **technology layer** (`FE` or `BE`), immediately followed by its **Jira-sync metadata** (Jira ID, Epic ID, Blocked by), then the capability title and stakeholder requirement, then **Acceptance Criteria**. It may also include optional technical appendices: **Implementation Decisions** and **Contracts Delta**. Write the story content for Product Owners and QA in plain business language, without code, class names, or technical jargon; each criterion must be a clear, testable statement of expected behavior. The sync-metadata block and the optional appendices are explicitly technical/mechanical and sit outside that plain-language body. When a prior requirement set is in context, copy the capability title and stakeholder requirement verbatim; otherwise derive them from the requirement text.

The heading may carry an optional feature slug, formatted `[SLUG]` in SCREAMING_SNAKE_CASE (uppercase words joined by underscores, e.g. `[NOTIFICATIONS]`), appended after the capability title. Add it **only when the user explicitly asks for a feature slug** — never by default. Once a slug is present in a title, preserve it verbatim on any later edit to that story; never strip or rename it.

Use the template below for every story. For a single story, the heading is `## [{{technology}}] {{capabilityTitle}}{{ [SLUG]|optional}}`. For multiple stories, repeat the block once per capability/technology pair, numbering each heading `Story {{n}} — [{{technology}}] {{capabilityTitle}}{{ [SLUG]|optional}}`; `{{technology}}` is `FE` or `BE`.

```
## Story {{n}} — [{{technology|FE|BE}}] {{capabilityTitle}}{{ [SLUG]|optional, SCREAMING_SNAKE_CASE, only when user asked for it}}

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
<summary>Implementation notes</summary>

### Implementation Decisions 
<!-- technical tone, optional - omit unless this capability requires a specific implementation decision. Class/type/object/endpoint names welcome for navigation; never a file path or line number. -->
- {{implementationDecision1}}
- ...

### Contracts Delta
<!-- optional - omit unless this capability changes an API, Database, or Resource contract, or (FE stories only) a GUI surface. Follow references/contracts-delta.md: Assemble the contract delta once per touched contract kind (API, Database, Resource), then Assemble the GUI delta for the GUI block. Order: API → Database → Resource → other → GUI. -->
{{contractsDeltaOutput| sections}}
{{guiDeltaOutput| FE stories only; omit for BE}}

</details>
```
