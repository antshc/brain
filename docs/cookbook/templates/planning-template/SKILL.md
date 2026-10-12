---
name: planning-template
description: Plans complex features, migrations, and multi-repository delivery using dependency-ordered tasks, verifiable slices, approval gates, and restartable task records.
---

<!-- @: Copy into a concrete skill folder; rename folder and frontmatter name, then replace all task placeholders. -->

# Planning

## Goal and current state
- Goal: {{goal|Approved target outcome}}
- Current state: {{baseline|Known implemented work and constraints}}

## Work units
1. Split the goal into independently verifiable slices; specify observable outputs. *Done when* each slice proves one result.
2. Account for changes across code, tests, documents, configuration, and compatibility. *Done when* none of the required areas is omitted.

## Dependencies and sequence
- {{dependencyGraph|Blocking relations between slices}}
- {{executionOrder|Wave or sequential order, based on blockers}}
- MUST NOT schedule a blocked slice as independently executable.

## Approval gates
- {{decisions|Irreversible changes, decision owners, and explicit approval status}}
- MUST NOT implement or deploy while only planning.

## Task handoff
- {{taskTracker|Saved tasks, ownership, evidence expectations, unresolved blockers}}

## Completion criteria
- Each goal maps to a verifiable task with dependencies and disposition of open decisions.
- The plan is recorded where the next executor can resume.
