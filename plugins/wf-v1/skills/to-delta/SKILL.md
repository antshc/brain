---
argument-hint: Which feature design document, and which contract(s) changed (API, database, resource, other)?
description: Write an API, database, resource, or other contract delta into a feature design document as a terse diff — only what each resource adds, modifies, or removes. Use whenever documenting REST endpoint changes, DynamoDB/table schema changes, swagger/OpenAPI diffs, queue/topic/bucket/IAM role/Terraform resource changes, a "Contract changes"/"Endpoints" section, a breaking-changes list, or any "what changed in the API/DB/resource contract" write-up for a design doc, spec, or PR description — even if the user just says "document the API changes" or "add the endpoint delta" without naming this skill.
disable-model-invocation: true
name: to-delta
---

Document contract changes as a terse diff — never restate untouched contract. Look up facts yourself (swagger.json, codebase, DB schema).

## Assemble and write the delta

Instantiate one copy of the template below per contract kind touched (API, Database, Resource, or other); delete unused copies. Per contract kind, in the order they appear in the template:

- One `Legend:` line defining that kind's tags (API: `hd`/`qp`/`req`/`res`/`sc`=status code; DB: none — use dotted field paths; Resource: none — use dotted field paths; other: define own).
- List every resource (endpoint, table, infra resource, etc.) added, modified, or removed. Per resource: header (`METHOD /path` for API, `Table name` for DB, `{{resourceType}}: {{resourceName}}` for Resource — e.g. `Queue: order-events`, `IAM Role: deploy-role`, `Bucket: uploads-raw` — equivalent for other kinds), then delta lines only — `+` add, `-` remove, `~ old → new` rename — with type, constraint, validation, default value, one-line reason.
- Order API resource headers by path, then by HTTP method within each path: `GET` → `POST` → `PUT` → `PATCH` → `DELETE`. Order DB resource headers alphabetically by table name. Order Resource headers alphabetically by `resourceType` then `resourceName` (other: define an analogous order).
- Order delta lines by tag group first (API: `hd` → `qp` → `req` → `res` → `sc`, in request/response lifecycle order; DB and Resource: no tag groups — order by field path; other: define an analogous group order), then by operation within each group (`+` before `~` before `-`).
- When the same delta applies identically to multiple resources, combine their headers into one CSV header instead of repeating the delta lines — e.g. `{{resourceHeader1}}, {{resourceHeader2}}`.
- `**Behaviour changes**` — system changes not visible in the delta lines themselves (e.g. a default list order set server-side, a new exception type thrown) — one line per item, `+|~|-` prefix; nested inside its contract type's own block, not a separate top-level section.
- `Objects referenced` only when an object/enum appears in more than one place — one line per shared object/enum.

Template — copy, populate every `{{placeholder}}`:

````markdown
## {{contractType}} delta
<!-- Diff-style (+/-/~ prefix, one line per field) -->

Legend: `+` add · `-` remove · `~ old → new` rename · `{{tag}}` {{meaning}} · `{{tag}}` {{meaning}}.

```
{{resourceHeader| e.g. "METHOD /path?[sort]&[order]", "{{table}}", or "{{resourceType}}: {{resourceName}}"; CSV multiple resources sharing the same delta: "{{resourceHeader1}}, {{resourceHeader2}}"}}
+ {{tag}}  {{field}}            {{type|type name+constraint, e.g. string≤4000}}    {{notes}}
- {{tag}}  {{field}}            {{type}}                                           {{removalReason}}
~ {{tag}}  {{old}} → {{new}}    {{type}}                                           {{renameReason}}
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

**Done when:** every touched contract kind has its block; every resource has its header and delta lines, ordered by tag group then operation; every line is tagged and pure (no untouched field); Objects referenced and Behaviour changes appear only when non-empty.

