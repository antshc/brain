# Output Format, Examples & Anti-Patterns

Write for Product Owners and QA — plain business language, no code, class names, or technical jargon. Each criterion is one clear, testable statement of expected behavior.

## Output Format

Each story is broken down by capability and carries four blocks in order: **Capability**, **Stakeholder Requirement**, **Functional Requirements**, then **Acceptance Criteria**. When the /to-requirements output is in context, copy the first three blocks verbatim; otherwise derive them from the requirement text.

One story:
```
## <Capability title>

<capability title — behavior + entity, no surface or placement>

The <actor> needs to <behavior> <entity>, so <value>.

### Acceptance Criteria
Each criterion states one observable outcome bound to a condition (`<outcome> when/if <condition>`). Vary the opening to fit the behavior — do not force "The system" every time:
- <entity/outcome> <is/becomes/does> ... when <condition>.
- The <actor> <sees/receives/is prompted> ... when <condition>.
- The system <does observable outcome> when <condition>.
- If <failure condition>, <what the user/operator sees>.

**Functional Requirements:**
- <Behavior> when <condition>.
- ...


```

Multiple stories — repeat the block, one per capability, under a numbered heading:
```
## Story 1 — <Capability title>

<capability title — behavior + entity, no surface or placement>

The <actor> needs to <behavior> <entity>, so <value>.

### Acceptance Criteria
- ...

**Functional Requirements:**
- ...
```

## Example — reserve stock
```
## Reserve stock for cart items

Reserve stock for cart items

Shoppers need stock for items in their cart held while they complete checkout, so purchased items remain available and cannot be oversold.

### Acceptance Criteria
- Stock for each cart item is reserved when the shopper begins checkout.
- Checkout is blocked and the affected items are identified when requested quantity exceeds available stock.
- If a reservation cannot be placed, checkout fails and the shopper's cart remains unchanged.
- Reserved stock is released and returned to availability when checkout is abandoned or the reservation expires.

**Functional Requirements:**
- Reserve stock for each cart item when the shopper begins checkout.
- Block checkout and identify the affected items when requested quantity exceeds available stock.
- Leave the cart unchanged when a reservation cannot be placed.
- Release reserved stock when checkout is abandoned or the reservation expires.
```

## Example — lifting a solution-leaking requirement
Shows a solution-leaking request raised to behavior. The input names a widget (*badge*) and a placement (*page header*); the output names the behavior, entity, scope, and value.

**Input (rejected):** *Display a cart badge in the page header to show the number of items.*

**Rewritten:**
```
## Keep shoppers aware of their cart contents while they browse

Keep shoppers aware of their cart contents while they browse

Shoppers need to stay aware of the items in their cart during normal browsing, so they can proceed to purchase without navigating away to check.

### Acceptance Criteria
- A cart-contents signal is shown whenever at least one item is in the shopper's cart.
- The cart-contents signal clears when the cart is empty.
- The count of cart items stays current for the shopper as items are added or removed, without a manual refresh.
- The shopper can reach the full cart contents in a single step from the notification.
- If cart information cannot be retrieved, the shopper is not shown an incorrect cart state and the rest of their shopping remains usable.

**Functional Requirements:**
- Signal that the cart contains items whenever at least one item is in the shopper's cart.
- Keep the count of cart items current as items are added or removed.
- Let the shopper reach the full cart contents in a single step from the notification.
- Avoid showing an incorrect cart state when cart information cannot be retrieved.
```

## Anti-Patterns (reject)
- "Add support for X", "Improve performance", "Refactor component", "Create service Y" — these are tasks, not behavior rules.
- "Display a badge", "Add a button/banner/dropdown", "Show a table" — these name UI artifacts, not behavior. Apply the solution-agnostic rule and describe what the system does and why.
