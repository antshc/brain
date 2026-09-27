# Evolving PM-Focused arc42 Documentation for Long-Term Projects

For systems and products that exist for many years, arc42 documentation should be treated as **living documentation**, not as a one-time project snapshot.

The key principle is to separate:

1. **Current state** — what is true now.
2. **Decision history** — why the system became this way.
3. **Evolution roadmap** — what is expected to change next.

> **Rule:** Main arc42 describes the present. ADRs explain the past. The roadmap describes the expected future.

---

## How the PM-Focused Sections Evolve

| arc42 section | How it evolves over time |
| --- | --- |
| **1. Introduction & Goals** | Business goals, ownership, and stakeholders change. Keep current goals and stakeholders in the main document. Preserve major historical shifts through linked decisions or dated notes. |
| **2. Constraints** | Constraints change with platforms, compliance, budget, organization, and technology policy. Mark important constraints as current, retired, or superseded instead of silently replacing them. |
| **3. Context & Scope** | System boundaries and dependencies change continuously. Keep the current system context accurate and track ownership and lifecycle for important dependencies. |
| **4. Solution Strategy** | Usually changes less often, but major architecture phases occur. Keep the current strategy in the main document and capture major strategy changes as architecture decisions. |
| **9. Architecture Decisions** | Decision history becomes increasingly important. Do not rewrite history. Use lifecycle states such as Proposed, Accepted, Superseded, and Deprecated, and link superseded decisions to their replacements. |
| **10. Quality Requirements** | Targets evolve with scale, business importance, and maturity. Keep current measurable targets in the main document. Preserve previous targets in decision history, release history, or archived baselines when relevant. |
| **11. Risks & Technical Debt** | This section changes most frequently. Risks should move through active, mitigated, accepted, closed, or escalated states. Technical debt should have ownership, impact, and a trigger or date for reconsideration. |

---

## 1. Goals & Stakeholders

### Keep current

- Current business goals.
- Current product or system purpose.
- Current accountable owners.
- Current major stakeholders.
- Current success criteria.

### Preserve historically when significant

- Major changes in business direction.
- Ownership transfer between teams or organizations.
- Major stakeholder-model changes.
- Changes that caused an architectural or delivery strategy shift.

### Example

**Current goal**

> Support all customer-facing transactional notifications through one shared platform.

**Historical change**

> 2024: Scope expanded from email-only delivery to email and SMS. See ADR-027.

---

## 2. Constraints

Constraints are often temporary even when they initially appear permanent.

Typical long-term changes include:

- Cloud/provider standards.
- Supported operating systems or runtimes.
- Security and compliance requirements.
- Procurement rules.
- Approved technology stacks.
- Budget or staffing limits.
- Organizational ownership.
- End-of-life platform requirements.

### Recommended lifecycle

Use one of:

- **Current**
- **Retiring**
- **Superseded**
- **Removed**

### Example

| Constraint | Status | Notes |
| --- | --- | --- |
| Workloads must run on Kubernetes | Current | Corporate platform standard |
| .NET 8 required | Retiring | Migration to .NET 10 planned |
| On-prem deployment required | Superseded | Replaced by cloud-first policy in 2025 |

Do not leave obsolete constraints mixed with active ones without status.

---

## 3. Scope & Dependencies

For long-lived systems, the context view should describe **today's boundaries**, not every integration the system has ever had.

Track important dependencies with ownership and lifecycle.

### Recommended dependency fields

| Field | Purpose |
| --- | --- |
| Dependency | External system, provider, platform, or team |
| Relationship | Why the system depends on it |
| Owner | Responsible team or organization |
| Status | Current, migrating, deprecated, planned |
| Delivery concern | Risk, SLA, sequencing, cost, or coordination issue |

### Example

| Dependency | Relationship | Owner | Status | Delivery concern |
| --- | --- | --- | --- | --- |
| Kafka | Notification job transport | Platform team | Current | Capacity |
| RabbitMQ | Legacy job transport | Messaging team | Deprecated | Remove after final migration |
| SendGrid | Email delivery | External vendor | Current | Rate limits |
| Managed Kafka | Future messaging platform | Platform team | Planned | Migration effort |

The main context diagram should remain current. Historical dependency changes belong in ADRs, migration records, or release history.

---

## 4. Solution Strategy

The solution strategy should explain the **current architectural direction**.

Long-running systems often move through architecture phases such as:

- Monolith → modular monolith.
- Modular monolith → distributed services.
- On-prem → cloud.
- Self-managed infrastructure → managed services.
- Synchronous integration → asynchronous messaging.
- Vendor-specific implementation → abstraction layer.

Do not turn the main solution strategy into a chronological history.

### Example

**Current**

> Notification delivery uses an asynchronous Kafka-based pipeline with provider adapters.

