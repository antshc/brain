# Examples & Anti-Patterns

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
