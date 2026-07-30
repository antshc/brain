# Types of Requirements

## Capability
a single, focused area of system behavior, defined by verifiable requirements and scenarios. It is behavior the system provides *independently of where it appears* and *survives after the current change completes* — never a one-off task. It names what the system *does* and the outcome the actor gets. Each capability scopes exactly one requirement set (stakeholder requirement + functional requirements + business rules + edge cases); an idea spanning several unrelated behaviors yields one set per capability, never merged.

A **capability title** names the behavior and entity:
- Reject: *Surface active notifications in the page header* · *Manage orders on the Fulfillment page*
- Prefer: *Present the count of active notifications* · *Manage orders*

Capability is a **scoping unit**, not a requirement type. It exists to prevent requirement sprawl — each set stays focused on one behavior rather than bundling several unrelated behaviors under one title.

## Stakeholder/User requirement
one sentence: `The {{actor}} needs to {{behavior}} {{entity}} for {{scope}}, so {{value}}.` Names a behavior, never an artifact.

## Functional requirements
Imperative `{{behavior}} when {{condition}}.` statements — specific, testable, externally visible. Cover, at minimum: **Capability** (actions and outcomes), **Integration** (external interactions), **State** (persistence and state changes), **Permissions** (who may and may not act), **Degraded behavior** (what still works when a dependency is slow or fails). When `ARCHITECTURE.md` is present, use its module layout to surface Integration and Degraded-behavior requirements at each boundary.

## Business rules
Invariants that must always hold: `If {{condition}}, {{invariant}}.` A functional requirement says a capability must exist; a business rule says what must always be true.

## Edge cases
Boundary and failure conditions: missing or unknown data, expired windows, absent permissions, unavailable dependencies, entities that no longer exist. Each edge case traces to a functional requirement or business rule.

# Quick Comparison

| Type | Best for | Audience |
| --- | --- | --- |
| Business requirement | Why the feature exists | Business, product |
| Capability | Scoping one bounded behavior | Product, analysts |
| Stakeholder requirement | What a user needs | Product, analysts, UX |
| Functional requirement | Exact system behavior | Devs, testers, analysts |
| Non-functional requirement | Quality attributes | Devs, testers, architects |
| Business rule | Logic and constraints | Analysts, devs, testers |
| User story | Backlog planning | Product, devs |
| Use case | Workflows and alternate paths | Analysts, devs, testers |
| Acceptance criteria | Done conditions | Devs, testers, POs |
| Constraint | Solution boundaries | Architects, devs |
| Assumption | Planning risks | Whole team |

# Levels
- **Why:** business requirement, goal, KPI.
- **What:** functional, non-functional, business rules, constraints.
- **User & flow:** stakeholder requirements, user stories, use cases.
- **Validation:** acceptance criteria, test cases.

# Common Mistakes
- **Only user stories** — *As a user, I want to manage files so I can be productive.* Too vague to build.
- **Mixing requirement and design** — *We need Redis because customers want performance.* Split: requirement = *response under 500 ms*; design = *use Redis*.
- **Vague acceptance criteria** — *Should be secure/fast/easy.* Replace with measurable outcomes (*results within 1 second for up to 5,000 items*).

# Full Example — real-time availability in the catalog

**Capability:** *Present item availability in the catalog*

**Stakeholder/User requirement:** *Customers need to know whether an item is available before adding it to the cart.*

**Functional requirements:**
- Retrieve availability from the source system for each item shown.
- Display availability for every item on the catalog page.
- Keep rendering the catalog even if availability retrieval partially fails.

**Business rules:**
- Available → show "In Stock". Unavailable → "Out of Stock". Missing/unknown → "Availability Unknown".
- An item absent from the source system must not show availability.
