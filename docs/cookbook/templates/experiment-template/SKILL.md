---
name: experiment-template
description: Experiments with uncertain SDK behavior, integration feasibility, safety assumptions, or competing designs using falsifiable and repeatable prototypes.
---

# Experimentation Skill Template

## Inputs
- `{{decision|Technical uncertainty to resolve}}`
- `{{candidates|Candidate approaches and constraints}}`

## Workflow
1. State competing hypotheses, measured outcomes, and rejection thresholds. *Done when* the decision is falsifiable.
2. Build the smallest throwaway experiment that exercises the real boundary. *Done when* a repeatable observation exists.
3. Compare results under matching conditions; record commands, outputs, and environmental limits. *Done when* the evidence distinguishes candidates or uncertainty remains explicit.
4. Select, reject, or defer candidates; remove owned experiment side effects. *Done when* the decision and cleanup status are recorded.

## Guardrails
- MUST NOT claim feasibility from a mocked boundary that excludes the uncertainty.
- MUST NOT promote prototype code into production without normal implementation gates.

## Completion criteria
- Each decision cites observed results and distinguishes untested assumptions.

## Handoff
- `{{experimentRecord|Hypotheses, reproduction, evidence, decision}}`
