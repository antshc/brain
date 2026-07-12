# Solution-Agnostic De-referencing Tables

Catalog of leaked implementation artifacts and the behavior to state instead. Each row maps a concrete artifact teams name in conversation (a column, an endpoint, an access role) to the outcome the actor actually gets, so requirements stay solution-agnostic. Apply these tables directly when scrubbing text — match a leaked term to its category, then restate the line as the behavior in the right-hand column.

Anchor the intent with a reject/prefer pair:
- Reject: *Show the alert count in the page header badge.*
- Prefer: *Surface the count of active alerts, so the operator sees load at a glance.*

## De-referencing tables

For every artifact, state the behavior it enables in plain language — "let the user …", "keep … so …", "tell the client …". Replace the `…` with the domain entity when applying a row.

### UI / presentation
Screens, components, and placements (badge, banner, dropdown, grid, header, panel, tab). State what the user sees or does, not the control.

| Leaked artifact | Behavior to state instead |
| --- | --- |
| badge / banner in the header | let the user see the current count or status at a glance |
| dropdown / picker | let the user choose from the allowed options |
| grid / table / list view | let the user review the set of items |
| modal / dialog | prompt the user to confirm or supply the missing input |
| tab / page / screen | give the user access to the behavior (name the behavior, not the placement) |

### Persistence / data
Storage shapes (column, row, blob, TTL, table/repository, null). State what is remembered and for how long.

| Leaked artifact | Behavior to state instead |
| --- | --- |
| column / field / flag | remember whether the entity is in a given state |
| TTL / retention window | keep the entity recoverable for the retention period, then release it |
| soft-delete flag | keep a deleted entity recoverable until its window expires |
| null / missing value | treat the value as unknown and state the fallback behavior |

### API / protocol
Transport surface (endpoint, HTTP verb, payload, response field, query param, status code, id). State what the client asks for or learns.

| Leaked artifact | Behavior to state instead |
| --- | --- |
| endpoint / route | let the client request the behavior or retrieve the entity |
| response field | tell the client the outcome or current state |
| status code (4xx/5xx) | tell the client the request was rejected and why |
| query param / filter | let the client narrow the results by a stated criterion |

### Domain-state / enum
Status values, flags, and derived states. State which phase the actor sees or what now needs action.

| Leaked artifact | Behavior to state instead |
| --- | --- |
| status enum value | tell the user which phase / state the entity is in |
| derived / computed flag | tell the user what now needs their action |
| boolean toggle | let the user see whether the behavior is on or off |

### Process / infrastructure
Background work and plumbing (worker, queue, retry, lock, cache, cron, metering, license). State what gets done for the user, reliably.

| Leaked artifact | Behavior to state instead |
| --- | --- |
| worker / job / cron | get the work done for the user without them waiting |
| queue / retry | complete the work reliably even when a step first fails |
| cache | serve the result quickly and keep it current |
| lock | keep concurrent changes from corrupting the entity |

### Access / identity
Permissions and cross-account trust (access role, grant, role status, delegated access, account list). State what access the owner grants or the user controls.

| Leaked artifact | Behavior to state instead |
| --- | --- |
| access role / permission | let only authorized actors perform the behavior |
| grant / delegated access | let the owner give another party controlled access |
| account / tenant scope | keep each owner's data separate from every other owner's |

## Criteria obey solution-agnostic too

A criterion states an observable outcome, not the control that produces it. Write what the user perceives or can do, not what they tap.
- Reject: *The user clicks the "Restore" button in the Deleted Files grid.*
- Prefer: *The user can restore a deleted item within its retention window.*

## Verb → component hints

Map behavior verbs to the component types they imply, so design can pick up where the requirement stops:

`persist → repository/accessor · validate → validator · create → provisioner · external API → client/gateway · emit alert → alert service · process async → worker · expose API → controller`
