---
description: Turn an **idea** or **business need** into a **stakeholder requirement** with its **functional requirements**, **business rules**, and **edge cases** — solution-agnostic. Use when the user wants to elicit, write, or structure requirements, capture what a user needs, or derive functional requirements from a feature idea.
name: to-requirements
---

Turn an **idea** or **business need** into a structured requirement set: one **stakeholder requirement** and the **functional requirements**, **business rules**, and **edge cases** it implies. One capability yields one set; an idea spanning several distinct capabilities yields one set per capability — never merged.

## Solution-agnostic
Every requirement is **solution-agnostic**: it names a **behavior and entity** — what the system *does* and the outcome the actor gets — never an implementation artifact (widget, screen, table, endpoint, flag, worker, access role). The test: if swapping the UI or technology would force a reword, the statement is over-specified. When a statement names an artifact, raise it one level to the behavior it enables and move the artifact into design. This governs the **capability title**, stakeholder requirements, functional requirements, and criteria alike. When `SOLUTION-AGNOSTIC-TERMS.md` is present in the repo, apply its de-referencing tables (UI, data, API, state, process, access) for the corrective move; when it is absent, apply the rule from the plain-language behavior alone.

The **capability title** names the behavior and entity, never the surface or placement that delivers it. Titles must not reference a page, screen, header, panel, tab, dropdown, grid, badge, endpoint, or route. Raise any such term to the behavior it enables — the same swap test applies: if renaming the screen or moving the control would force a retitle, the title is over-specified.
- Reject: *Surface active alerts in the page header* · *Manage tasks on the Monitoring page* · *View aggregated health on the Dashboard*.
- Prefer: *Surface the count of active alerts* · *Manage tasks* · *View aggregated ZIC health*.

## Domain vocabulary
Name entities and behaviors in the project's approved language. `CONTEXT.md` is the domain glossary — the source of allowed terms. When it exists in the repo, prefer its exact terms over synonyms so requirements match the shared language; when it is absent, fall back to the plainest business language for the domain.

## Workflow
1. **Analyze input** → split the input into **capabilities** using the grouping rule and five-question decision process in [references/capability-detection.md](references/capability-detection.md) — grounding first in `CONTEXT.md` (name each capability in approved domain terms) and `ARCHITECTURE.md` (module boundaries signal ownership and rates of change: a candidate straddling two modules is a split signal) — then note each capability's domain/module, actors, inputs, and outputs. *Done when* every capability passes all five questions and no two independently-changing capabilities share a set.
2. **Grill** → consult the taxonomy in [references/requirement-types.md](references/requirement-types.md); run /grilling to resolve ambiguity and surface actors, failure paths, and edge cases. *Done when* no open ambiguity remains before writing.
3. **Write the stakeholder requirement** → one sentence per capability (see **Stakeholder Requirement**).
4. **Derive functional requirements** → the `The system must …` statements that make the capability concrete and testable (see **Functional Requirements**).
5. **Capture business rules** → the invariants that must always hold (see **Business Rules**).
6. **Capture edge cases** → the boundary and failure conditions (see **Edge Cases**).
7. **Verify** → every requirement passes the **Quality Check**.

## Stakeholder Requirement
The single sentence that names what the user needs to achieve, written to survive any design choice.

**Pattern:** `The <actor/stakeholder> needs to <behavior> <entity> for <who/scope>, so <business value>.`

A strong statement encodes:
- **Behavior** — what the user needs the system to *do* (surface, keep current, block, reconcile), not what is *built* (button, banner, dropdown).
- **Entity** — the domain thing acted on (items in the cart, reserved stock, deleted files).
- **Scope/actor** — whose data or which context (the current shopper, administrators, per storefront).
- **Value** — the outcome that justifies the work.

Keep it **solution-agnostic**: the sentence names a behavior, never an artifact.

## Functional Requirements
Write each as `The system must <behavior> when <condition>.` — specific, testable, and focused on externally visible behavior. When `ARCHITECTURE.md` is present, use its module layout to find the capability's dependencies and surface the **Integration** and **Degraded behavior** requirements — name the behavior at each boundary, never the component that implements it. Cover, at minimum:
- **Capability** — what actions the system performs and what outcomes it produces.
- **Integration** — external system interactions the capability depends on.
- **State** — persistence, retention, and state changes.
- **Permissions** — who may and may not perform the action.
- **Degraded behavior** — what still works when a dependency is slow or fails.

Keep it **solution-agnostic**: state an observable outcome, not the control that produces it.

## Business Rules
Write each as a policy that must **always** hold, independent of any single interaction: `If <condition>, <the invariant that must be true>.` Business rules drive validation, eligibility, permissions, calculations, and display logic. A functional requirement says a capability must exist; a business rule says what must always be true.

## Edge Cases
List the boundary and failure conditions the functional requirements must handle: missing or unknown data, expired windows, absent permissions, unavailable dependencies, and entities that no longer exist. When `ARCHITECTURE.md` is present, derive a dependency-failure edge case for each boundary it reveals (the dependency is slow, unavailable, or returns nothing). Each edge case should trace to a functional requirement or business rule that covers it.

## Output
Follow the template and writing style in [references/output-format.md](references/output-format.md). For worked examples, see [references/examples.md](references/examples.md).

## Quality Check (before output)
- Each capability is atomic; unrelated capabilities are split into separate requirement sets.
- The **capability title** is solution-agnostic — it names a behavior and entity, not a page, screen, header, panel, tab, dropdown, grid, badge, endpoint, or route.
- Every requirement is **solution-agnostic** — swapping UI or technology would not force a reword.
- Entities and behaviors use `CONTEXT.md`'s approved terms wherever they exist.
- Every functional requirement is specific, testable, and externally visible.
- Business rules state invariants, not capabilities.
- Every edge case traces to a functional requirement or business rule.

## Next Step
The output of this skill is the input to /to-story: hand the functional requirements (with their business rules and edge cases) to /to-story to package each capability into a backlog-ready user story with acceptance criteria.
