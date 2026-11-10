---
name: {{skillName|lowercase-hyphenated, matches folder, verb-prefix family}}
description: {{description|imperative What sentence with concrete result, then Use when or Use for /name with 2 to 5 user phrases, optional sibling redirect; 60 to 300 chars; no forbidden description characters}}
---
<!-- @: Add `disable-model-invocation: true` to frontmatter only for user-invoked skills. -->
<!-- @: Pick body blocks per Block selection; delete unused blocks and every directive. -->

# {{Title}}

{{scope|One or two lines: what the skill owns and its writable surface; omit identity already in the description.}}

## Inputs

- {{input|Name, source, required or [optional]; how to resolve when missing}}

## Constraints
<!-- @: Hard rules only; constraint, mechanism, rationale if non-obvious, failure policy. Delete section if none. -->

- **MUST** {{constraint}}. {{mechanism}}. Rationale: {{rationale}}. If {{blocker}}, {{failurePolicy|fail closed, controlled fallback, or graceful degradation}}.

<!-- @: Block selection: inline Workflow for a short procedure; Routing plus playbooks for distinct substantial outcomes; add Loop, Tactics, Reference only as needed; free-form when output dictates structure. -->
<!-- @: BLOCK Routing: omit for a single short procedure; repeat rows per route and keep shared invariants here. -->
## Routing

| Route | Select when | Playbook |
|---|---|---|
| {{routeName}} | {{trigger|Unambiguous intent or observable condition}} | [{{routeTitle}}](playbooks/{{routeName}}.md) |

Select {{selectionPolicy|Explicit precedence or mutually exclusive conditions}}. Read only the selected playbook in full. If the requested outcome remains ambiguous, {{ambiguityPolicy|Ask the smallest clarifying question}}. For combined requests, {{combinedPolicy|Route order and dependency handling}}. After its output, {{continuationPolicy|Stop or select the next requested route}}.

<!-- @: BLOCK Workflow: ordered steps; add the branch step only when cases need different steps. -->
## Workflow

1. Determine the case: **{{caseA|observable condition}}?** → {{caseASteps|steps or section}}; **{{caseB}}?** → {{caseBSteps}}. *Done when* one case is selected.
2. {{step|Imperative action}}. *Done when* {{completionCondition|checkable, exhaustive where it matters}}.

<!-- @: BLOCK Loop: repeat-until work (interview, review, validate then fix). -->
## {{loopName|Loop named for its activity, e.g. Interview or Review}}

Repeat until {{exitCondition|observable stop, e.g. user confirms or validator passes}}. Every pass:

1. {{passStep|Action run on every pass}}. *Done when* {{completionCondition}}.

<!-- @: BLOCK Tactics: unordered situational techniques; each applies only while its trigger holds. -->
## Tactics

Re-check triggers {{cadence|once at start, after every answer, or after every new fact}}.

<!-- @: Keep short techniques inline; for extracted techniques use the linked form below, repeat per tactic, delete unused form. -->
**{{tacticName|leading word}}** — when {{trigger|observable condition}}, {{action}}. Yields {{result|evidence or artifact}}.

**{{externalTacticName|leading word}}** — when {{externalTrigger|observable condition}}, read [{{externalTacticTitle}}](tactics/{{tacticSlug}}.md) in full. Used by {{consumingRoutes}}; yields {{externalResult|evidence or artifact}}.

<!-- @: BLOCK Reference: definitions or rules consulted on demand; name the section for its content; disclose branch-only material. -->
## {{referenceName|Section named for its content}}

{{reference|Definitions, rules, decision criteria}}

## Examples
<!-- @: Input then output pairs when output style or quality matters; delete otherwise. -->

- {{example|Input → expected output}}

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
