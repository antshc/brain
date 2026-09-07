---
argument-hint: Which feature design document, and which contract(s) changed (API, database, resource, other, GUI)?
description: Write an API, database, resource, other contract, or GUI delta into a feature design document as a terse diff — only what each resource or surface adds, modifies, or removes. Use whenever documenting REST endpoint changes, DynamoDB/table schema changes, swagger/OpenAPI diffs, queue/topic/bucket/IAM role/Terraform resource changes, a "Contract changes"/"Endpoints" section, a breaking-changes list, user-visible GUI state or interaction changes, or any "what changed in the API/DB/resource contract/UI" write-up for a design doc, spec, or PR description — even if the user just says "document the API changes", "add the endpoint delta", or "document the GUI changes" without naming this skill.
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
- `**Behaviour changes**` — system changes not visible in the delta lines themselves (e.g. a default list order set server-side, a new exception type thrown) — one line per item, `+|~|-` prefix, prefix backticked (e.g. `` `-` ``) so it never merges with the bullet marker into a double dash; nested inside its own resource's `<details>`, not a separate top-level section; omit entirely when the resource has no such change.
- `Scenarios` — API resources only, never DB/Resource/other — one title+HTTP-block pair per distinct scenario implied by the delta lines or requirements (different filter/query-param combo, different status/header value, success vs failure variant, with-data vs null/absent variant); skip when there is only one trivial way to call the resource, and never invent a scenario without a backing requirement or delta line. Title is caller intent in bold-italic text, not mechanics — no numbering, no "Use case/Scenario N:" prefix, no markdown header. Omit the request `Content-Type` line when there's no body. Pull field names, casing, and enum values from the swagger/contract file; elide unrelated nested objects as `"field": { "...": "..." }` instead of omitting or flattening them. Trim the response body to the fields the scenario illustrates plus minimal identifying fields (id/name); keep arrays to 1–2 representative items.
- `Objects referenced` only when an object/enum appears in more than one resource block within that contract kind — one line per shared object/enum, once per contract kind (not once per resource); omit the whole section when no shorthand repeats.

**Done when:** every touched contract kind has its own copies; every resource has its own `#### header` + `<details>` block, ordered by tag group then operation (`+`/`%`/`~`/`-`); every line is tagged and pure (no untouched field); renames use `%` and in-place spec changes use `~` — never combined; Scenarios appear only under API resources; Objects referenced and Behaviour changes appear only when non-empty.

## Assemble and write a GUI delta

Instantiate one copy of the skeleton in [gui-delta-template.md](templates/gui-delta-template.md) per surface (page or route family) touched; delete unused copies. Open the template with the file-reading tool before drafting — do not compose from memory. See [gui-delta-example.md](assets/gui-delta-example.md) for a full worked example. Per surface, in the order the template defines:

- Give each surface its own `#### <Page>` heading + `<details><summary><Page></summary>` expandable block, mirroring the contract delta's per-resource heading + `<details>`.
- Describe only changed UI: prefix every added/changed/removed/renamed line with `+`/`~`/`-`/`% old → new`; never repeat untouched components.
- Use indentation to express ownership and scope instead of qualified names.
- Use `match:` as optional metadata only to anchor an existing surface or component to its implementation — it carries no diff prefix; prefer a stable route, falling back to an existing component name or visible label when a route alone can't locate the implementation.
- Declare a component as `Component: Name` (omit `: Name` when the label alone is enough) and its simple properties as `key: value`.
- Use `->` for navigation/actions/opening another component, `<-` for API/data binding, `*` for the default tab/item, and `@Name` to reference a shared component declared once under `#### Components referenced`.
- Put `data:` beside the component that consumes it rather than hoisting every data call to page level.
- Use `% old → new` for a rename (same meaning); use `~` only for an in-place modify of a same-named item — never combine the two.
- Add visible text explicitly only when it differs from the component/item name or is itself important to the contract.
- `**Behaviour changes**` — rules that cannot be expressed naturally on the owning component, `+|~|-` prefix, prefix backticked (e.g. `` `-` ``) so it never merges with the bullet marker into a double dash; nested inside its own surface's `<details>`, outside the fenced diff block, mirroring the contract delta's Behaviour changes; omit entirely when the surface has no such change.
- `**Scenarios**` — one `Scenario:` (Gherkin `Given`/`When`/`Then`) per important multi-step flow, in its own fenced `gherkin` block outside the surface's diff block — never nested inside it; omit the heading when there are no scenarios.

**Done when:** every touched surface has its own `#### <Page>` heading + `<details>` block; every touched surface contains only changed UI; nesting makes ownership clear; renames use `%` and in-place changes use `~` — never combined; shared components are declared once under a `#### Components referenced` + `<details>` block; Behaviour changes and Scenarios sit outside the fenced diff block, headed by `**Behaviour changes:**`/`**Scenarios:**` when present; no component-specific grammar is introduced when indentation plus `key: value`, `->`, or `<-` is sufficient.

