# Contracts Delta (embedded)

Use to assemble the optional **Contracts Delta** appendix inside a story's Implementation notes, once per touched contract kind (API, Database, Resource, or other), plus — for `[FE]` stories — the **GUI delta** block that closes the appendix. Document changes as a delta — never restate untouched contract or untouched GUI; look up facts yourself (swagger.json, codebase, DB schema, component tree, existing routes). GUI is not a contract kind: it uses Assemble the GUI delta and its own template below, never these diff lines.

## Assemble the contract delta
Instantiate one copy of the template below per contract kind touched; delete unused copies. Per contract kind, in order:

- One `Legend:` line defining that kind's tags (API: `hd`/`qp`/`req`/`res`/`sc`=status code; DB: none — use dotted field paths; Resource: none — use dotted field paths; other: define own).
- List every resource (endpoint, table, infra resource, etc.) added, modified, or removed. Per resource: header (`METHOD /path` for API, `Table name` for DB, `{{resourceType}}: {{resourceName}}` for Resource — e.g. `Queue: order-events`, `IAM Role: deploy-role`, `Bucket: uploads-raw` — equivalent for other kinds), then delta lines only — `+` add, `-` remove, `% old → new` rename (field renamed, same meaning), `~ oldSpec → newSpec` modify (same field name; spec = type, constraint, validation, default, or required↔optional) — with type, constraint, validation, default value, one-line reason.
- Order API resource headers by path, then by HTTP method within each path: `GET` → `POST` → `PUT` → `PATCH` → `DELETE`. Order DB resource headers alphabetically by table name. Order Resource headers alphabetically by `resourceType` then `resourceName` (other: define an analogous order).
- Order delta lines by tag group first (API: `hd` → `qp` → `req` → `res` → `sc`, in request/response lifecycle order; DB and Resource: no tag groups — order by field path; other: define an analogous group order), then by operation within each group (`+` before `%` before `~` before `-`).
- When the same delta applies identically to multiple resources, combine their headers into one CSV header instead of repeating the delta lines — e.g. `{{resourceHeader1}}, {{resourceHeader2}}`.
- `**Behaviour changes**` — system changes not visible in the delta lines themselves (e.g. a default list order set server-side, a new exception type thrown) — one line per item, `+|~|-` prefix; nested inside its contract type's own block, not a separate top-level section.
- `Objects referenced` only when an object/enum appears in more than one place — one line per shared object/enum.

## Contract delta template
Copy, populate every `{{placeholder}}`:

````markdown
## {{contractType}} delta
<!-- Diff-style (+/-/~ prefix, one line per field) -->

Legend: `+` add · `-` remove · `% old → new` rename · `~` modify (same name, `oldSpec → newSpec`; spec = type, constraint, validation, default, or required↔optional) · `{{tag}}` {{meaning}} · `{{tag}}` {{meaning}}.

```
{{resourceHeader| e.g. "METHOD /path?[sort]&[order]", "{{table}}", or "{{resourceType}}: {{resourceName}}"; CSV multiple resources sharing the same delta: "{{resourceHeader1}}, {{resourceHeader2}}"}}
+ {{tag}}  {{field}}            {{type|type name+constraint, e.g. string≤4000}}    {{notes}}
% {{tag}}  {{old}} → {{new}}    {{type}}                                           {{renameReason}}
~ {{tag}}  {{field}}            {{oldSpec}} → {{newSpec}}                          {{modifyReason}}
- {{tag}}  {{field}}            {{type}}                                           {{removalReason}}
+ {{tag}}  {{statusCode}}       {{type}}                                           {{meaning| e.g. "accepted, async started"}}
- {{tag}}  {{statusCode}}       {{type}}                                           {{removalReason}}

{{nextResourceHeader}}
+ {{fieldPath| DB/Resource/other: no tag, dotted field path}}             {{type}}    {{constraintOrDescription}}
```

**Behaviour changes:**
<!-- Omit if this section has no validation/side-effect/ordering/error/convention change. -->

- {{changeType| One of (+|-|~)}} {{change| one line}}.

## Objects referenced
<!-- Omit if the diff above references no shared object/enum shorthand. -->

```
{{name}} (object) = { "type":"{{typeName}}", {{field}}({{type|type name+constraint, e.g. string≤4000}}), {{field}}?({{type|type name+constraint}}) }
{{name}} (enum)   = {{member}}={{value}} | {{member}}={{value}}
```

````

**Done when (contract delta):** every touched contract kind has its block; every resource has its header and delta lines, ordered by tag group then operation (`+`/`%`/`~`/`-`); every line is tagged and pure (no untouched field); renames use `%` and in-place spec changes use `~` — never combined; Objects referenced and Behaviour changes appear only when non-empty.

## Assemble the GUI delta
Applies to `[FE]` stories only, and only when the capability adds or changes a surface, GUI component, or interaction. Organise by **surface** — either a **page**, or a **GUI component** (`Toolbar`, `Header component`, `Panel`, `Modal`, `Grid`, …), including a utility component or a Layout component used across pages such as header, menu, or badge. In order:

