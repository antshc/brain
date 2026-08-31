# GUI Delta (embedded)

Use to assemble the optional **GUI delta** block inside a story's Implementation notes → Contracts Delta appendix. Applies to `[FE]` stories only, and only when the capability adds or changes a surface, sub-component, grid, or interaction. Document the GUI **delta** — never restate untouched GUI; look up facts yourself (component tree, existing routes, swagger.json).

## Assemble the delta
Organise by **surface** — either a **page** (its entry documents changes to the GUI components on that page) or a **GUI component** itself (a utility component, or a Layout component used across pages such as header, menu, or badge). In order:

- One `<details>` entry per surface the story adds or changes. Order surfaces alphabetically by surface name; within a surface, order sub-components Toolbar → Panel → Modal → Grid.
- Every surface, sub-component (toolbar, panel, modal, grid), and grid records its changes as **Behaviour changes** bullets, each starting with an **Added**, **Modified**, or **Removed** marker — use **Obsolete** for a field the backend still returns but the GUI must stop using.
- Fold data loading into a Behaviour-changes bullet: name the exact call the surface fires (`GET /api/v2/…`) and the polling cadence when it polls, so the GUI ties back to the story's API delta.
- Grid columns list **only changed** columns, each with a `Change` column; field-rendering rules shared across a grid's columns live in that grid's inline **Grid column formatting** block.
- Cross-cutting GUI rules the story adds, modifies, or removes live under `## Conventions`; omit the section when nothing cross-cutting changed.

## Assemble the scenarios
The scenarios close the GUI delta and tell an FE dev exactly which request to fire and what comes back. One `<details>` per surface, summary `Scenarios — {{surfaceName}}`, in the same surface order as the delta above. In order:

- One title+http-block pair per distinct scenario implied by that surface's data-loading bullets or the requirements above (different filter/query-param combo, different status/header value, success vs failure variant, with-data vs null/absent variant).
- Each title carries the trigger that fires the call — `on page load`, `every 30s while the page is active`, `on filter change`, `on row click`, `on submit` — matching a data-loading bullet on that surface.
- Cover every variant the surface renders differently, including the empty result and the failure status when the acceptance criteria imply them.
- Skip a surface's whole block when there is only one trivial way to call it — never invent a scenario without a backing requirement or delta bullet.
- Title is caller intent in bold-italic text, not mechanics — no numbering, no "Use case/Scenario N:" prefix, no markdown header.
- Omit the request `Content-Type` line when there is no body.
- Pull field names, casing, and enum values from the swagger/contract file; elide unrelated nested objects that exist in the real schema as `"field": { "...": "..." }` instead of omitting or flattening them.
- Trim the response body to the fields the scenario illustrates plus minimal identifying fields (id/name). Keep arrays to 1–2 representative items.

## Template
Copy, populate every `{{placeholder}}`, delete every unused part and every hidden instruction:

`````markdown
## GUI delta

## {{pagesOrGuiComponent}}

### {{guiComponentName|omit unless the component sits under a page}}

<details>
<summary>{{surfaceName|page or GUI component}} — `{{Added|Modified|Removed}}`</summary>

{{surfaceSummary|one line; for a page, give its route, e.g. `/monitoring`}}

**Behaviour changes**

- {{Added|Modified|Removed}} {{change|route / default state / interaction / validation / ordering / side effect}}.
- {{Added|Modified|Removed}} Data loading Fires `{{verb}} {{path}}?{{params}}` {{cadence|every `n` seconds when polling | on open | on action}}. {{notes|tweakable client-side? stop-when-inactive?}}

**{{subComponent|Toolbar | Header component | Panel | Modal}}** <!-- omit when the surface has none -->

**Behaviour changes**

- {{Added|Modified|Removed}} {{change|route / default state / interaction / validation / ordering / side effect}}.
- {{Added|Modified|Removed}} Data loading Fires `{{verb}} {{path}}?{{params}}` {{cadence|every `n` seconds when polling | on open | on action}}. {{notes|tweakable client-side? stop-when-inactive?}}

<!-- Grid: omit the whole block when the surface has no table. -->

**Grid**

**Behaviour changes**

- {{Added|Modified|Removed}} Default sort: `{{field}}` `{{asc|desc}}`.
- {{Added|Modified|Removed}} Pagination: {{pagination|client-side, no server pagination | …}}.
- {{Added|Modified|Removed}} Row interaction: {{rowInteraction|what a row click opens}}.

**Grid columns** <!-- changed columns only: added/modified/removed -->

| Column | Source field | Change | Description |
|---|---|---|---|
| `{{column}}` | `{{responseField}}` | `{{Added|Modified|Removed|Obsolete}}` | {{description|formatting / one-line change summary}} |

**Grid column formatting**
<!-- Shared field-formatting rules referenced by more than one column. Delete the whole block when no rule is shared. -->

**{{fieldName}}**

{{renderingRule|how the field renders — per entity type, per status, the displayed information, and an example}}

- **{{variant|variant / entity type}}** — Displayed information: `{{fieldsShown}}`. Example: `{{example}}`.

</details>

## Conventions
<!-- Cross-cutting GUI rules the story adds, modifies, or removes (e.g. polling cadence, client-side pagination, grid-state persistence). Include ONLY changed conventions; delete the section otherwise. -->

<details>
<summary>Conventions</summary>

**{{conventionName}}**

{{convention|the added, modified, or removed rule — e.g. a new polling cadence, no server-side pagination, grid state stored in local storage}}

</details>

<!-- Scenarios: one <details> per surface, in the same order as the delta above. One title+http-block pair per distinct scenario implied by that surface's data-loading bullets or requirements (different filter/query-param combo, different status/header value, success vs failure variant, with-data vs null/absent variant); cover the empty result and the failure status when the acceptance criteria imply them. Skip a surface's block if there's only one trivial way to call it — never invent a scenario without a backing requirement or delta bullet. Title is caller intent in bold-italic text plus the trigger that fires the call, not mechanics — no numbering, no "Use case/Scenario N:" prefix, no markdown header. Omit the request Content-Type line when there's no body. Pull field names, casing, and enum values from the swagger/contract file; elide unrelated nested objects that exist in the real schema as "field": { "...": "..." } instead of omitting or flattening them. Trim the response body to fields the scenario illustrates plus minimal identifying fields (id/name). Keep arrays to 1–2 representative items. -->

<details>
<summary>Scenarios — {{surfaceName|page or GUI component}}</summary>

_{{shortScenarioName}}_ — fires {{trigger|on page load | every `n`s while the page is active | on filter change | on row click | on submit}}.

```http
{{method}} {{path}}{{?query}} HTTP/1.1
Host: {{host}}
Authorization: Bearer {{token}}
{{endpointSpecificHeader}}: {{value}}
Content-Type: application/json

{{requestBody}}

HTTP/1.1 {{statusCode}} {{statusText}}
Content-Type: application/json

{{responseBody}}
```

</details>

`````

**Done when:** every added or changed surface has a `<details>` entry, ordered alphabetically; every bullet carries an Added/Modified/Removed/Obsolete marker; every data-loading bullet names its call and cadence; grid tables list changed columns only; every scenario traces to a data-loading bullet or requirement, names the trigger that fires it, and shows both request and response; a blank line follows every `</summary>` so the markdown inside renders; Grid column formatting, Conventions, and Scenarios appear only when non-empty; no hidden instruction or unused placeholder survives.
