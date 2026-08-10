## Database Schema Delta

<!-- Include changed persisted schema and behavior only. Repeat the table or collection block for every changed resource; order resources alphabetically and lines by field path, then operation (+, ~, -). Delete unused lines and every hidden instruction. -->

Legend: `+` add · `-` remove · `~ old → new` change or rename.

#### {{tableOrCollection}}

```text
+ field        {{fieldPath}}                   {{type}}, {{nullability}}, default={{defaultValue}}    {{notes}}
~ field        {{oldFieldPath}} → {{newFieldPath}}       {{typeAndConstraint}}                         {{reason}}
- field        {{fieldPath}}                   {{typeAndConstraint}}                                  {{removalReason}}
+ key          {{keyName}}                     {{fieldPaths}}                                         {{notes}}
+ index        {{indexName}}                   {{fieldPathsAndOrdering}}                              {{notes}}
+ constraint   {{constraintName}}              {{constraintDefinition}}                              {{notes}}
+ relationship {{relationshipName}}            {{targetAndCardinality}}                              {{notes}}
```

**Behavior changes:**

- {{operation|One of (+|~|-)}} {{migrationBackfillCompatibilityOrRollbackConsequence}}.

<!-- Keep rollout detail in Upgrade Considerations; omit Behavior changes when the schema transition has no additional behavior. -->