**History**

> RabbitMQ was replaced by Kafka during the 2024 scaling initiative. See ADR-041.

**Future**

> Migration to managed Kafka is planned as part of the 2027 platform modernization roadmap.

---

## 9. Architecture Decisions

For a multi-year system, architecture decisions are the primary record of **why the current architecture exists**.

### Do not rewrite old decisions

Instead, change their lifecycle state.

Recommended states:

- **Proposed**
- **Accepted**
- **Rejected**
- **Superseded**
- **Deprecated**

### Example

**ADR-014 — Use RabbitMQ for notification jobs**  
Status: **Superseded by ADR-041**

**ADR-041 — Use Kafka for notification jobs**  
Status: **Accepted**

This preserves causal history without polluting the current architecture description.

### PM relevance

Track decisions that materially affect:

- Scope.
- Cost.
- Schedule.
- Dependencies.
- Delivery sequencing.
- Operational model.
- Security/compliance.
- Migration effort.
- Long-term ownership.

---

## 10. Quality Requirements

Quality requirements should represent **current expectations**.

They often evolve as:

- Traffic increases.
- The system becomes more business-critical.
- New customer tiers appear.
- Regulatory expectations change.
- Operational maturity increases.
- Platform capabilities improve.

### Example

| Period | Availability target | Throughput target |
| --- | --- | --- |
| 2023 pilot | 99.5% | 500k/day |
| 2025 production | 99.9% | 5M/day |
| Current | 99.95% | 20M/day |

The main quality-requirements section should normally contain only the **current** target.

Historical values are useful only when they explain:

- A past decision.
- A migration.
- A capacity investment.
- A contractual change.

---

## 11. Risks & Technical Debt

This is the most dynamic PM-facing section.

### Risk lifecycle

Use explicit states such as:

- **Active**
- **Mitigating**
- **Accepted**
- **Escalated**
- **Closed**

### Technical debt lifecycle

Each significant debt item should include:

- What the debt is.
- Why it was accepted.
- Current impact.
- Owner.
- Reconsideration trigger.
- Target milestone or review date when appropriate.

### Example

| Debt | Why accepted | Impact | Trigger |
| --- | --- | --- | --- |
| Single email provider | Faster initial delivery | Provider outage affects all email | Add second provider when availability SLA exceeds 99.95% |
| Manual failed-message replay | Low current support volume | Operational effort | Automate when failures exceed 100/week |

Avoid permanent debt lists with no ownership or trigger.

---

## Add an Evolution Roadmap

arc42 does not require a dedicated evolution-roadmap section, but it is useful for long-term project and product management.

Use it for planned architectural changes such as:

- Platform migrations.
- Runtime upgrades.
- Provider replacement.
- Major deprecations.
- Datastore migration.
- Security modernization.
- Scaling work.
- Operational improvements.
- Major capability expansion.

### Example

| Horizon | Planned evolution | Driver | Dependency |
| --- | --- | --- | --- |
| Q1 2027 | Move to managed Kafka | Reduce operational overhead | Platform team |
| Q2 2027 | Remove RabbitMQ compatibility layer | Complete migration | Final legacy client migration |
| H2 2027 | Add provider failover | Higher availability target | Procurement + engineering |

The roadmap describes intended future direction. It is not a substitute for ADRs. Once a significant future choice becomes an accepted architectural decision, record it as an ADR.

---

## Recommended Long-Term Structure

For project managers, use this flow:

1. **Goals & stakeholders** — current business purpose and ownership.
2. **Constraints** — current delivery boundaries.
3. **Scope & dependencies** — current system boundary and external reliance.
4. **Solution strategy** — current architectural direction.
5. **Architecture decisions** — decision history and rationale.
6. **Quality requirements** — current measurable expectations.
7. **Risks & technical debt** — active threats and accepted compromises.
8. **Evolution roadmap** — expected architectural change.

This creates three clean views:

### Present

- Goals.
- Constraints.
- Scope.
- Dependencies.
- Solution strategy.
- Quality targets.
- Current risks.

### Past

- ADRs.
- Superseded constraints.
- Major migrations.
- Previous architectural strategies.
- Important historical quality targets.

### Future

- Evolution roadmap.
- Planned migrations.
- Deprecations.
- Expected quality-target changes.
- Major modernization initiatives.

---

## Maintenance Rule

When updating long-term architecture documentation, ask:

1. **Is this true now?**  
   Keep it in the main arc42 documentation.

2. **Was this important in explaining how we got here?**  
   Preserve it in an ADR, migration record, or historical note.

3. **Is this planned but not yet true?**  
   Put it in the evolution roadmap.

This keeps multi-year documentation useful without mixing obsolete, current, and planned architecture into the same view.
