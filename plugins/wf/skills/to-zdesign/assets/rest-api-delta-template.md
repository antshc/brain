## REST API Delta

<!-- Include changed contract and behavior only. Repeat the endpoint block for every changed endpoint; order by path, then GET, POST, PUT, PATCH, DELETE. Delete unused lines and every hidden instruction. Reference a reused object or enum by its {{name}} shorthand in the hd/qp/req/res type column instead of repeating its shape inline; define the shorthand once under Objects referenced. -->

Legend: `+` add · `-` remove · `% old → new` rename · `~` modify (same name, `oldSpec → newSpec`; spec = type, constraint, validation, default, or required↔optional) · `hd` header · `qp` query parameter · `req` request · `res` response · `sc` status code.

#### {{method}} {{path}}
<details>
<summary>{{method}} {{path}}</summary>

```text
+ hd  {{header}}                 {{typeAndConstraint}}    {{notes}}
% qp  {{oldParameter}} → {{newParameter}}                {{typeAndConstraint}}    {{renameReason}}
~ req {{fieldPath}}              {{oldSpec}} → {{newSpec}}                        {{modifyReason}}
- req {{fieldPath}}              {{typeAndConstraint}}    {{removalReason}}
+ res {{fieldPath}}              {{typeAndConstraint}}    {{notes}}
+ sc  {{statusCode}}                                      {{meaning}}
```

**Behavior changes:**

- {{operation|One of (+|~|-)}} {{validationSideEffectOrderingOrErrorChange}}.

<!-- Scenarios: one title+http-block pair per distinct scenario implied by the delta bullets or requirements above (different filter/query-param combo, different status/header value, success vs failure variant, with-data vs null/absent variant). Skip this whole Scenarios block if there's only one trivial way to call the endpoint — never invent a scenario without a backing requirement or delta bullet. Title is caller intent in bold-italic text, not mechanics — no numbering, no "Use case/Scenario N:" prefix, no markdown header. Omit the request Content-Type line when there's no body. Pull field names, casing, and enum values from the swagger/contract file; elide unrelated nested objects that exist in the real schema as "field": { "...": "..." } instead of omitting or flattening them. Trim the response body to fields the scenario illustrates plus minimal identifying fields (id/name). Keep arrays to 1–2 representative items. -->

**Scenarios:**

_{{shortScenarioName}}_

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

#### Objects referenced
<details>
<summary>Objects referenced</summary>

<!-- Render once, after every endpoint block above, not once per endpoint. Include an object or enum only when its {{name}} shorthand is referenced by more than one endpoint block in this appendix; omit the whole section when no shorthand repeats. -->

```
{{name}} (object) = { "type":"{{typeName}}", {{field}}({{type|type name+constraint, e.g. string≤4000}}), {{field}}?({{type|type name+constraint}}) }
{{name}} (enum)   = {{member}}={{value}} | {{member}}={{value}}
```
</details>