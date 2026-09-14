## {{contractType}} delta
<!-- One copy per contract kind touched; delete unused copies. -->

Legend: `+` add · `-` remove · `% old → new` rename · `~` modify (same name, `oldSpec → newSpec`; spec = type, constraint, validation, default, or required↔optional) · `{{tag}}` {{meaning}} · `{{tag}}` {{meaning}}.

#### {{resourceHeader| e.g. "METHOD /path?[sort]&[order]", "{{table}}", or "{{resourceType}}: {{resourceName}}"; CSV multiple resources sharing the same delta: "{{resourceHeader1}}, {{resourceHeader2}}"}}
<details>
<summary>{{resourceHeader}}</summary>

```text
+ {{tag}}  {{field}}            {{type|type name+constraint, e.g. string≤4000}}    {{notes}}
% {{tag}}  {{old}} → {{new}}    {{type}}                                           {{renameReason}}
~ {{tag}}  {{field}}            {{oldSpec}} → {{newSpec}}                          {{modifyReason}}
- {{tag}}  {{field}}            {{type}}                                           {{removalReason}}
+ {{tag}}  {{statusCode}}       {{type}}                                           {{meaning| e.g. "accepted, async started"}}
- {{tag}}  {{statusCode}}       {{type}}                                           {{removalReason}}
```

**Behaviour changes:**

- `{{changeType| One of (+|-|~)}}` {{change| one line}}.

**Scenarios:**

**_{{shortScenarioName}}_**

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

```
{{name}} (object) = { "type":"{{typeName}}", {{field}}({{type|type name+constraint, e.g. string≤4000}}), {{field}}?({{type|type name+constraint}}) }
{{name}} (enum)   = {{member}}={{value}} | {{member}}={{value}}
```
</details>
