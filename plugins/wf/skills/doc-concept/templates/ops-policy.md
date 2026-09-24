# Ops policy — body template

```md
## Purpose
<Quality goal, risk, or operational need; affected services and environments.>

## Rules
- MUST <one enforceable requirement and condition>.

## Design Guidance
| Condition / event | Required behavior | Responsible component | Verification |
|---|---|---|---|
| <trigger> | <response> | <owner> | <test, alert, or drill> |

<Describe applicable setup/configuration source, runtime signals and thresholds, and recovery or rollback.>
<State guarantees, limits, and how an operator or developer verifies the policy.>

## Violation signals
- <Observable breach; omit if none.>

## Exceptions
- <Permitted deviation and its condition; omit if none.>

## Examples
- <Representative test, incident, or deployment case; omit if none.>

## Consequences
- <Accepted trade-off; omit if none.>
```

Include only applicable lifecycle details and optional headings. Keep commands, environment-specific values, and stepwise recovery procedures in a linked runbook; state the shared policy and recovery contract here.
