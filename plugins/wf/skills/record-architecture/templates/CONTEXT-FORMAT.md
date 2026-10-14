# CONTEXT.md Format

## Structure

```md
# {{contextName}}

<!-- Location: optional, only if multiple contexts in the CONTEXT.md file. Path to the module directory covered by the context, relative to the repo root. -->
Location: {{modulePath}}

{{contextDescription}} <!-- one or two sentence description of what this context is and why it exists -->

## Language

**{{term}}**:
{{termDescription}} <!-- one or two sentence description of the term -->
_Avoid_: {{synonymsToAvoid}}

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account

# Relationships
<!-- exists only if multiple contexts in the CONTEXT.md -->
- **{{producerContext}} → {{consumerContext}}**: {{producerContext}} emits `{{eventName}}` events; {{consumerContext}} consumes them to start picking/processing/etc.
- **Ordering → Fulfillment**: Ordering emits `OrderPlaced` events; Fulfillment consumes them to start picking
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched` events; Billing consumes them to generate invoices
- **Ordering ↔ Billing**: Shared types for `CustomerId` and `Money`
```

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list the others under `_Avoid_`.
- **Keep definitions tight.** One or two sentences max. Define what it IS, not what it does.
- **Only include terms specific to this project's context.** General programming concepts (timeouts, error types, utility patterns) don't belong even if the project uses them extensively. Before adding a term, ask: is this a concept unique to this context, or a general programming concept? Only the former belongs.
- **Group under context.** Every term sits under a context heading — one heading for a single-context project, one per context otherwise, named after the project modules. When the current topic's context is unclear, ask. Add subheadings when natural clusters emerge; a flat list is fine when the terms form one cohesive area.
- **Relationships.** With multiple contexts, define how they relate to each other.
