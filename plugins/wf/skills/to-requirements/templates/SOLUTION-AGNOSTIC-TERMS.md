# Solution-Agnostic De-referencing Tables

> **Template.** Copy this file to the repo root as `SOLUTION-AGNOSTIC-TERMS.md`, then replace the guidance below with entries drawn from your own codebase. The /to-requirements skill applies this file only when it exists at the repo root.

Project-owned catalog of leaked implementation artifacts and the behavior to state instead. Each row maps a concrete artifact your team names in conversation (a column, an endpoint, an access role) to the outcome the actor actually gets, so requirements stay solution-agnostic.

Add a short reject/prefer pair here to anchor the intent:
- Reject: *<a statement that names a widget/table/endpoint + placement>.*
- Prefer: *<the same intent stated as behavior + entity + scope + value>.*

## De-referencing tables
Group the artifacts your codebase actually uses into the categories below (drop categories you don't have, add ones you do). For every artifact, write the behavior it enables in plain language — "let the user …", "keep … so …", "tell the client …". Fill the `…` with the domain entity.

### UI / presentation
Screens, components, and placements (badge, banner, dropdown, grid, header). State what the user sees or does, not the control.

| Leaked artifact | Behavior to state instead |
| --- | --- |
| <component or placement> | <what the user perceives or can do> |

### Persistence / data
Storage shapes (column, row, blob, TTL, table/repository, null). State what is remembered and for how long.

| Leaked artifact | Behavior to state instead |
| --- | --- |
| <storage shape> | <what is kept, and the guarantee> |

### API / protocol
Transport surface (endpoint, HTTP verb, payload, response field, query param, status code, id). State what the client asks for or learns.

| Leaked artifact | Behavior to state instead |
| --- | --- |
| <transport element> | <what the client can do or is told> |

### Domain-state / enum
Status values, flags, and derived states. State which phase the actor sees or what now needs action.

| Leaked artifact | Behavior to state instead |
| --- | --- |
| <status / flag / derived state> | <what the user understands from it> |

### Process / infrastructure
Background work and plumbing (worker, queue, retry, lock, cache, cron, metering, license). State what gets done for the user, reliably.

| Leaked artifact | Behavior to state instead |
| --- | --- |
| <process or infra element> | <the outcome delivered without the user waiting> |

### Access / identity
Permissions and cross-account trust (access role, grant, role status, delegated access, account list). State what access the owner grants or the user controls.

| Leaked artifact | Behavior to state instead |
| --- | --- |
| <access / identity element> | <what the owner grants or the user controls> |

## Criteria obey solution-agnostic too
A criterion states an observable outcome, not the control that produces it. Write what the user perceives or can do, not what they tap. Add a reject/prefer pair that reflects your domain:
- Reject: *<criterion that names a widget + interaction>.*
- Prefer: *<the same outcome stated as what the user can reach or perceive>.*

## Verb → Component Hints
Map the behavior verbs your team uses to the component types they imply, so design can pick up where the requirement stops. Example shape:

`persist → repository/accessor · validate → validator · create → provisioner · external API → client/gateway · emit alert → alert service · process async → worker · expose API → controller`
