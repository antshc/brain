# Contracts Delta (embedded)

Use to assemble the optional **Contracts Delta** appendix inside a story's Implementation notes, once per touched contract kind (API, Database, Resource, or other). Document contract changes as a terse diff — never restate untouched contract; look up facts yourself (swagger.json, codebase, DB schema). GUI changes are not a contract kind here — they use [gui-delta.md](gui-delta.md) and its own format, never these diff lines.

## Assemble the delta
Instantiate one copy of the template below per contract kind touched; delete unused copies. Per contract kind, in order:

- One `Legend:` line defining that kind's tags (API: `hd`/`qp`/`req`/`res`/`sc`=status code; DB: none — use dotted field paths; Resource: none — use dotted field paths; other: define own).
- List every resource (endpoint, table, infra resource, etc.) added, modified, or removed. Per resource: header (`METHOD /path` for API, `Table name` for DB, `{{resourceType}}: {{resourceName}}` for Resource — e.g. `Queue: order-events`, `IAM Role: deploy-role`, `Bucket: uploads-raw` — equivalent for other kinds), then delta lines only — `+` add, `-` remove, `% old → new` rename (field renamed, same meaning), `~ oldSpec → newSpec` modify (same field name; spec = type, constraint, validation, default, or required↔optional) — with type, constraint, validation, default value, one-line reason.
- Order API resource headers by path, then by HTTP method within each path: `GET` → `POST` → `PUT` → `PATCH` → `DELETE`. Order DB resource headers alphabetically by table name. Order Resource headers alphabetically by `resourceType` then `resourceName` (other: define an analogous order).
- Order delta lines by tag group first (API: `hd` → `qp` → `req` → `res` → `sc`, in request/response lifecycle order; DB and Resource: no tag groups — order by field path; other: define an analogous group order), then by operation within each group (`+` before `%` before `~` before `-`).
- When the same delta applies identically to multiple resources, combine their headers into one CSV header instead of repeating the delta lines — e.g. `{{resourceHeader1}}, {{resourceHeader2}}`.
- `**Behaviour changes**` — system changes not visible in the delta lines themselves (e.g. a default list order set server-side, a new exception type thrown) — one line per item, `+|~|-` prefix; nested inside its contract type's own block, not a separate top-level section.
- `Objects referenced` only when an object/enum appears in more than one place — one line per shared object/enum.

## Template
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

**Done when:** every touched contract kind has its block; every resource has its header and delta lines, ordered by tag group then operation (`+`/`%`/`~`/`-`); every line is tagged and pure (no untouched field); renames use `%` and in-place spec changes use `~` — never combined; Objects referenced and Behaviour changes appear only when non-empty.
