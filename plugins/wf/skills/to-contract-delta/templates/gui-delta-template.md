## GUI delta
<!-- Diff-style (+/-/~ prefix, one line per component). Instantiate one copy of the Skeleton below per surface (page or route family) touched; delete unused copies. -->

## Legend

- A **surface** is always a full page (a route or route family) — never a widget.
- A **component** is any addressable UI part on a surface (badge, button, table, modal, header, menu, breadcrumb, …).
- A component reused across more than one surface (e.g. a persistent header, a left/right menu, a breadcrumb) is declared once under "Components referenced" and pulled onto each surface that shows it with a `ref` row — never redeclared inline.
- Diff tags: `+` add · `-` remove · `% old → new` rename · `~ old → new` modify (same name, spec changed).
- `rt` marks a route; `data` marks a data-loading call (endpoint + cadence/trigger).
- A component is declared with its **kind as the row tag** (`badge`, `button`, `table`, `link`, `modal`, … — full list below), followed by `{{name}}` and a one-line behavior.
- A container kind (`table`, `toolbar`, `tabs`) scopes any child's `{{name}}` as `{{containerName}}.{{itemName}}`, regardless of the child's own kind (e.g. a `badge` decorating one `tabs` item).
- A component's own single-trigger click effect is noted directly in its declare row, appended to the one-line behavior as `, click → {{effect}}` — never a separate row.
- A table's own row-click effect is noted the same way in its `table` declare row (e.g. `table {{name}} {{behavior}}, click row → opens {{kind}}.{{path}}`).
- A column's own per-row clickable content is noted the same way in that column's `table.col` row (e.g. `table.col {{column}} data.{{field}} renders link:{{name}}, click → {{effect}}`).
- A component's user-visible text is a further row tagged `{{kind}}.{{fact}}`, scoped to the same `{{name}}`: `.title`/`.content` for its visible text (modal carries both; other kinds carry `.title` only).
- Every `link` must be visibly identifiable, never bare — declare a `link.title` row for its visible text label, a `link.icon` row (named for the icon shown) when it renders as an icon instead of or alongside text, and a `link.tip` row for its hover tooltip whenever it has an icon but no visible text label.
- `.hd` is a table column's header label (`table.hd`, named `{{column}}` only — the table it belongs to was already declared once via its `table` row, so rows under it never repeat `{{tableName}}.`), always added for every column, even when the label matches `{{column}}`.
- `.col` is that column's data source (`table.col`, same scope), sourced from `data.{{field}}` — join with `+` for more than one field (e.g. `data.{{field1}}+{{field2}}`) — `derived` when computed client-side with no direct API field, or `select` for a row-selection checkbox column (no data source; its presence is what enables selection-gated toolbar controls elsewhere on the page).
- Every `table` must declare its default sort via a `table.sort` row (`table.sort {{tableName}} {{column}} asc|desc`) — repeat the row, in priority order, for a composite sort; this replaces stating default sort as prose in Behaviour changes.
- A column's header can itself drive sorting and/or filtering — append `, sortable` to its `table.hd` row when clicking the header toggles that column's sort, and `, search` when the header hosts an inline per-column filter input, distinct from a toolbar's page-level quick filter (`input` under `toolbar`).
- When a `sortable` or `search` header renders as its own icon, add a `table.hd.tip` row for its hover tooltip, scoped `{{column}}.sort` or `{{column}}.search` (e.g. `table.hd.tip {{column}}.search "{{tooltip text}}"`) — omit only when the header's own visible label already makes the icon's purpose obvious.
- A row-actions column (per-row icon/button controls) is declared the same way with source `derived`, its one-line behavior naming each control as `{{kind}}:{{name}}`; each control gets its own declare row plus a `.tip` fact row for its hover tooltip (`{{kind}}.tip`, distinct from `.title`, which is always visible rather than hover-only) — the whole block headed by a bare `table.col.{{column}}` row before the per-control declare+`.tip` rows.
- Use plain `ev` instead of a component-owned click row when the trigger doesn't belong to one component alone (cross-component) or is more than a bare click (e.g. select rows + click button, or clicking one icon inside a row).
- Add a `.fact` row only when it isn't already obvious from the component's declare row.
- `ev` marks a cross-component trigger/interaction that doesn't belong to one component alone (`trigger → effect`, e.g. a row click inside a table opening a popover, or a batch action combining a row selection with a button click).
- `ref` references a component defined once under "Components referenced" (`ref {{kind}}:{{name}}`; add `({{variant}})` when this spot shows one specific value/state of it) — used in place of a declare row or a `.fact` row, instead of redeclaring the shared component's behavior.
- A component opened from more than one trigger source must always carry parenthetical text at every reference — declare row, `ref`, or click effect — e.g. `{{kind}}.{{path}}({{what it shows}})`, so the text keeps each site self-explanatory without following the reference elsewhere. A component with a single trigger source needs no parenthetical text.

