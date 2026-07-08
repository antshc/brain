---
description: Package a **single requirement** or a **list of requirements** into one or more atomic, testable, implementation-agnostic **user stories** (title + business value + acceptance criteria) that map to a production codebase. Use when the user has requirements and wants stories, backlog-ready items, or acceptance criteria.
name: to-story
---

Package a **single requirement** or a **list of requirements** into one or more atomic, testable, implementation-agnostic **user stories** (title + business value + acceptance criteria) that map to a production codebase.

The input is typically the output of /to-requirements — a stakeholder requirement with its functional requirements, business rules, and edge cases. It also works standalone on any requirement text.

**Input & output shape:**
- A single requirement → produce **one** story.
- A list of requirements, or a requirement covering several distinct capabilities → produce **one story per capability**. Split anything non-atomic; never merge unrelated behaviors into one story.

Ground every story in the project's own language and structure: read `CONTEXT.md` for the domain glossary and `ARCHITECTURE.md` for the module layout.

## Principle
Describe system behavior, not implementation. Name the **entity and behavior**, never a widget, screen element, or technical artifact. If the input requirement already leaks a solution, raise it to the behavior it enables before writing the story (see the solution-agnostic rule).

## Workflow
1. **Analyze input** → identify each distinct capability, its domain/module, actors, inputs, outputs, failure cases. One capability → one story; a list or multi-capability input → one story each.
2. **Write the story header** per capability → a short title and a one-line business value that names the capability and why it matters.
3. **Derive acceptance criteria** per story as behavior rules (see below).
4. **Verify** each rule implies concrete code changes and maps to a responsibility.

## Acceptance Criteria
Write 3–6 criteria per story. If more are needed, the story is too broad — split it. Write each rule as one observable behavior:
- `The system must <behavior> when <condition>.`
- `If <condition>, the <actor> must <result>.`

Cover these rule types:
- **Input** — what the system accepts.
- **Processing** — internal validation/logic.
- **Integration** — external system interactions.
- **State** — persistence/state changes.
- **Failure** — error handling.

When the input comes from /to-requirements, its functional requirements, business rules, and edge cases map directly onto these criteria.

Criteria obey the solution-agnostic rule: state an observable outcome, not the control that produces it. See [../to-requirements/SKILL.md](../to-requirements/SKILL.md) and `SOLUTION-AGNOSTIC-TERMS.md` for the de-referencing tables and verb → component hints.

## Quality Check (before output)
- Story is atomic and behavior-focused.
- Title and value name a behavior + entity, not a widget, screen, or component. Apply the solution-agnostic rule.
- Story is solution-agnostic: swapping UI or technology would not force a reword.
- Each rule = one behavior, exposes data flow + failure handling.
- Each rule implies clear code changes. If not, rewrite.

## Output & Examples
Write for Product Owners and QA — plain business language, no code, class names, or technical jargon. Each criterion is one clear, testable statement of expected behavior. For the exact output format (single and multiple stories), worked examples, and anti-patterns to reject, see [references/output-and-examples.md](references/output-and-examples.md).

## Golden Rule
A good criterion is written in plain business language a PO can approve and a QA can verify by testing — clear, specific, and unambiguous about the expected outcome. If a QA couldn't confirm it passed or failed, rewrite.
