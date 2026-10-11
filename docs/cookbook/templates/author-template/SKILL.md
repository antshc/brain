---
name: author-template
description: Authors and improves reusable agent skills using scoped triggers, constraint-first rules, progressive references, and behavioral routing evaluations.
---

# Skill authoring & learning Skill Template

## Inputs
- `{{need|Observed agent failure or repeatable task}}`
- `{{owners|Existing skills, instructions, and competing triggers}}`

## Workflow
1. Check existing skills, rejected proposals, and source evidence before creating another owner. *Done when* duplication is ruled out.
2. Write a terse, trigger-rich description and one-owner workflow with checkable steps. *Done when* the target task and boundaries are explicit.
3. Encode only demonstrated guardrails; keep bulky references on demand and rendering rules in templates. *Done when* the skill has no duplicated procedure.
4. Evaluate positive triggers, neighboring negative triggers, and observable skill-on/off behavior. *Done when* routing and outcomes are evidenced.
5. Capture failure patterns in an improvement record; accept only supported revisions. *Done when* changes address measured failures.

## Guardrails
- MUST NOT claim a skill works merely because it was invoked.
- MUST NOT add speculative restrictions or weaken mandatory checks to improve apparent success.

## Completion criteria
- Valid concise skill entrypoint, explicit owner, executable behavior evidence, and uncovered risks are recorded.

## Handoff
- `{{skillResult|Path, trigger tests, behavior evidence, accepted/rejected revisions}}`
