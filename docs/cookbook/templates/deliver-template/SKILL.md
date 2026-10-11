---
name: deliver-template
description: Delivers verified changes through pull-request checks, staged releases, observability, and rollback gates for deployments, migrations, and launches.
---

# Delivery & operations Skill Template

## Inputs
- `{{release|Patch, version, and target environment}}`
- `{{risk|Affected users, dependencies, and rollback constraints}}`

## Workflow
1. Verify the exact reviewed patch, required CI gates, and release prerequisites. *Done when* failures and approvals are explicit.
2. Define rollout stages, health signals, abort thresholds, and tested rollback. *Done when* go/no-go criteria are observable.
3. Execute only authorized stages, checking user-visible paths and telemetry after each stage. *Done when* each stage meets its release gates.
4. Record release result and outstanding risks. *Done when* the live state and recovery path are documented.

## Guardrails
- MUST NOT bypass blocking quality gates or deploy unresolved critical findings without explicit risk approval.
- MUST NOT infer production success from pipeline completion alone.

## Completion criteria
- Approved rollout state, health evidence, and rollback readiness are recorded.

## Handoff
- `{{releaseReport|Version, gates, approvals, health, rollback, owner}}`
