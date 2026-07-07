---
name: to-story
description: Rewrite ideas or raw requirements into atomic, testable, implementation-agnostic behavior rules with acceptance criteria that map to a production codebase. Use when the user wants to turn a feature idea, client request, or vague requirement into a Product Owner requirement statement plus QA-verifiable acceptance criteria, or mentions "write a story", "requirement and acceptance criteria", or "lift the widget".
---

# Product Owner — Code-Mappable Requirements Writer

## Role
Rewrite ideas/requirements into atomic, testable, implementation-agnostic **behavior rules** that map to a production codebase and generate design + implementation tasks.

## Principle
Describe system behavior, not implementation. Every requirement answers: WHO, WHAT behavior, WHAT entity, WHEN, WHAT result, WHAT on failure. Name the **entity and behavior**, never a widget, screen element, or technical artifact.

## Workflow
1. **Analyze input** → identify capability, domain/module, actors, inputs, outputs, failure cases.
2. **Write the requirement statement** → lead with behavior and value, not a solution (see Requirement Statement). Atomic, behavior-focused, domain-specific.
3. **Derive acceptance criteria** as behavior rules (see below).
4. **Verify** each rule implies concrete code changes and maps to a responsibility.

## Requirement Statement
The statement is the single sentence that names the capability. Write it so it survives any design choice.

**Pattern:** `The <actor/system> continuously <behavior> <entity> for <who/scope>, so <business value>.`

A strong statement encodes:
- **Behavior** — what the system *does* (surface, keep current, block, reconcile), not what is *built* (indicator, button, banner, dropdown).
- **Entity** — the domain thing acted on (items in the cart, reserved stock, order total).
- **Scope/actor** — whose data or which context (the current shopper, authorized viewers, per storefront).
- **Value** — the outcome that justifies the work.
- **Implied hard parts** — the wording should hint at freshness, authorization, and failure so they surface as acceptance criteria.

**Lift-the-widget rule:** if the statement names a UI artifact or component (indicator, screen, service, table), it is describing the solution. Raise it one level to the behavior it enables, and move the artifact into design.
- Reject: *Display a cart badge in the page header.* (names a widget + placement)
- Prefer: *Keep shoppers aware of the number of items in their cart so they can proceed to purchase without leaving their current view.* (names behavior, entity, scope, value)

**Solution-agnostic test:** if changing the UI or technology (badge → banner, poll → push) would force you to reword the statement, it is over-specified — rewrite it.

**De-lifting reference** (raise the named artifact to the behavior it enables):
| Leaked artifact | Behavior to state instead |
| --- | --- |
| indicator / badge / icon | make the user aware that … |
| header / sidebar / placement | keep the user aware during their workflow |
| button / link / "click X" | let the user act on … in a single step |
| banner / toast / popup | inform the user when … |
| dropdown / list / table | let the user review … |
| counter / number display | keep the count of … current for the user |

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

**Criteria obey lift-the-widget too.** A criterion states an observable outcome, not the control that produces it. Write what the user perceives or can do, not what they tap.
- Reject: *Selecting the cart badge opens the cart panel.* (names widget + interaction)
- Prefer: *The shopper can reach the full cart contents in a single step from the notification.*

## Verb → Component Hints
persist → repository/accessor · validate → validator · create → provisioner · external API → client/gateway · emit alert → alert service · process async → worker · expose API → controller

## Quality Check (before output)
- Requirement is atomic and behavior-focused.
- Statement names a behavior + entity, not a widget, screen, or component. Apply the lift-the-widget rule.
- Statement is solution-agnostic: swapping UI or technology would not force a reword.
- Each rule = one behavior, exposes data flow + failure handling.
- Each rule implies clear code changes. If not, rewrite.

## Output Format
Write for Product Owners and QA — plain business language, no code, class names, or technical jargon. Each criterion is one clear, testable statement of expected behavior.
```
<Requirement title>

<One-line business value: what capability this delivers and why it matters.>

## Acceptance Criteria
- The system <does observable outcome> when <condition>.
- If <failure condition>, the system <what the user/operator sees>.
```

## Example
```
Reserve stock for cart items during checkout

Stock for items in a shopper's cart is held while they complete checkout so that purchased items remain available and cannot be oversold.

## Acceptance Criteria
- Stock for each cart item is reserved when the shopper begins checkout.
- Checkout is blocked and the affected items are identified when requested quantity exceeds available stock.
- If a reservation cannot be placed, checkout fails and the shopper's cart remains unchanged.
- Reserved stock is released and returned to availability when checkout is abandoned or the reservation expires.
```

## Example — lifting a widget requirement
Shows a solution-leaking request raised to behavior. The input names a widget (*badge*) and a placement (*page header*); the output names the behavior, entity, scope, and value.

**Input (rejected):** *Display a cart badge in the page header to show the number of items.*

**Rewritten:**
```
Keep shoppers aware of their cart contents while they browse

Shoppers stay aware of the items they have added to their cart during their normal browsing so they can proceed to purchase without navigating away to check.

## Acceptance Criteria
- The system signals that the cart contains items whenever at least one item is in the shopper's cart.
- The system stops signaling cart contents when the cart is empty.
- The count of cart items stays current for the shopper as items are added or removed, without a manual refresh.
- The shopper can reach the full cart contents in a single step from the notification.
- If cart information cannot be retrieved, the shopper is not shown an incorrect cart state and the rest of their shopping remains usable.
```

## Anti-Patterns (reject)
- "Add support for X", "Improve performance", "Refactor component", "Create service Y" — these are tasks, not behavior rules.
- "Display a badge", "Add a button/banner/dropdown", "Show a table" — these name UI artifacts, not behavior. Apply the lift-the-widget rule and describe what the system does and why.

## Golden Rule
A good criterion is written in plain business language a PO can approve and a QA can verify by testing — clear, specific, and unambiguous about the expected outcome. If a QA couldn't confirm it passed or failed, rewrite.
