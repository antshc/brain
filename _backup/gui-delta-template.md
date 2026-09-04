# GUI delta — template

Fill this template to document the GUI **delta** a feature introduces. Copy only the parts you need, replace every `<placeholder>`, and delete the rest.

- The section is organised by **surface** — either a **page**, or a **GUI component** (`Toolbar`, `Header component`, `Panel`, `Modal`, `Grid`, …), including a utility component or a Layout component used across pages such as header, menu, or badge. Add one flat `<details>` entry per surface the feature adds or changes, ordered alphabetically by surface name — a component that sits on a page names that page in its one-line summary, never nested inside another surface's entry.
- Every surface records its changes as **Behaviour changes** bullets, each starting with an **Added**, **Modified**, or **Removed** marker (use **Obsolete** for a field the backend still returns but the GUI must stop using).
- Fold data loading into a Behaviour-changes bullet: name the exact API call the surface fires (`GET /api/v2/…`) and the polling cadence when it polls, so the GUI ties back to the ZIC API section.
- A `Grid` surface also carries **Grid columns** — only changed columns, each with a `Change` column — and, when a field-rendering rule is shared across its columns, an inline **Grid column formatting** block.
- Cross-cutting GUI rules live under `## Conventions`.

---

<details>
<summary><Surface name — page, Toolbar, Header component, Panel, Modal, Grid, …> — `<Added | Modified | Removed>`</summary>

<One-line summary of the surface.> _(For a page, give its route, e.g. `/monitoring`; for a component, name the page or layout it sits on.)_

**Behaviour changes**

- <Added | Modified | Removed> <route / default state / interaction / validation / ordering / side effect>.
- <Added | Modified | Removed> Data loading Fires `<VERB> <path>?<params>` <every `<n>` seconds when polling | on open | on action>. <Tweakable client-side? stop-when-inactive?>

**Grid columns** _(Grid surfaces only; changed columns only: added/modified/removed)_

| Column | Source field | Change | Description |
|---|---|---|---|
| `<column>` | `<response field>` | `<Added\|Modified\|Removed\|Obsolete>` | <formatting / oneline change summary> |

**Grid column formatting**
<!-- Shared field-formatting rules referenced by more than one column. Delete the whole block when no rule is shared. -->

**<Field name>**

<Describe how the field renders — per entity type, per status, the displayed information, and an example.>

- **<Variant / entity type>** — Displayed information: `<fields shown>`. Example: `<example>`.

</details>
---

## Conventions

<!-- Cross-cutting GUI rules the feature adds, modifies, or removes (e.g. polling cadence, client-side pagination, grid-state persistence). Include ONLY changed conventions; delete the section otherwise. -->

<details>
<summary>Conventions</summary>

**<Convention name title>**

<Describe the added, modified, or removed convention — e.g. a new polling cadence, no server-side pagination, grid state stored in local storage.>

</details>
---

**Done when:** every added or changed surface has its own flat entry, ordered alphabetically, never nested inside another surface's entry; every bullet carries an Added/Modified/Removed/Obsolete marker; every data-loading bullet names its call and cadence; grid tables list changed columns only; Grid columns, Grid column formatting, and Conventions appear only when non-empty; no unused placeholder survives.
