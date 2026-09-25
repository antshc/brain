# Business Hierarchy

A useful hierarchy from business intent to execution:

```text
Business Goal / Strategy
  ↓
Business Capability
  ↓
Value Stream / Business Process
  ↓
Business Scenario
  ↓
Use Case
  ↓
Activity / Task
  ↓
Process Step
```

| Level | Meaning | Example |
|---|---|---|
| **Business Goal / Strategy** | What the organization wants to achieve | Increase customer retention |
| **Business Capability** | What the organization must be able to do | Customer Relationship Management |
| **Value Stream / Business Process** | How the capability delivers value | Handle Customer Complaints |
| **Business Scenario** | A particular situation in which the process occurs | Customer reports a damaged product |
| **Use Case** | A specific interaction needed to handle the scenario | Register a complaint |
| **Activity / Task** | Work performed by a person or system | Verify order details |
| **Process Step** | The smallest operational action | Enter order number and search |

## Example

```text
Capability: Order Management
  ↓
Business Process: Process Customer Order
  ↓
Scenario: Customer changes an order before shipment
  ↓
Use Case: Modify existing order
  ↓
Activity: Validate requested change
  ↓
Task / Step: Check inventory availability
```

## Key distinction

- **Capability** — what the business can do.
- **Process** — how the business performs it.
- **Scenario** — a particular situation or variation of the process.
- **Use case** — a specific interaction required to handle the scenario.
- **Activity / task / step** — progressively finer-grained execution details.

A fuller hierarchy sometimes used in enterprise architecture and business analysis is:

```text
Strategy
  ↓
Capability
  ↓
Value Stream
  ↓
Business Process
  ↓
Scenario
  ↓
Use Case
  ↓
Activity
  ↓
Task
  ↓
Step
```
