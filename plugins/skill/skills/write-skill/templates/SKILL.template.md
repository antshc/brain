---
name: {{skillName|lowercase-hyphenated, matches folder, verb-prefix family}}
description: {{description|third person, 100 to 300 chars, when then responsibility then result, 3 to 6 trigger keywords, no forbidden description characters}}
---
<!-- @: Add `disable-model-invocation: true` to frontmatter only for user-invoked skills. -->
<!-- @: Pick one variant per Variant selection; keep its body section, delete the other two and every directive. -->

# {{Title}}

{{scope|One or two lines: what the skill owns and its writable surface; omit identity already in the description.}}

## Inputs

- {{input|Name, source, required or [optional]; how to resolve when missing}}

## Constraints
<!-- @: Hard rules only; constraint, mechanism, rationale if non-obvious, failure policy. Delete section if none. -->

- **MUST** {{constraint}}. {{mechanism}}. Rationale: {{rationale}}. If {{blocker}}, {{failurePolicy|fail closed, controlled fallback, or graceful degradation}}.

<!-- @: VARIANT workflow — order mandatory. -->
## Workflow

1. {{step|Imperative action}}. *Done when* {{completionCondition|checkable, exhaustive where it matters}}.
2. {{step}}. *Done when* {{completionCondition}}.

<!-- @: VARIANT probes — agent chooses path among predefined probes. -->
## Probes

Select and combine probes by their trigger; run each selected probe to its result. Skip probes whose trigger is absent and record why.

| Probe | Use when | Result |
|---|---|---|
| **{{probeName|leading word}}** | {{trigger|observable condition}} | {{result|evidence or artifact it yields}} |

<!-- @: VARIANT free-form — neither fits; agent designs body sections around the output contract. -->
## {{sectionName|Section serving the output contract}}

{{content|Steps, reference, or decision criteria the task needs}}

## Output

- {{output|Artifact, format, location, ordering}}
- No result: {{noResult|explicit outcome, e.g. "No findings."}}
- Incomplete: {{incomplete|report what is missing; never guess}}

## Gotchas
<!-- @: Only for external tool, API, or platform quirks; delete otherwise. -->

- {{gotcha|Constraint first; why only when it changes handling}}

## Completion criteria
<!-- @: Observable result conditions; delete if step criteria already prove the result. Add a final completeness sweep only for multi-part work. -->

- {{criterion|Checkable condition on files, output, or state}}

<!-- @: Variant selection: workflow if steps must run in a fixed order; probes if the agent picks among known techniques by situation; free-form if the task is creative or its structure follows the output itself. -->
