---
description: Rewrite an **idea description** or a **list of requirements** into one or more atomic, testable, implementation-agnostic **user stories** (behavior rules + acceptance criteria) that map to a production codebase..
name: to-story
---

Rewrite an **idea description** or a **list of requirements** into one or more atomic, testable, implementation-agnostic **user stories** (behavior rules + acceptance criteria) that map to a production codebase.

**Input & output shape:**
- A single idea or requirement → produce **one** story.
- A list of requirements, or an idea covering several distinct capabilities → produce **one story per capability**. Split anything non-atomic; never merge unrelated behaviors into one story.

Ground every requirement in the project's own language and structure: read `CONTEXT.md` for the domain glossary and `ARCHITECTURE.md` for the module layout.

Run a /grilling session to clarify any ambiguity, surface missing acceptance criteria, and ensure the story is atomic and testable.

## Principle
Describe system behavior, not implementation. Every requirement answers: WHO, WHAT behavior, WHAT entity, WHEN, WHAT result, WHAT on failure. Name the **entity and behavior**, never a widget, screen element, or technical artifact.

## Workflow
1. **Analyze input** → identify each distinct capability, its domain/module, actors, inputs, outputs, failure cases. One capability → one story; a list or multi-capability idea → one story each.
2. **Write the requirement statement** per story → lead with behavior and value, not a solution (see Requirement Statement). Atomic, behavior-focused, domain-specific.
3. **Derive acceptance criteria** per story as behavior rules (see below).
4. **Verify** each rule implies concrete code changes and maps to a responsibility.

## Requirement Statement
The statement is the single sentence that names the capability. Write it so it survives any design choice.

**Pattern:** `The <actor/system> continuously <behavior> <entity> for <who/scope>, so <business value>.`

A strong statement encodes:
- **Behavior** — what the system *does* (surface, keep current, block, reconcile), not what is *built* (button, banner, dropdown).
- **Entity** — the domain thing acted on (items in the cart, reserved stock, order total).
- **Scope/actor** — whose data or which context (the current shopper, authorized viewers, per storefront).
- **Value** — the outcome that justifies the work.
- **Implied hard parts** — the wording should hint at freshness, authorization, and failure so they surface as acceptance criteria.

**Lift-the-widget rule (core):** if the statement names a UI artifact or component (screen, service, table), it is describing the solution. Raise it one level to the behavior it enables, and move the artifact into design. For the full rule, the de-lifting reference table, and the solution-agnostic test, see [references/lift-the-widget.md](references/lift-the-widget.md).

## Acceptance Criteria
Write 3–6 criteria per requirement. If more are needed, the requirement is too broad — split it. Write each rule as one observable behavior:
- `The system must <behavior> when <condition>.`
- `If <condition>, the <actor> must <result>.`

Cover these rule types:
- **Input** — what the system accepts.
- **Processing** — internal validation/logic.
- **Integration** — external system interactions.
- **State** — persistence/state changes.
- **Failure** — error handling.

Criteria obey the lift-the-widget rule too: state an observable outcome, not the control that produces it. See [references/lift-the-widget.md](references/lift-the-widget.md) for examples and the verb → component hints.

## Quality Check (before output)
- Requirement is atomic and behavior-focused.
- Statement names a behavior + entity, not a widget, screen, or component. Apply the lift-the-widget rule.
- Statement is solution-agnostic: swapping UI or technology would not force a reword.
- Each rule = one behavior, exposes data flow + failure handling.
- Each rule implies clear code changes. If not, rewrite.

## Output & Examples
Write for Product Owners and QA — plain business language, no code, class names, or technical jargon. Each criterion is one clear, testable statement of expected behavior. For the exact output format (single and multiple stories), worked examples, and anti-patterns to reject, see [references/output-and-examples.md](references/output-and-examples.md).

## Golden Rule
A good criterion is written in plain business language a PO can approve and a QA can verify by testing — clear, specific, and unambiguous about the expected outcome. If a QA couldn't confirm it passed or failed, rewrite.