**Component kinds** (also the row tag used to declare each):

| kind | meaning |
|---|---|
| `layout` | persistent structural region hosting other components, reused across every (or almost every) surface (e.g. Header, Footer) |
| `breadcrumb` | persistent trail of navigational links showing the current location |
| `badge` | small numeric/status indicator on a widget |
| `dropdown` | floating list of options or actions, usually opened by click |
| `table` | tabular list; columns declared via `col {{name}}.{{column}}` |
| `toolbar` | container that groups action controls (`input`, `toggle`, `button`, `chooser`); children declared via `{{childKind}}:{{toolbarName}}.{{itemName}}` |
| `tabs` | tab-strip navigation; declared once with its items and default (`tabs {{tabsName}} {{item1}} \| {{item2}}; default = {{item}}`); each item's nav trigger is a `tabs.nav` row (`tabs.nav {{tabsName}}.{{tabItem}} {{decoration, e.g. badge}}; click → navigate {{route}}`) and its rendered body is a `tabs.content` row (`tabs.content {{tabsName}}.{{tabItem}}`, header for that tab's own component groups — see Grouping) |
| `accordion` | vertically stacked, collapsible content panels; declared once with its items (`accordion {{name}} {{item1}} \| {{item2}}; default open = {{item}}`) |
| `alert` | contextual inline message banner (info/success/warning/error), dismissible or static |
| `modal` | blocking confirmation/dialog overlay |
| `popover` | floating interactive content, usually opened by click; may contain buttons, links, or other controls |
| `tooltip` | short, non-interactive contextual information, usually shown on hover or focus |
| `toast` | small, timed, self-dismissing notification |
| `collapse` | toggleable container that shows/hides its content in place, without navigating away |
| `carousel` | slideshow cycling through a set of content panels/images |
| `pagination` | page-number navigation control for a table or list |
| `progress` | horizontal bar showing completion percentage |
| `spinner` | indeterminate loading indicator |
| `toggle` | on/off switch |
| `checkbox` | independent binary on/off selection control (e.g. a table's `select` row-selection column) |
| `radio` | single-select control among a mutually exclusive group, declared once with its group's options |
| `input` | free-text field |
| `textarea` | free-text multi-line field |
| `range` | slider input selecting a numeric value from a bounded range |
| `chooser` | multi-option selection control (e.g. column chooser) |
| `button` | clickable action trigger |
| `headline` | static/conditional text line |
| `link` | navigable text anchor |
| `menu` | persistent side navigation panel (e.g. left menu, right menu) |
| `icon` | small pictographic indicator, often data-driven (e.g. severity level) |

**Route conventions** (`rt` values):

| form | meaning |
|---|---|
| `{{path}}` | a route this surface owns |
| `{{path}}   default child route → {{childPath}}` | index route that renders/redirects to `{{childPath}}` by default |
| `*` | present on every route (global/persistent element, e.g. Header, left/right menu) |
| `* except {{path}}` | present on every route except the listed one(s) (hidden there) |

**Data-loading triggers** (`data` cadence column):

| trigger | meaning |
|---|---|
| `poll {{n}}s` | refetches every n seconds while the surface is mounted, regardless of focus |
| `poll {{n}}s while active` | refetches every n seconds only while this tab/panel is the active one; stops otherwise |
| `on open` | fires once when the panel/modal opens |
| `on action` | refetches once after a user action (e.g. a batch call) completes |

**Event vocabulary** (`ev` trigger / effect column):

| part | common values |
|---|---|
| trigger | `click {{kind}}:{{name}}` · `select rows + click {{kind}}:{{name}}` · `click {{descriptor}} in table:{{name}}` (e.g. an icon inside one row) |
| effect | `opens {{kind}}:{{name}}` · `closes {{kind}}:{{name}}` · `navigate {{route}}` · `{{METHOD}} {{path}}` (add `parallel, 1 per selected row` when batched) |

## Skeleton

<!-- Repeat this per surface (page or route family) touched. All of a page's rows live in one fenced code block — never split components into separate blocks under bold or markdown headers. -->

#### {{page name}}
<details>
<summary>{{page name}}</summary>

```text
+ rt         {{route}}
+ ref        {{kind}}:{{name}}                 <!-- persistent component shown on this page, e.g. layout:Header -->
+ data       {{METHOD}} {{path}}{{?query}}     poll {{n}}s | on {{trigger}}
+ {{kind}}   {{name}}                          {{one-line behavior}}
~ {{kind}}   {{name}}                          {{oldSpec}} → {{newSpec}}
+ {{kind}}   {{name}}                          click → {{effect}}   <!-- component's own single-trigger click, appended inline on a shared kind row when it doesn't already carry a one-line behavior -->
+ {{kind}}.title   {{name}}                    "{{visible text}}"
+ modal.title      {{name}}                    "{{visible title text}}"
+ modal.content    {{name}}                    "{{visible body text}}"
+ link.title       {{name}}                    "{{visible text label}}"   <!-- required unless the link is icon-only -->
+ link.icon        {{name}}                    "{{icon shown}}"           <!-- when rendered as an icon instead of or alongside text -->
+ link.tip         {{name}}                    "{{hover tooltip text}}"   <!-- required when the link has an icon but no visible text label -->
+ ev               {{cross-component trigger}} → opens {{kind}}:{{name}} | {{effect}}
+ table       {{tableName}}                      {{one-line behavior}}, click row → opens {{kind}}:{{name}} | {{effect}}
+ table.sort  {{tableName}}                      {{column}} asc|desc   <!-- required default sort; repeat in priority order for a composite sort -->
+ table.hd    {{column}}              "{{visible header label}}"   <!-- always added, even when it matches {{column}} -->
+ table.hd    {{column}}              "{{visible header label}}", sortable   <!-- header click toggles this column's sort -->
+ table.hd    {{column}}              "{{visible header label}}", search     <!-- header hosts an inline per-column filter input -->
+ table.hd.tip  {{column}}.sort         "{{hover tooltip text}}"   <!-- required when the sort control is icon-only -->
+ table.hd.tip  {{column}}.search       "{{hover tooltip text}}"   <!-- required when the search control is icon-only -->
+ table.col   {{column}}              data.{{field}}   {{formatting/notes, if any}}
+ table.col   {{column}}              data.{{field1}}+{{field2}}   {{formatting/notes, if any}}   <!-- add ", click → {{effect}}" when this column renders a per-row clickable element -->
```

**Behaviour changes:**
<!-- Omit if this surface has no non-tabular rule change (validation, batching, error handling, ordering). -->

```text
{{+|~|-}} {{non-tabular rule: validation, batching, error handling, ordering}}.
```

<!-- Scenarios: one title+trace pair per distinct scenario implied by the delta rows or requirements above. Skip this whole Scenarios block if there's only one trivial way to use the surface — never invent a scenario without a backing requirement or delta row. Title is caller intent in bold-italic text, not mechanics. An interaction trace replaces the REST template's HTTP request/response block — same job (one concrete walkthrough per distinct case), adapted to a UI trigger chain instead of a wire request. -->

**Scenarios:**

_{{shortScenarioName}}_
```
{{user action}} → {{effect 1}} → {{effect 2}} → ...
```

</details>

## Grouping

- All of a page's rows live in **one fenced code block** — never split components into separate blocks under bold or markdown headers.
- A blank line separates each group, and a fixed four-level hierarchy fixes the order top to bottom; never flatten tab content straight to page-level rows:
  1. **Page** — routes (`rt`), persistent `ref`s, and every `data` row for the page (including each tab's own data-loading call, with its full URL) — all data rows sit together right after the `rt`/`ref` rows, never inside a tab's own content group.
  2. **Tab header** — the `tabs` component's own rows: its declare row, click→navigate rows per item, and any decoration on an item (badge, count).
  3. **Tab content** — per tab, a blank-line-separated group holding only what that tab renders, never rows that belong to another tab or to the page itself.
  4. **Components in tab content** — one blank-line-separated group per component family rendered inside that tab (toolbar, table, …); each group's own declare row (`toolbar {{name}}`, `table {{name}}`) is its label — no separate heading needed.
- A page with no tabs skips levels 2–3 and goes straight from Page to level 4's component groups; when the page renders more than one independent level-4 family (e.g. two side-by-side tables), each still gets its own blank-line group, ordered top-to-bottom / left-to-right as rendered.
- A modal, popover, or accordion item that itself hosts more than one component family (e.g. a toolbar + a table) follows the same level-4 grouping as tab content: one blank-line group per component family inside it, nested under that container's own sub-section.
- Within one group of level-4 families, order them `toolbar → alert → table → pagination`, matching top-to-bottom render order on the surface.
- Multiple `data` rows at the page level are ordered by first on-screen use (tab order, then component order within a tab) — never alphabetically.
- A page is always a full route (or route family); it never redeclares a component that's reused elsewhere.
- HTML comment markers (`<!-- Page -->`, `<!-- Tab content: {{tab}} -->`, …) are optional annotations for readability, not required syntax — blank lines alone define the groups.

## Components referenced
<details>
<summary>Components referenced</summary>

<!-- Render once, after every surface block above, not once per surface. Shared/persistent components (a header, left/right menu, breadcrumb, popovers, icons, …) used by more than one surface go here, mirroring the contract delta template's "Objects referenced". Each shared component gets its own #### {{kind}}:{{name}} sub-section, declared with the same {{kind}} {{name}} {{one-line behavior}} row (plus its own nested .title/.col/.hd rows, and Behaviour changes/Scenarios blocks, when it has sub-parts or its own delta) as a page's own list — the one definition every referencing surface points to, not a per-surface restatement. A component referenced only from within another shared component's rows (not directly from any surface) still gets its own #### {{kind}}:{{name}} sub-section here — never declared inline inside its parent's block. A surface that shows a shared component writes ref {{kind}}:{{name}} (optionally ({{variant}})) instead of a declare row or a .fact row that redeclares its behavior. Omit the whole section when no component is shared across more than one surface. -->

#### {{kind}}:{{name}}
<details>
<summary>{{kind}}:{{name}}</summary>

```text
rt      {{route| * for global}}
data    {{METHOD}} {{path}}{{?query}}     {{cadence}}
+ {{childKind}}   {{childName}}           {{one-line behavior}}
```

**Behaviour changes:**
<!-- Omit if this component has no delta. -->

```text
{{+|~|-}} {{change| one line}}.
```

**Scenarios:**
<!-- Omit if there's only one trivial way to trigger this component. -->

_{{shortScenarioName}}_
```
{{user action}} → {{effect 1}} → {{effect 2}} → ...
```

`used by {{surface names| or "* (global)" when shown on every route}}`

</details>
</details>

**Done when:** every touched surface has its `#### {{page name}}` + `<details>` block; every component row is diff-tagged (`+`/`%`/`~`/`-`) and pure (no untouched row); every table declares `table.sort`; every `link` carries `link.title` or `link.icon`+`link.tip`; a component shown on more than one surface is declared once under "Components referenced" and pulled in elsewhere via `ref`; Scenarios and Behaviour changes appear only when non-empty and every Scenario traces to a delta row or requirement.
