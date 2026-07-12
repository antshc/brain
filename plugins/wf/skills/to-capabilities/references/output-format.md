# Output Format

## Writing Style
- Write for Product Owners and analysts — plain business language, no code, class names, or technical jargon. 
- **Solution-agnostic**: every sentence names a behavior and entity, never a widget, table, endpoint, or access role.

## Template
{Emit one block per capability.}

```markdown
## <Capability title — behavior + entity, no surface or placement>

> **Priority**: <Importance of the requirement: MVP/Should have/Nice to have. If not applicable, use MVP as default> | **Risk**: <Complexity: Low/Medium/High. If not applicable, use Low as default>

### Stakeholder Requirement
The <actor> needs to <behavior> <entity>, so <value>.

### Functional Requirements
- <Behavior> when <condition>.
- ...

### Business Rules
{Optional section — if no business rules exist, omit this section.}

- If <condition>, <invariant>.
- ...

### Edge Cases
{Optional section — if no edge cases exist, omit this section.}

- <boundary/failure condition> → <expected handling>.
- ...
```

## Example

## Example — reinstate cancelled orders

**Input idea:** *Let store administrators reinstate orders that were cancelled by mistake.*

```
## Reinstate cancelled orders

### Stakeholder Requirement
Store administrators need to reinstate mistakenly cancelled orders without contacting support, so customers keep their purchases and support load drops.

### Functional Requirements
- Retain cancelled orders for 30 days before permanent removal.
- Let a store administrator review the orders available for reinstatement.
- Reinstate a selected order to its original status.
- Require the store administrator to confirm current pricing when the original prices are no longer valid.
- Prevent users without reinstate permission from reinstating orders.
- Record an audit event when an order is reinstated.

### Business Rules
- A cancelled order may only be reinstated within 30 days of cancellation.
- Only users with the reinstate permission may reinstate an order.
- An order whose items are no longer sold must not be offered for reinstatement.

### Edge Cases
- Retention window expired → the order is not offered for reinstatement and the reason is explained.
- Original pricing no longer valid → the store administrator must confirm current pricing before reinstatement proceeds.
- Reinstatement requested without permission → the action is denied.
```
