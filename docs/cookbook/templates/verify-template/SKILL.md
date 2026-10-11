---
name: verify-template
description: Verifies implemented behavior, exit criteria, integration boundaries, and completeness against actual artifacts rather than self-reported success or proxy checks.
---

# Verification & testing Skill Template

## Inputs
- `{{contract|Expected behavior and exit criteria}}`
- `{{artifact|Changed code, running system, or deliverable}}`

## Workflow
1. Map each exit criterion to a directly observable check. *Done when* the verification scope is explicit.
2. Exercise real inputs, outputs, and failure paths; capture expected and actual results. *Done when* checks have evidence, not just status claims.
3. Classify failed, blocked, or unavailable checks honestly. *Done when* unresolved obligations have owners or explicit deferrals.
4. Run the closing completeness sweep last for multi-part scope: re-read the request and map every obligation to evidence. *Done when* no required scope is missing.

## Guardrails
- MUST NOT report an unrun quality guard as passing.
- MUST NOT substitute build success, a mock, or an agent claim for the required live result.

## Completion criteria
- Every exit criterion has proof, failure evidence, or an explicit unresolved status.

## Handoff
- `{{verificationReport|Criterion, command or observation, evidence, status}}`

## Related recipe
- [Verification, exit criteria, completeness sweep](../../verification-exit-criteria-completeness-sweep.md)
