## {{contractType}} delta
<!-- Diff-style (+/-/~ prefix, one line per field). Instantiate one copy of this block per contract kind touched (API, Database, Resource, other); delete unused copies. -->

Legend: `+` add · `-` remove · `% old → new` rename · `~` modify (same name, `oldSpec → newSpec`; spec = type, constraint, validation, default, or required↔optional) · `{{tag}}` {{meaning}} · `{{tag}}` {{meaning}}.

<!-- Repeat this resource block for every added/modified/removed resource. Order API resource headers by path, then GET → POST → PUT → PATCH → DELETE. Order DB resource headers alphabetically by table name. Order Resource headers alphabetically by resourceType then resourceName (other: define an analogous order). When the same delta applies identically to multiple resources, combine their headers into one CSV header instead of repeating the delta lines. -->

#### {{resourceHeader| e.g. "METHOD /path?[sort]&[order]", "{{table}}", or "{{resourceType}}: {{resourceName}}"; CSV multiple resources sharing the same delta: "{{resourceHeader1}}, {{resourceHeader2}}"}}
<details>
<summary>{{resourceHeader}}</summary>

<!-- Order delta lines by tag group first (API: hd → qp → req → res → sc; DB and Resource: no tag groups, order by field path; other: define an analogous group order), then by operation within each group (+ before % before ~ before -). -->

```text
+ {{tag}}  {{field}}            {{type|type name+constraint, e.g. string≤4000}}    {{notes}}
% {{tag}}  {{old}} → {{new}}    {{type}}                                           {{renameReason}}
~ {{tag}}  {{field}}            {{oldSpec}} → {{newSpec}}                          {{modifyReason}}
- {{tag}}  {{field}}            {{type}}                                           {{removalReason}}
+ {{tag}}  {{statusCode}}       {{type}}                                           {{meaning| e.g. "accepted, async started"}}
- {{tag}}  {{statusCode}}       {{type}}                                           {{removalReason}}
```

**Behaviour changes:**
<!-- Omit if this resource has no validation/side-effect/ordering/error/convention change. -->

- {{changeType| One of (+|-|~)}} {{change| one line}}.

<!-- Scenarios: API resources only — never add this subsection for DB, Resource, or other contract kinds. One title+http-block pair per distinct scenario implied by the delta bullets or requirements above (different filter/query-param combo, different status/header value, success vs failure variant, with-data vs null/absent variant). Skip this whole Scenarios block if there's only one trivial way to call the resource — never invent a scenario without a backing requirement or delta bullet. Title is caller intent in bold-italic text, not mechanics — no numbering, no "Use case/Scenario N:" prefix, no markdown header. Omit the request Content-Type line when there's no body. Pull field names, casing, and enum values from the swagger/contract file; elide unrelated nested objects that exist in the real schema as "field": { "...": "..." } instead of omitting or flattening them. Trim the response body to fields the scenario illustrates plus minimal identifying fields (id/name). Keep arrays to 1–2 representative items. -->

**Scenarios:**

_{{shortScenarioName}}_

```http
{{method}} {{path}}{{?query}} HTTP/1.1
Host: {{host}}
Authorization: Bearer {{token}}
{{resourceSpecificHeader}}: {{value}}
Content-Type: application/json

{{requestBody}}

HTTP/1.1 {{statusCode}} {{statusText}}
Content-Type: application/json

{{responseBody}}
```
</details>

#### Objects referenced
<details>
<summary>Objects referenced</summary>

<!-- Render once per contract kind, after every resource block above, not once per resource. Include an object or enum only when its {{name}} shorthand is referenced by more than one resource block in this contract kind's section; omit the whole section when no shorthand repeats. -->

```
{{name}} (object) = { "type":"{{typeName}}", {{field}}({{type|type name+constraint, e.g. string≤4000}}), {{field}}?({{type|type name+constraint}}) }
{{name}} (enum)   = {{member}}={{value}} | {{member}}={{value}}
```
</details>
