## Database Schema Delta

<!-- Include changed persisted schema and behavior only. Repeat the table or collection block for every changed resource; order resources alphabetically and lines by field path, then operation (+, %, ~, -). Delete unused lines and every hidden instruction. Reference a reused object or enum by its {{name}} shorthand in the type column instead of repeating its shape inline; define the shorthand once under Objects referenced. -->

Legend: `+` add · `-` remove · `% old → new` rename · `~` modify (same name, `oldSpec → newSpec`; spec = type, nullability, constraint, or default).

#### {{tableOrCollection}}
<details>
<summary>{{tableOrCollection}}</summary>

```text
+ field        {{fieldPath}}                   {{type}}, {{nullability}}, default={{defaultValue}}    {{notes}}
% field        {{oldFieldPath}} → {{newFieldPath}}       {{typeAndConstraint}}                         {{renameReason}}
~ field        {{fieldPath}}                              {{oldSpec}} → {{newSpec}}                     {{modifyReason}}
- field        {{fieldPath}}                   {{typeAndConstraint}}                                  {{removalReason}}
+ key          {{keyName}}                     {{fieldPaths}}                                         {{notes}}
+ index        {{indexName}}                   {{fieldPathsAndOrdering}}                              {{notes}}
+ constraint   {{constraintName}}              {{constraintDefinition}}                              {{notes}}
+ relationship {{relationshipName}}            {{targetAndCardinality}}                              {{notes}}
```

**Behavior changes:**

- {{operation|One of (+|~|-)}} {{migrationBackfillCompatibilityOrRollbackConsequence}}.

<!-- Keep rollout detail in Upgrade Considerations; omit Behavior changes when the schema transition has no additional behavior. -->
</details>

#### Objects referenced
<details>
<summary>Objects referenced</summary>

<!-- Render once, after every table or collection block above, not once per resource. Include an object or enum only when its {{name}} shorthand is referenced by more than one table or collection block in this appendix; omit the whole section when no shorthand repeats. -->

```
{{name}} (object) = { "type":"{{typeName}}", {{field}}({{type|type name+constraint, e.g. string≤4000}}), {{field}}?({{type|type name+constraint}}) }
{{name}} (enum)   = {{member}}={{value}} | {{member}}={{value}}
```
</details>