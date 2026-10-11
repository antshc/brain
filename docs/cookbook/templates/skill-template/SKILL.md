---
name: skill-template
description: Provides a reusable agent skill scaffold for investigation, planning, implementation, verification, and other cookbook categories; customize triggers, workflow, guardrails, and observable results.
---

# {{skillTitle|Concrete verb-object task}}

<!-- @: Replace the frontmatter name with the final skill folder name and the description with a trigger, responsibility, and result. -->

## Inputs

- `{{goal|Task and observable intended outcome}}`
- `{{context|Relevant repository, boundaries, evidence, and constraints}}`

## Workflow

1. {{inspect|Inspect relevant current state and evidence.}} *Done when* {{inspectProof|The affected scope is known.}}
2. {{act|Perform category-specific steps in dependency order.}} *Done when* {{actionProof|The required result exists.}}
3. {{check|Verify the actual result against its contract.}} *Done when* {{checkProof|Each completion criterion has evidence or a reported blocker.}}
4. {{sweep|For multi-part work, run a completeness sweep last.}} *Done when* {{scopeProof|Every requested obligation is accounted for.}}

## Guardrails

- MUST {{requiredConstraint|Honor the category's mandatory process or safety requirement.}}
- MUST NOT {{prohibitedShortcut|Substitute a convenient alternative for the required mechanism.}}

## Completion criteria

- {{outcome|State the observable result, not that steps ran.}}
- {{evidence|Provide evidence supporting each required result.}}

## Handoff

- `{{handoff|Deliverable, evidence, decisions, blockers, and non-obvious gotchas}}`

<!-- @: Add a Related recipes section only when confirmed cookbook recipes apply. -->
