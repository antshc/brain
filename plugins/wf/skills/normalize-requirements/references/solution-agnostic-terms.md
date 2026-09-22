# Solution-Agnostic De-referencing Tables

Catalog of leaked implementation artifacts and the behavior to state instead. 

Anchor the intent with a reject/prefer pair:
- Reject: *Display a cart badge in the page header.* (names a widget + placement)
- Prefer: *Keep shoppers aware of the number of items in their cart so they can proceed to purchase without leaving their current view.* (names behavior, entity, scope, value)

## De-referencing tables
Raise each named artifact to the behavior it enables.

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
| Leaked artifact | Behavior to state instead |
| --- | --- |
| column / field | keep … recorded so a later read returns the same value |
| record / row / document | remember one … so it survives restarts and crashes |
| serialized blob / metadata blob | keep … attached to the operation it describes |
| TTL / `ExpiresAt` / expiry column | let finished … drop out automatically once they no longer matter |
| table / DynamoDB / repository | store every … durably so the user never loses it |
| null / missing value | treat an absent … as "the user gave no value" |

### API / protocol
Transport surface (endpoint, HTTP verb, payload, response field, query param, status code, id). State what the client asks for or learns.

| Leaked artifact | Behavior to state instead |
| --- | --- |
| endpoint / route / URL | let the client ask the system to … |
| GET / POST / PUT / DELETE | let the client read / start / change / remove a … |
| request body / payload | let the client hand the system the … it needs to do the work |
| response field / JSON key | tell the client the resulting … |
| query parameter / filter | let the client narrow the results down to … |
| status code / HTTP error | tell the client whether … worked, or why it failed |
| identifier in response | give the client a handle to come back to the same … later |

### Domain-state / enum
Status values, flags, and derived states. State which phase the actor sees or what now needs action.

| Leaked artifact | Behavior to state instead |
| --- | --- |
| status / state enum value | let the user see which phase a … has reached |
| boolean flag (e.g. `isDismissed`) | let the user tell an active … from one already handled |
| derived / computed state | surface to the user that a … now needs their action |
| level / severity value | let the user judge how urgent a … is |
| completion / outcome value | tell the user how a … ended — success or failure |

### Process / infrastructure
| Leaked artifact | Behavior to state instead |
| --- | --- |
| background service / worker | get … done for the user without them waiting |
| queue / job / task record | run each … reliably and in the right order |
| retry / backoff | keep trying … until it succeeds |
| lock / mutex | stop two … from clashing when they run at once |
| cache | give the user … back fast |
| scheduled run / cron | do … for the user at the right time, unprompted |
| usage report / CallHome / metering | account for each customer's usage of … so they can be billed |
| license / entitlement type | let the user unlock the … they have paid for |

### Access / identity
Permissions and cross-account trust (access role, grant, role status, delegated access, account list). State what access the owner grants or the user controls.

| Leaked artifact | Behavior to state instead |
| --- | --- |
| access role / permission | let only authorized actors perform the behavior |
| grant / delegated access | let the owner give another party controlled access |
| account / tenant scope | keep each owner's data separate from every other owner's |

## Criteria obey solution-agnostic too

A criterion states an observable outcome, not the control that produces it. Write what the user perceives or can do, not what they tap.
- Reject: *Selecting the cart badge opens the cart panel.* (names widget + interaction)
- Prefer: *The shopper can reach the full cart contents in a single step from the notification.*

## Verb → component hints

Map behavior verbs to the component types they imply, so design can pick up where the requirement stops:

`persist → repository/accessor · validate → validator · create → provisioner · external API → client/gateway · emit alert → alert service · process async → worker · expose API → controller`

