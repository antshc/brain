# Ops policy — body template

```md
# <Operational Concept Name>
<!-- Examples: Security, Error Handling, Testing, Configuration, Migration, Installation, Logging, Disaster Recovery, Domain Safety, Runtime Safety, Batch Operations -->

## Purpose
<What operational concern does this concept address, and what are the main objectives?>

## Approach
<Describe the overall operational and technical approach — main mechanisms, responsibilities, technologies, runtime behavior, operational process.>

## Rules

- MUST <mandatory requirement>.
- SHOULD <recommended practice>.
- MUST NOT <forbidden practice>.

---

## Optional: Responsibilities
| Role / Component | Responsibility |
|---|---|
| <Role or component> | <Responsibility> |

## Optional: Operational Flow
<Describe the normal operational flow or lifecycle.>

<Draw it by running `/doc-behavior-diagram` skill **Swimlane Diagram**, one lane per responsible role or component.>

## Optional: Failure Handling
<Describe what happens when the mechanism fails — detection, retry, fallback, escalation, recovery, manual intervention.>

## Optional: Monitoring and Alerting
<Describe what is monitored and when alerts are raised — metrics, logs, health checks, thresholds, alerts.>

## Optional: Security / Safety Controls
<Describe controls that prevent unwanted or unsafe behavior — access control, validation, isolation, approval, limits, kill switches, auditability.>

## Optional: Procedures
<Describe important operational procedures — installation, deployment, migration, rollback, backup, restore, disaster recovery, batch restart.>

## Optional: Validation / Testing
<How is this concept verified — automated tests, failure simulations, recovery tests, security tests, operational drills, manual review.>

## Optional: Example
<Concrete example, configuration, workflow, command, or scenario.>

## Optional: References

-
```

Include only applicable optional sections. Keep each `Rules` bullet atomic and checkable; put the reasoning, thresholds, and mechanism behind a rule in `Approach`, not in the bullet itself. Keep commands, environment-specific values, and stepwise recovery procedures in a linked runbook; state the shared policy and recovery contract here.
