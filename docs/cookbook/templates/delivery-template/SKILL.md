---
name: delivery-template
description: Delivers releases, schema migrations, and production deployments through reviewed-patch preflight checks, staged rollout, live health signals, and rollback decisions.
---

<!-- @: Copy into a concrete skill folder; rename folder and frontmatter name, then replace all task placeholders. -->

# Delivery and rollout

## Release candidate
- {{artifact|Immutable patch, version, environment, and affected users}}

## Preflight
1. Check the exact reviewed patch, required CI gates, compatibility, and approvals. *Done when* each prerequisite has a status.
- MUST NOT silently bypass blocking quality gates or irreversible-change approvals.

## Rollout stages
2. Define {{stages|Canary, staged population, success and abort thresholds}} before changing live state. *Done when* each stage has observable gates.
3. Execute only approved stages and record the released version. *Done when* deployment state is known.

## Health signals
4. Verify critical user flows and telemetry after each stage. *Done when* actual service health and notification paths are checked.
- {{health|Measured signals, regressions, on-call owner}}
- MUST NOT infer user success from a green deployment pipeline.

## Rollback
- {{rollback|Recovery procedure, trigger thresholds, and tested rollback outcome}}

## Completion criteria
- Final rollout or rollback state, approval, health evidence, and unresolved risks are recorded.
