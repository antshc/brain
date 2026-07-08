# Types of Requirements

Teams mix requirement types and cause confusion. Quick map:

| Question | Type |
| --- | --- |
| Why are we building this? | Business requirement |
| What distinct behavior are we scoping? | Capability |
| What must the system do? | Functional requirement |
| How well must it work? | Non-functional requirement |
| What must always be true? | Business rule |
| What does the user want to achieve? | Stakeholder requirement / user story |
| What steps happen in the interaction? | Use case |
| How do we know it is done? | Acceptance criteria |

## Capability
A bounded unit of behavior that scopes one requirement set. A capability names what the system *does* and the outcome the actor gets — never a screen, widget, or implementation artifact. One distinct capability yields exactly one requirement set (stakeholder requirement + functional requirements + business rules + edge cases); an idea spanning several unrelated behaviors yields one set per capability, never merged.

A **capability title** names the behavior and entity:
- Reject: *Surface active alerts in the page header* · *Manage tasks on the Monitoring page*
- Prefer: *Present the count of active alerts* · *Manage tasks*

Capability is a **scoping unit**, not a requirement type. It exists to prevent requirement sprawl — each set stays focused on one behavior rather than bundling several unrelated behaviors under one title.

## Business Requirements
Why the feature exists — the business need, value, or goal. Understandable by business stakeholders; no implementation detail.
- Good: *The system must let enterprise customers recover accidentally deleted files within 30 days to reduce support tickets.*
- Bad (already a solution): *Add a "Restore" button on the Files page.*

## Stakeholder / User Requirements
What a user, admin, or other stakeholder needs to achieve — more user-oriented than a business goal. Connects business need to product behavior.
- *Administrators need to restore deleted files without contacting support.*
- *Customers need to see accurate delivery costs before confirming an order.*

## Functional Requirements
What the system must do — concrete, testable, externally visible behavior. Avoid implementation detail.
- *The system must retain deleted files for 30 days before permanent deletion.*
- *The system must allow administrators to restore a deleted file to its original location.*
- *The system must prevent standard users from restoring files unless authorized.*
- *The system must record an audit event when a file is restored.*
- Bad (design decision): *The backend should use a soft-delete flag.*

## Non-Functional Requirements
How well the system must behave — quality attributes and constraints.
- Performance: *Display deleted files within 2 seconds for up to 10,000 items.*
- Security: *Only users with the FileAdmin role may restore deleted files.*
- Reliability: *Deleted file metadata must remain recoverable for 30 days after service restart.*
- Auditability: *Every restore action must be logged with user ID, timestamp, and file ID.*
- Availability: *Restore must be available 99.9% of the time.*

Commonly forgotten: permissions, performance, logging, retries, failure handling, audit, scalability, consistency.

## Business Rules
Logic or policy that must **always** hold. A requirement says a capability must exist; a rule says what must always be true. Rules drive validation, calculations, eligibility, permissions, and workflow decisions.
- *A deleted file may only be restored within 30 days of deletion.*
- *A user may only have one active domestic billing profile.*
- *An item with unknown availability must display "Availability Unknown".*

## User Stories
A lightweight planning slice from the user's point of view. Useful for backlog, but not a complete requirement on its own — still needs functional requirements, rules, acceptance criteria, edge cases, and NFRs.

Format: `As a [user], I want [capability], So that [benefit].`
- Good: *As a customer, I want a notification when my order ships, so I know it is on the way.*
- Weak (too vague): *As a user, I want notifications so I stay informed.*

## Use Cases
How a user interacts with the system to reach a goal — more detailed and flow-oriented than a story. Answers: what steps, what alternate paths, what can go wrong, what is the result. Best for multi-step workflows, complex permissions, branching, and error handling.

```
Use Case: Restore Deleted File
Primary Actor: Administrator
Main Flow:
1. Admin opens the Deleted Files page.
2. System shows recoverable files.
3. Admin selects a file and restores it.
4. System restores it to its original location and confirms.
Alternate Flows:
- Retention expired → restore prevented, explanation shown.
- No permission → restore denied.
- Original folder missing → prompt for a new location.
Postconditions: file is active; restore recorded in audit logs.
```

## Acceptance Criteria
What must be true for a story, feature, or requirement to be done. Makes requirements testable — specific, observable, unambiguous.
- *The system must display files deleted within the last 30 days.*
- *The system must restore a file to its original location if it still exists.*
- *If the original location no longer exists, the system must require choosing a new location.*
- *The system must deny restore for users without permission.*
- Bad (untestable): *Should work fast. Should be secure. Should be user-friendly.*

## Constraints
Limits the solution must respect — often not user-visible but strongly shaping design.
- *Must run in Azure.* / *API must stay backward compatible.* / *Must use the company auth provider.* / *No downtime during deployment.* / *Must run on .NET 8.*

## Assumptions
Statements currently believed true; not requirements, but they affect planning. Make them explicit — a wrong assumption can force a redesign.
- *We assume deleted file metadata is already stored.* / *We assume restore is admin-only.*

## Levels
- **Why:** business requirement, goal, KPI.
- **What:** functional, non-functional, business rules, constraints.
- **User & flow:** stakeholder requirements, user stories, use cases.
- **Validation:** acceptance criteria, test cases.

## Full Example — real-time availability in the catalog

**Capability:** *Present item availability in the catalog*

**Business requirement:** *The business must display current availability to reduce frustration from ordering unavailable products.*

**Stakeholder requirement:** *Customers need to know whether an item is available before adding it to the cart.*

**Functional requirements:**
- Retrieve availability from the source system for each item shown.
- Display availability for every item on the catalog page.
- Keep rendering the catalog even if availability retrieval partially fails.

**Business rules:**
- Available → show "In Stock". Unavailable → "Out of Stock". Missing/unknown → "Availability Unknown".
- An item absent from the source system must not show availability.

**Non-functional requirements:**
- Availability retrieval must not block rendering longer than 2 seconds.
- The catalog must survive a source-system failure without crashing.

**User story:** *As a customer browsing the catalog, I want real-time availability, so I can make informed purchase decisions.*

**Acceptance criteria:**
- Display availability for each item on page load.
- Available → "In Stock"; unavailable → "Out of Stock"; unknown → "Availability Unknown".
- The page must still render if the source system is slow or unavailable.

## Quick Comparison

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

## Common Mistakes
- **Only user stories** — *As a user, I want to manage files so I can be productive.* Too vague to build.
- **Mixing requirement and design** — *We need Redis because customers want performance.* Split: requirement = *response under 500 ms*; design = *use Redis*.
- **Vague acceptance criteria** — *Should be secure/fast/easy.* Replace with measurable outcomes (*results within 1 second for up to 5,000 items*).

## Recommended Structure
1. Business context → 2. User need → 3. Functional requirements → 4. Business rules → 5. Non-functional requirements → 6. User story → 7. Acceptance criteria → 8. Use case (if the workflow is complex).

The strongest requirement set combines several of these, not just one format.
