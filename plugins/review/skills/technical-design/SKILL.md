---
name: technical-design
description: Review a technical design for missing, contradictory, infeasible, unsafe, or untestable decisions. Use when asked to assess design completeness, find architecture gaps, or decide whether a design is ready for implementation or approval.
---

# Review solution

Review decisions, not document style. A section may have any name or location. Do not require irrelevant detail.

## Workflow

1. Read the design and its linked requirements, ADRs, diagrams, and constraints.
2. Identify the change boundary: actors, capabilities, affected components, data, integrations, deployment units, and environments.
3. Verify material current-system claims against available evidence. Run `/inspect-system` skill for behavior inside one deployable, across deployables, or in the data model, and `/research-aws` or `/research-azure` skill for provider constraints only when the claim affects the verdict.
4. Trace each goal and requirement to architecture, runtime behavior, verification, rollout, and an implementation step. Record broken links.
5. Evaluate every category below. Use `Covered`, `Gap`, `Unknown`, or `Not applicable`.
6. Report prioritized, non-duplicated findings. Do not rewrite the design unless asked.

`Not applicable` requires a short reason. Missing information is `Gap` or `Unknown`, never `Not applicable`. `Unknown` names the evidence or decision needed.

## Gap categories

| # | Category | Review for |
|---|---|---|
| 1 | Summary | Problem, users, change, value, scope, design status |
| 2 | Goals | Measurable outcomes and success criteria |
| 3 | Non-goals | Explicit boundaries and likely scope assumptions |
| 4 | Current system | Relevant behavior, ownership, limitations, baseline, evidence |
| 5 | Requirements and constraints | Functional/non-functional requirements, assumptions, invariants, regulatory and platform constraints |
| 6 | Proposed architecture | Boundaries, responsibilities, dependencies, ownership, rationale |
| 7 | Component changes | Added/changed/removed components, configuration, dependency and resource changes |
| 8 | Runtime design | Main and edge flows, state transitions, concurrency, ordering, idempotency, cancellation |
| 9 | Interfaces and integrations | APIs/events/SDKs/protocols, schemas, compatibility, auth, timeouts, retries, errors |
| 10 | Data design | Model, ownership, consistency, transactions, migration, retention, deletion, backup/restore |
| 11 | Cloud / external services | Regions, permissions, networking/DNS, quotas, availability, provider failures, lock-in |
| 12 | Deployment and upgrade | Packaging, config/secrets, sequencing, zero-downtime needs, rollback/downgrade |
| 13 | Reliability and failure handling | Failure modes, degradation, recovery, HA/DR, backpressure, SLOs |
| 14 | Security | Trust boundaries, threat model, least privilege, validation, encryption, secrets, audit |
| 15 | Observability | Logs, metrics, traces, correlation, alerts, dashboards, redaction, diagnostics |
| 16 | Compatibility / migration | Version skew, coexistence, backfill, cutover, rollback, client and data compatibility |
| 17 | Alternatives considered | Viable options, trade-offs, rejection reasons |
| 18 | Risks | Likelihood, impact, mitigation, owner, trigger |
| 19 | Open questions | Decision owner, deadline, blocker status |
| 20 | Implementation plan | Slices, order, dependencies, ownership, release gates |
| 21 | Architecture decisions | Durable decisions, rationale, status, ADR links |
| 22 | Traceability | Requirements mapped to design elements, tests, rollout, and implementation |
| 23 | Performance and capacity | Expected load, sizing, latency/throughput targets, hot paths, scale limits |
| 24 | Testing and verification | Unit/integration/contract/E2E/failure/performance/security tests and acceptance evidence |
| 25 | Rollout and operations | Feature flags, staged rollout, rollback signals, runbooks, support and incident ownership |
| 26 | Privacy and compliance | Data classification, PII, consent, residency, retention, audit and mandated controls |
| 27 | Cost and resources | Expected cost, cost drivers, budgets, capacity and operational overhead |
| 28 | Dependencies and delivery | External teams, prerequisites, critical path, procurement and release dependencies |

Also detect cross-category defects:

- contradictions between text, diagrams, contracts, ADRs, code, and implementation plan;
- happy-path-only design; undefined terminal states or partial failure behavior;
- decisions hidden as assumptions, placeholders, or open questions;
- non-testable requirements or success criteria;
- responsibility without an owner, or behavior without a source of truth;
- rollout without safe rollback, migration without coexistence, retry without idempotency;
- security, observability, or operational controls added after rather than designed into the flow.

## Severity

- `Blocker` — implementation or approval is unsafe; core behavior or irreversible change unresolved.
- `High` — likely architecture failure, outage, security exposure, incompatibility, or data loss.
- `Medium` — material ambiguity, operability, delivery, or verification risk.
- `Low` — useful clarity or maintainability improvement with limited delivery risk.

## Output

```markdown
# Design Review: <design>

## Verdict
Ready | Ready with conditions | Not ready
<one-paragraph rationale>

## Findings
| ID | Severity | Category | Evidence | Gap and impact | Recommendation |
|---|---|---|---|---|---|

## Coverage
| # | Category | Status | Evidence / reason / needed information |
|---|---|---|---|

## Traceability gaps
- <requirement or goal> -> <missing design, verification, rollout, or implementation link>

## Approval conditions
- <only the minimum decisions required before approval or implementation>
```

Evidence cites the design section and, when inspected, `path:line` or authoritative URL. Omit empty `Traceability gaps` and `Approval conditions` sections. The Coverage table always contains all 28 categories.

## Done

Every category has a justified status; every finding states evidence, impact, and a concrete fix; every blocker/high gap appears in approval conditions; no finding depends on guessed requirements.
