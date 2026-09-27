# PM-Focused arc42 Example

A compact arc42 subset for project managers. It focuses on information that affects scope, planning, dependencies, delivery, governance, and risk.

> Example project: **Customer Notification Platform** — a service that sends transactional email and SMS notifications for multiple products.

## 1. Introduction & Goals

### Business goals

- Replace product-specific notification implementations with one shared platform.
- Reduce time to add a new notification type from weeks to days.
- Provide delivery visibility for support and operations.
- Support growth from 1M to 5M notifications per day.

### Key stakeholders

| Stakeholder | Interest / responsibility |
| --- | --- |
| Product Manager | Scope, business outcomes, roadmap |
| Project Manager | Delivery plan, dependencies, risks, coordination |
| Engineering | Architecture, implementation, operability |
| Security | Data protection, access controls, compliance |
| Support | Delivery status and troubleshooting |
| Product teams | Integrate applications with the platform |

### Success criteria

- Three pilot products migrated before general rollout.
- 99.9% monthly platform availability.
- Notification submission API p95 latency below 300 ms.
- Delivery status available to support within 5 minutes.
- No product team needs direct integration with email/SMS providers.

---

## 2. Constraints

### Organizational

- Delivery team: 5 engineers, 1 QA, shared DevOps support.
- First pilot must be production-ready within four months.
- Product teams migrate incrementally; a big-bang migration is not acceptable.

### Technical

- Must run on the existing Kubernetes platform.
- Must use the company's standard identity provider.
- Existing Kafka platform must be reused for asynchronous messaging.
- External providers are SendGrid for email and Twilio for SMS.

### Regulatory / security

- Personally identifiable information must not be written to application logs.
- Secrets must be stored in the approved secrets-management system.
- Notification metadata must follow the corporate retention policy.

### PM relevance

These constraints define fixed boundaries that can affect schedule, staffing, dependencies, procurement, and delivery options.

---

## 3. Context & Scope

### In scope

- Notification submission API.
- Email and SMS delivery.
- Template management.
- Delivery-status tracking.
- Retry and failure handling.
- Operational dashboards and alerts.

### Out of scope

- Marketing campaign management.
- Push notifications.
- Customer preference management.
- Product-specific business rules deciding **when** to send a notification.

### External dependencies

| Dependency | Relationship | Delivery concern |
| --- | --- | --- |
| Product applications | Submit notification requests | Migration coordination |
| Identity provider | Authenticates callers | Access setup |
| Kafka | Buffers notification jobs | Platform capacity |
| SendGrid | Sends email | External SLA and rate limits |
| Twilio | Sends SMS | External SLA, rate limits, cost |
| Observability platform | Logs, metrics, alerts | Dashboard/on-call readiness |

### Boundary

The platform owns notification processing after a valid request is accepted. Product applications remain responsible for deciding whether a notification should be generated.

---

## 4. Solution Strategy

The system uses an asynchronous notification pipeline:

1. Product application submits a request through the REST API.
2. The API validates and stores the request.
3. A notification job is published to Kafka.
4. Workers consume jobs and call the appropriate delivery provider.
5. Delivery results are persisted and exposed through the status API.
6. Failed transient requests are retried; terminal failures are recorded for support.

### Major strategy choices

- **Asynchronous processing** isolates callers from provider latency.
- **Provider adapters** isolate SendGrid/Twilio-specific behavior.
- **Centralized templates** keep notification content consistent.
- **Incremental migration** allows products to move independently.

### PM relevance

The strategy highlights major workstreams, integration points, sequencing constraints, and areas requiring specialist involvement.

---

## 9. Architecture Decisions

Only project-significant decisions are surfaced here. Detailed ADRs can live separately.

| Decision | Reason | Project impact |
| --- | --- | --- |
| Use Kafka for delivery jobs | Existing supported platform; absorbs traffic spikes | Requires Kafka capacity and access before integration testing |
| Use asynchronous delivery | Provider calls may be slow or unavailable | API completion does not mean message delivery |
| Start with email and SMS only | Limits first-release scope | Push notifications require a later phase |
| Introduce provider abstraction | Avoid provider-specific logic throughout the system | Adds initial implementation work but reduces migration cost |
| Migrate products incrementally | Reduces rollout risk | Temporary coexistence with legacy implementations |

### Decision tracking

For each decision that materially changes cost, schedule, scope, risk, or an external dependency, link the relevant ADR from the project plan or status report.

---

## 10. Quality Requirements

Quality goals should be measurable enough to influence acceptance and planning.

| Quality | Scenario / target |
| --- | --- |
| Availability | Submission API available 99.9% per month |
| Performance | p95 submission latency < 300 ms under expected load |
| Scalability | Sustain 5M notifications/day without architecture change |
| Reliability | Transient provider failures are retried without losing accepted notifications |
| Security | Only authorized applications can submit notifications |
| Privacy | PII is excluded from application logs |
| Operability | Support can identify notification state within 5 minutes |
| Recoverability | Pending jobs survive worker restart or deployment |

### PM relevance

These requirements create non-functional acceptance criteria and often introduce work that is otherwise missed in feature-only planning: load testing, security review, monitoring, resiliency testing, and operational readiness.

---

## 11. Risks & Technical Debt

### Active risks

| Risk | Impact | Mitigation / action | Owner |
| --- | --- | --- | --- |
| Kafka capacity is insufficient for peak load | Pilot delay or degraded delivery | Capacity test before production readiness review | Platform team |
| Provider rate limits are lower than expected | Delivery backlog | Confirm limits and test throttling behavior | Engineering |
| Product teams migrate late | Legacy system must remain longer | Agree migration dates and track each product as a dependency | Project Manager |
| Support tooling is delivered after the API | Operational readiness gap | Include status/dashboard work in pilot exit criteria | Product + Engineering |
| Shared DevOps availability is limited | Environment/setup delays | Book required DevOps work against milestones early | Project Manager |

### Accepted technical debt

| Debt | Reason accepted | Follow-up trigger |
| --- | --- | --- |
| Only one email provider in v1 | Meets current availability requirement | Add second provider if availability target changes |
| Template editor is API-only | UI is not required for pilot | Revisit after three product migrations |
| Manual replay of terminal failures | Expected volume is initially low | Automate when support volume exceeds agreed threshold |

### PM relevance

Risks belong in delivery tracking when they can affect scope, schedule, cost, quality, dependencies, or release readiness. Technical debt should have an explicit reason and a trigger for reconsideration.

---

## PM View

For routine project management, review these sections in this order:

1. **Goals & stakeholders** — why the project exists and who matters.
2. **Constraints** — fixed boundaries affecting delivery.
3. **Scope & dependencies** — what is included and what the project relies on.
4. **Solution strategy** — enough architecture to understand workstreams and sequencing.
5. **Major decisions** — choices with project-level consequences.
6. **Quality expectations** — non-functional work required for acceptance.
7. **Risks & technical debt** — threats, compromises, owners, and follow-up.

The detailed arc42 building-block, runtime, deployment, and cross-cutting-concept views remain engineering-focused references. Pull them into project management only when they expose a delivery dependency, significant risk, operational requirement, or change in scope.
