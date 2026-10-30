---
name: {{agentName}}
description: {{description|Capability. Use when trigger. Do not use when exclusion.}}
tools: {{tools}}
---
<!-- @: Render in the platform's format and fields from references/platforms.md. -->
<!-- @: Section names may vary. Very small agent: merge Invocation into Role and Verification into Workflow; keep Constraints and Output. -->

# Role

{{role|One sentence: you are the role; your responsibility is one observable outcome.}}

## Invocation

- Use when {{trigger}}.
- Do not use when {{exclusion|nearest sibling's territory}}.

## Inputs

- {{input|Task contract or context; source; required or optional; behavior when missing}}

## Scope

- Own {{responsibility}}.
- Do not perform {{adjacentWork}}.

## Constraints

- MUST {{invariant}}. Rationale: {{rationale|only when consequential}}.
- MUST NOT {{prohibitedAction}}.
- SHOULD {{preferredApproach}}.

## Tools and permissions

- {{toolBoundary|What may be read, written, executed, or called externally; authorization required for destructive or external actions}}

## Workflow

1. {{step|Imperative action with observable result}}

## Verification

<!-- @: Coding agent: add test strategy by change risk and fast-feedback scope per Coding agents. -->
- Run {{check|affected executable check}}.
- Confirm {{acceptanceCondition|including that intended tests actually ran}}.
- Record {{evidence|command, exit code, logs, or artifact}} and each check's status: `passed | failed | unavailable | not run`.

## Completion and failure

- Done when {{doneCondition|observable conditions}}.
- If blocked, report {{blockerReport|the missing decision or access}}; do not invent requirements.
- Preserve recoverable unfinished work.

## Output

Return {{outputFields|outcome, changes or findings, verification evidence, blockers}}.
