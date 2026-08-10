# GUI delta — template

Fill this template to document the GUI **delta** a feature introduces. Copy only the parts you need, replace every `<placeholder>`, and delete the rest.

- The section is organised by **surface** — either a **page** (its entry documents changes to the GUI components on that page) or a **GUI component** itself (a utility component, or a Layout component used across pages such as, header, menu, or badge). Add one `<details>` entry per surface the feature adds or changes.
- Every surface, sub-component (toolbar, panel, modal, grid), and grid records its changes as **Behaviour changes** bullets, each starting with an **Added**, **Modified**, or **Removed** marker (use **Obsolete** for a field the backend still returns but the GUI must stop using).
- Fold data loading into a Behaviour-changes bullet: name the exact API call the surface fires (`GET /api/v2/…`) and the polling cadence when it polls, so the GUI ties back to the ZIC API section.
- Grid columns list **only changed** columns, each with a `Change` column; field-rendering rules shared across a grid's columns live in that grid's inline **Grid column formatting** block.
- Cross-cutting GUI rules live under `## Conventions`.

---
## <Pages or Gui component>

### <Gui component name, if under the page>

<details>
<summary><Surface — page, gui component> — `<Added | Modified | Removed>`</summary>

<One-line summary of the surface.> _(For a page, give its route, e.g. `/monitoring`.)_

**Behaviour changes**

- <Added | Modified | Removed> <route / default state / interaction / validation / ordering / side effect>.
- <Added | Modified | Removed> Data loading Fires `<VERB> <path>?<params>` <every `<n>` seconds when polling | on open | on action>. <Tweakable client-side? stop-when-inactive?>

**Toolbar / header component / panel / modal/ Grid** _(omit when the surface has none)_

**Behaviour changes**

- <Added | Modified | Removed> <route / default state / interaction / validation / ordering / side effect>.
- <Added | Modified | Removed> Data loading Fires `<VERB> <path>?<params>` <every `<n>` seconds when polling | on open | on action>. <Tweakable client-side? stop-when-inactive?>

<grid-changes-template>
{ omit when the surface has no table, it is template for grid}

**Grid**
**Behaviour changes**

- <Added | Modified | Removed> Default sort: `<field>` `<asc\|desc>`.
- <Added | Modified | Removed> Pagination: <client-side, no server pagination | …>.
- <Added | Modified | Removed> Row interaction: <what a row click opens>.

**Grid columns** _(changed columns only: added/modified/removed)_

| Column | Source field | Change | Description |
|---|---|---|---|
| `<column>` | `<response field>` | `<Added\|Modified\|Removed\|Obsolete>` | <formatting / oneline change summary> |

**Grid column formatting**
<!-- Shared field-formatting rules referenced by more than one grid. Delete the whole section when no rule is shared. -->

**<Field name>**

<Describe how the field renders — per entity type, per status, the displayed information, and an example.>

- **<Variant / entity type>** — Displayed information: `<fields shown>`. Example: `<example>`.

</grid-changes-template>

</details>
---

## Conventions

<!-- Cross-cutting GUI rules the feature adds, modifies, or removes (e.g. polling cadence, client-side pagination, grid-state persistence). Include ONLY changed conventions; delete the section otherwise. -->

<details>
<summary><Convention name title></summary>

<Describe the added, modified, or removed convention — e.g. a new polling cadence, no server-side pagination, grid state stored in local storage.>

</details>
---
