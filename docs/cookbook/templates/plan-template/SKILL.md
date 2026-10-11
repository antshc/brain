---
name: plan-template
description: Plans dependency-ordered delivery slices, task ownership, quality gates, and handoff milestones for features, migrations, or multi-repository changes.
---

# Planning Skill Template

## Inputs
- `{{goal|Approved or provisional outcome}}`
- `{{dependencies|Repositories, services, and constraints}}`

## Workflow
1. Inspect current state and identify external constraints. *Done when* assumptions and existing work are recorded.
2. Split scope into independently verifiable, vertical task slices. *Done when* each slice has an outcome and proof.
3. Order slices by blocking dependencies; mark parallel work and irreversible gates. *Done when* dependency order and approvals are explicit.
4. Record the plan in `{{tracker|Project's designated task tracker}}` and identify incomplete work. *Done when* the handoff is restartable.

## Guardrails
- MUST NOT implement, migrate, or deploy while producing the plan.
- MUST NOT conceal unresolved blockers by inventing task order.

## Completion criteria
- Every required outcome maps to a task, owner or assignment rule, dependency, and completion check.

## Handoff
- `{{plan|Ordered slices, blockers, approvals, and task references}}`
