---
description: Package a **single requirement** or a **list of requirements** into one or more atomic, testable, implementation-agnostic **user stories** — broken down by capability, each carrying a capability reference, stakeholder requirement, functional-requirements list, and acceptance criteria — that map to a production codebase. Use when the user has requirements and wants stories, backlog-ready items, or acceptance criteria.
name: to-stories
---

Package a **single requirement** or a **list of requirements** into one or more atomic, testable, implementation-agnostic **user stories**, broken down **by capability**. Each story carries four blocks: a **capability reference**, the **stakeholder requirement**, the **functional-requirements list** it covers, and the **acceptance criteria**.

The input is typically a prior requirement set — a capability with its stakeholder requirement, functional requirements, business rules, and edge cases. It also works standalone on any requirement text.

**Input & output shape:**
- Produce **one story per capability**. A single-capability requirement → one story; a list of requirements, or a requirement covering several distinct capabilities → one story each. Split anything non-atomic; never merge unrelated behaviors into one story.
- When a prior requirement set is in context, **copy the capability title, stakeholder requirement, and functional-requirements list verbatim** into the story's reference blocks. When the input is standalone requirement text, derive them from that text.

Ground every story in the project's own language and structure: read `CONTEXT.md` for the domain glossary and `ARCHITECTURE.md` for the module layout.

## Principle
Describe system behavior, not implementation. Name the **entity and behavior**, never a widget, screen element, or technical artifact. If the input requirement already leaks a solution, raise it to the behavior it enables before writing the story (see the solution-agnostic rule).

## Workflow
1. **Analyze input** → identify each distinct capability, its domain/module, actors, inputs, outputs, failure cases. One capability → one story; a list or multi-capability input → one story each.
2. **Assemble the reference block** per capability → copy the **capability title**, **stakeholder requirement**, and **functional-requirements list** verbatim from the prior requirement set when it is in context; otherwise derive each from the standalone requirement text.
3. **Derive acceptance criteria** per story as behavior rules (see below).
4. **Verify** → run `/solution-agnostic` over every story and criterion to scrub implementation artifacts, then confirm each rule implies concrete code changes and maps to a responsibility.

## Acceptance Criteria
<acceptance-criteria-rule>
- Each criterion is a single, self-contained pass/fail check, verifiable without reading code.
- Phrase as: `{{outcome}} when {{condition}}` for behaviors; `If {{condition}}, {{actor}} must {{outcome}}` for invariants/edge cases. Vary the subject (entity, actor, outcome) — don't force "The system" every time.
- Cover: input, processing, integration, state, failure — one criterion each, not a labeled section.
- Use domain language (`CONTEXT.md`); apply the solution-agnostic rule — no widget/screen/code terms. Run `/solution-agnostic` to raise any leaked artifact to the behavior and entity it enables.
- State the exact outcome — never "works", "correctly", "properly", "as expected".
- Fold every applicable Business Rule and Edge Case from the source requirement into its own criterion here — do not create separate sections for them.
</acceptance-criteria-rule>

## Quality Check (before output)
- Story is atomic and behavior-focused, scoped to exactly one capability.
- Each story names its **capability**, includes the **stakeholder requirement**, and lists the **functional requirements** it covers.
- When a prior requirement set is in context, the capability title, stakeholder requirement, and functional-requirements list are copied **verbatim**.
- Capability and stakeholder requirement name a behavior + entity, not a widget, screen, or component. Apply the solution-agnostic rule.
- Each criterion implies clear code changes and a QA could confirm pass/fail by testing. If not, rewrite.

## Output & Examples
For the exact output format (single and multiple stories) see [references/output-format.md](references/output-format.md). For worked examples and anti-patterns to reject, see [references/examples.md](references/examples.md).
