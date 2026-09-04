---
argument-hint: Which feature design document, and which contract(s) changed (API, database, resource, other, GUI)?
description: Write an API, database, resource, other contract, or GUI delta into a feature design document as a terse diff — only what each resource or surface adds, modifies, or removes. Use whenever documenting REST endpoint changes, DynamoDB/table schema changes, swagger/OpenAPI diffs, queue/topic/bucket/IAM role/Terraform resource changes, a "Contract changes"/"Endpoints" section, a breaking-changes list, user-visible GUI state or interaction changes, or any "what changed in the API/DB/resource contract/UI" write-up for a design doc, spec, or PR description — even if the user just says "document the API changes", "add the endpoint delta", or "document the GUI changes" without naming this skill.
disable-model-invocation: true
name: to-contract-delta
---

Document contract and GUI changes as a terse diff — never restate untouched contract or surface. Look up facts yourself (swagger.json, codebase, DB schema, GUI source).

## Assemble and write a contract delta

Instantiate one copy of [contract-delta-template.md](templates/contract-delta-template.md) per contract kind touched (API, Database, Resource, or other); delete unused copies. Open the template with the file-reading tool before drafting — do not compose from memory. Per contract kind, in the order the template defines:

- One `Legend:` line defining that kind's tags (API: `hd`/`qp`/`req`/`res`/`sc`=status code; DB: none — use dotted field paths; Resource: none — use dotted field paths; other: define own).
- One `#### {{resourceHeader}}` + `<details>` block per resource (endpoint, table, infra resource, etc.) added, modified, or removed — header (`METHOD /path` for API, `Table name` for DB, `{{resourceType}}: {{resourceName}}` for Resource — e.g. `Queue: order-events`, `IAM Role: deploy-role`, `Bucket: uploads-raw` — equivalent for other kinds), then delta lines only — `+` add, `-` remove, `% old → new` rename (field renamed, same meaning), `~ oldSpec → newSpec` modify (same field name; spec = type, constraint, validation, default, or required↔optional) — with type, constraint, validation, default value, one-line reason.
- Order API resource headers by path, then by HTTP method within each path: `GET` → `POST` → `PUT` → `PATCH` → `DELETE`. Order DB resource headers alphabetically by table name. Order Resource headers alphabetically by `resourceType` then `resourceName` (other: define an analogous order).
- Order delta lines by tag group first (API: `hd` → `qp` → `req` → `res` → `sc`, in request/response lifecycle order; DB and Resource: no tag groups — order by field path; other: define an analogous group order), then by operation within each group (`+` before `%` before `~` before `-`).
- When the same delta applies identically to multiple resources, combine their headers into one CSV header instead of repeating the delta lines — e.g. `{{resourceHeader1}}, {{resourceHeader2}}`.
- `**Behaviour changes**` — system changes not visible in the delta lines themselves (e.g. a default list order set server-side, a new exception type thrown) — one line per item, `+|~|-` prefix; nested inside its own resource's `<details>`, not a separate top-level section.
- `Scenarios` — API resources only, never DB/Resource/other — one title+HTTP-block pair per distinct scenario implied by the delta lines or requirements (different filter/query-param combo, different status/header value, success vs failure variant); skip when there is only one trivial way to call the resource.
- `Objects referenced` only when an object/enum appears in more than one resource block within that contract kind — one line per shared object/enum, once per contract kind (not once per resource).

**Done when:** every touched contract kind has its own copies; every resource has its own `#### header` + `<details>` block, ordered by tag group then operation (`+`/`%`/`~`/`-`); every line is tagged and pure (no untouched field); renames use `%` and in-place spec changes use `~` — never combined; Scenarios appear only under API resources; Objects referenced and Behaviour changes appear only when non-empty.

## Assemble and write a GUI delta

Instantiate one copy of the Skeleton in [gui-delta-template.md](templates/gui-delta-template.md) per surface (page or route family) touched; delete unused copies. Open the template with the file-reading tool before drafting — do not compose from memory. Per surface, in the order the template defines:

- One `#### {{page name}}` + `<details>` block per touched surface, all its rows in one fenced code block, grouped per the template's Grouping rules (Page → Tab header → Tab content → Components in tab content).
- Declare each component with its kind as the row tag from the Component kinds table, diff-tagged (`+`/`%`/`~`/`-`); reference a component reused across more than one surface via a `ref` row instead of redeclaring it.
- Route (`rt`), data-loading (`data`), and event (`ev`) rows per the template's Route conventions, Data-loading triggers, and Event vocabulary tables.
- `**Behaviour changes**` — non-tabular rule changes (validation, batching, error handling, ordering) — nested inside its own surface's `<details>`.
- `Scenarios` — one title+trace pair per distinct scenario implied by the delta rows or requirements; skip when there is only one trivial way to use the surface.
- `Components referenced` only when a component is shown on more than one surface — one `#### {{kind}}:{{name}}` sub-section per shared component, once after every surface block (not once per surface).

**Done when:** every touched surface has its own `#### page name` + `<details>` block; every component row is diff-tagged and pure; every table declares `table.sort`; every `link` carries `link.title` or `link.icon`+`link.tip`; a component shown on more than one surface is declared once under Components referenced and pulled in elsewhere via `ref`; Scenarios and Behaviour changes appear only when non-empty.

