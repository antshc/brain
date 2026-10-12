---
name: requirements-template
description: Specifies ambiguous feature requests, stakeholder intent, scope boundaries, acceptance scenarios, and quality thresholds before planning or implementation.
---

<!-- @: Copy into a concrete skill folder; rename folder and frontmatter name, then replace all task placeholders. -->

# Requirements

## Intent and stakeholders
- Outcome: {{intent|User value and consumer}}
- Decision owner: {{owner|Stakeholder able to resolve conflicts}}

## Assumptions and open questions
1. Restate the desired behavior; distinguish known requirements from guesses. *Done when* ambiguity is visible.
2. Challenge unnecessary scope and compare meaningful alternatives. *Done when* included and excluded capabilities are explicit.
3. Obtain a decision for conflicting or material assumptions. *Done when* the approval state and owner are known.
- MUST NOT resolve conflicting requirements by silent invention.

## Scenarios and quality thresholds
- {{scenarios|Observable success, failure, and boundary cases}}
- {{quality|Measurable nonfunctional constraints}}

## Scope decision
- In scope: {{included|Supported capabilities}}
- Out of scope: {{excluded|Explicit exclusions}}
- Open: {{pending|Unresolved items and owner}}

## Completion criteria
- A consumer can evaluate the outcome against scenarios and thresholds.
- The specification is approved or its blocking decisions are explicit.
