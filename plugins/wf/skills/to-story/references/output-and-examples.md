# Output Format, Examples & Anti-Patterns

Write for Product Owners and QA — plain business language, no code, class names, or technical jargon. Each criterion is one clear, testable statement of expected behavior.

## Output Format

One story:
```
<Short requirement title>

<One-line business value: what capability this delivers and why it matters.>

## Acceptance Criteria
- The system <does observable outcome> when <condition>.
- If <failure condition>, the system <what the user/operator sees>.
```

Multiple stories — repeat the block, one per capability, under a numbered heading:
```
## Story 1 
<Short requirement title>
<One-line business value: what capability this delivers and why it matters.>
### Acceptance Criteria
- ...

```

## Example — reserve stock
```
Reserve stock for cart items

Stock for items in a shopper's cart is held while they complete checkout so that purchased items remain available and cannot be oversold.

## Acceptance Criteria
- Stock for each cart item is reserved when the shopper begins checkout.
- Checkout is blocked and the affected items are identified when requested quantity exceeds available stock.
- If a reservation cannot be placed, checkout fails and the shopper's cart remains unchanged.
- Reserved stock is released and returned to availability when checkout is abandoned or the reservation expires.
```

## Example — lifting a solution-leaking requirement
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
- "Display a badge", "Add a button/banner/dropdown", "Show a table" — these name UI artifacts, not behavior. Apply the solution-agnostic rule and describe what the system does and why.