- One `###` entry per surface the story adds or changes, ordered alphabetically by surface name. A component that sits on a page names that page in its one-line summary — never nest it under a page entry.
- Every surface records its changes as **Behaviour changes** bullets, each starting with an **Added**, **Modified**, or **Removed** marker — use **Obsolete** for a field the backend still returns but the GUI must stop using.
- Fold data loading into a Behaviour-changes bullet: name the exact call the surface fires (`GET /api/v2/…`) and the polling cadence when it polls, so the GUI ties back to the story's API delta.
- A `Grid` surface also carries **Grid columns** — **only changed** columns, each with a `Change` column — and, when a field-rendering rule is shared across its columns, an inline **Grid column formatting** block.
- Cross-cutting GUI rules the story adds, modifies, or removes live under `### Conventions`; omit the section when nothing cross-cutting changed.

## Assemble the GUI API calls
The **API calls** block closes each surface entry and tells an FE dev exactly which request to fire and what comes back. In order:

- One title+http-block pair per distinct call implied by that surface's data-loading bullets or the requirements above (different filter/query-param combo, different status/header value, success vs failure variant, with-data vs null/absent variant).
- Each title carries the trigger that fires the call — `on page load`, `every 30s while the page is active`, `on filter change`, `on row click`, `on submit` — matching a data-loading bullet on that surface.
- Cover every variant the surface renders differently, including the empty result and the failure status when the acceptance criteria imply them.
- Skip a surface's whole block when there is only one trivial way to call it — never invent a call without a backing requirement or delta bullet.
- Title is caller intent in bold-italic text, not mechanics — no numbering, no "Use case/Call N:" prefix, no markdown header.
- Omit the request `Content-Type` line when there is no body.
- Pull field names, casing, and enum values from the swagger/contract file; elide unrelated nested objects that exist in the real schema as `"field": { "...": "..." }` instead of omitting or flattening them.
- Trim the response body to the fields the call illustrates plus minimal identifying fields (id/name). Keep arrays to 1–2 representative items.

## GUI delta template
Copy, populate every `{{placeholder}}`, delete every unused part and every hidden instruction:

`````markdown
## GUI delta

### {{surfaceName| page | Toolbar | Header component | Panel | Modal | Grid | …}} — `{{Added|Modified|Removed}}`

{{surfaceSummary|one line; for a page, give its route, e.g. `/monitoring`; for a component, name the page or layout it sits on}}

**Behaviour changes**

- {{Added|Modified|Removed}} {{change|route / default state / interaction / validation / ordering / side effect / default sort / pagination / row interaction}}.
- {{Added|Modified|Removed}} Data loading — fires `{{verb}} {{path}}?{{params}}` {{cadence|every `n` seconds when polling | on open | on action}}. {{notes|tweakable client-side? stop-when-inactive?}}

**Grid columns** <!-- Grid surfaces only; changed columns only: added/modified/removed/obsolete -->

| Column | Source field | Change | Description |
|---|---|---|---|
| `{{column}}` | `{{responseField}}` | `{{Added|Modified|Removed|Obsolete}}` | {{description|formatting / one-line change summary}} |

**Grid column formatting**
<!-- Shared field-formatting rules referenced by more than one column. Delete the whole block when no rule is shared. -->

**{{fieldName}}**

{{renderingRule|how the field renders — per entity type, per status, the displayed information, and an example}}

- **{{variant|variant / entity type}}** — Displayed information: `{{fieldsShown}}`. Example: `{{example}}`.

**API calls**
<!-- One title+http-block pair per distinct call implied by this surface's data-loading bullets or requirements (different filter/query-param combo, different status/header value, success vs failure variant, with-data vs null/absent variant); cover the empty result and the failure status when the acceptance criteria imply them. Skip the whole block if there's only one trivial way to call it — never invent a call without a backing requirement or delta bullet. Title is caller intent in bold-italic text plus the trigger that fires the call, not mechanics — no numbering, no "Use case/Call N:" prefix, no markdown header. Omit the request Content-Type line when there's no body. Pull field names, casing, and enum values from the swagger/contract file; elide unrelated nested objects that exist in the real schema as "field": { "...": "..." } instead of omitting or flattening them. Trim the response body to fields the call illustrates plus minimal identifying fields (id/name). Keep arrays to 1–2 representative items. -->

_{{shortCallName}}_ — fires {{trigger|on page load | every `n`s while the page is active | on filter change | on row click | on submit}}.

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

### Conventions
<!-- Cross-cutting GUI rules the story adds, modifies, or removes (e.g. polling cadence, client-side pagination, grid-state persistence). Include ONLY changed conventions; delete the section otherwise. -->

**{{conventionName}}**

{{convention|the added, modified, or removed rule — e.g. a new polling cadence, no server-side pagination, grid state stored in local storage}}

`````

**Done when (GUI delta):** every added or changed surface has its own `###` entry, ordered alphabetically; every bullet carries an Added/Modified/Removed/Obsolete marker; every data-loading bullet names its call and cadence; grid tables list changed columns only; every API call traces to a data-loading bullet or requirement, names the trigger that fires it, and shows both request and response; Grid columns, Grid column formatting, API calls, and Conventions appear only when non-empty; no hidden instruction or unused placeholder survives.
