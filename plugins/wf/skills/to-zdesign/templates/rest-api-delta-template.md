## REST API Delta

<!-- Include changed contract and behavior only. Repeat the endpoint block for every changed endpoint; order by path, then GET, POST, PUT, PATCH, DELETE. Delete unused lines and every hidden instruction. -->

Legend: `+` add · `-` remove · `~ old → new` change or rename · `hd` header · `qp` query parameter · `req` request · `res` response · `sc` status code.

#### {{method}} {{path}}

```text
+ hd  {{header}}                 {{typeAndConstraint}}    {{notes}}
~ qp  {{oldParameter}} → {{newParameter}}                {{typeAndConstraint}}    {{reason}}
- req {{fieldPath}}              {{typeAndConstraint}}    {{removalReason}}
+ res {{fieldPath}}              {{typeAndConstraint}}    {{notes}}
+ sc  {{statusCode}}                                      {{meaning}}
```

**Behavior changes:**

- {{operation|One of (+|~|-)}} {{validationSideEffectOrderingOrErrorChange}}.
