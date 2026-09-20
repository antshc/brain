# Design Skills

Status: proposal / ongoing

## Goal

Build a composable set of skills for producing implementation-ready software technical designs.

The design workflow should reuse the existing `research-*` skills and `trace-flow`/flow-tracing skills rather than duplicating their responsibilities.

Core separation:

- **Research skills discover facts and constraints.**
- **Trace skills reconstruct current behavior.**
- **Design skills make technical decisions.**
- **Diagram skills visualize the design.**
- **`technical-design` assembles the final design artifact.**
- **`design-review` challenges the completed design before implementation.**

## Workflow

```text
research-* / trace-flow
        |
        v
current-system
        |
        v
design-requirements
        |
        v
solution-architecture
        |
        +--------------------+
        |                    |
        v                    v
integration-design      data-design
        |                    |
        +---------+----------+
                  |
                  v
            runtime-design
                  |
                  v
             cloud-design
                  |
                  v
          deployment-design
                  |
        +---------+----------+
        |         |          |
        v         v          v
 reliability  security  observability
   -design     -design      -design
        \         |         /
         +--------+--------+
                  |
                  v
          technical-design
                  |
                  v
            design-review
```

The skills do not have to run as a strict sequence. The technical design skill should invoke only the design/research lanes relevant to the change.

## Skill Set

| Skill | Responsibility | Inputs | Primary outputs |
|---|---|---|---|
| `current-system` | Build an evidence-backed view of the implementation relevant to the proposed change. | Repository, existing docs/diagrams, `research-*`, `trace-flow`. | Relevant components, current flows, dependencies, state, configuration, deployment, constraints, extension points, evidence. |
| `design-requirements` | Convert product/feature requirements into technical design drivers. | Story, epic, PRD, acceptance criteria, current-system findings. | Functional requirements, NFRs, constraints, assumptions, open questions, compatibility requirements, design acceptance criteria. |
| `solution-architecture` | Define the proposed high-level solution and component responsibilities. | Current system, design requirements, research findings. | Proposed components, responsibilities, boundaries, interactions, state ownership, affected components, alternatives. |
| `integration-design` | Design communication between internal components and external systems. | Solution architecture, API/protocol/SDK research. | API/event contracts, call flows, timeouts, retries, idempotency, ordering, auth, error propagation, fallback behavior. |
| `data-design` | Design persistence and state changes. | Existing data model, requirements, solution architecture. | Data ownership, schema/model changes, migrations, consistency model, concurrency, retention, backward compatibility. |
| `runtime-design` | Design in-process/runtime behavior, especially .NET and ASP.NET Core implementation structure. | Solution architecture, .NET/ASP.NET research, current implementation. | Runtime components, services/classes/modules, DI lifetimes, workers, concurrency, cancellation, queues/channels, caching, error handling. |
| `cloud-design` | Design interaction with AWS/Azure services and their APIs/SDKs. | Cloud requirements, `research-cloud` findings. | Cloud resources, APIs, SDK usage, IAM/RBAC, networking, quotas, throttling, retries, HA, cost-sensitive choices. |
| `deployment-design` | Design how the change is configured, deployed, upgraded and rolled back. | Current deployment, solution architecture, cloud/runtime design. | Deployment topology, containers/services, configuration, secrets, rollout, upgrade, rollback, compatibility and migration. |
| `reliability-design` | Explicitly define failure behavior and recovery. | Architecture, integration/cloud research, operational requirements. | Failure modes, retries, circuit breakers, recovery, durability, degraded modes, RPO/RTO implications. |
| `security-design` | Define security boundaries and controls. | Architecture, cloud/runtime research, security requirements. | Trust boundaries, authentication, authorization, IAM/RBAC, secrets, network exposure, sensitive-data handling. |
| `observability-design` | Define how the implementation will be operated and diagnosed. | Proposed flows/components and failure modes. | Logs, metrics, traces, correlation, alerts, health checks, dashboards and operational signals. |
| `technical-design` | Assemble the relevant design outputs into one implementation-ready technical design and check consistency across sections. | Outputs from research and design skills. | Final technical design document. |
| `architecture-decision` | Capture important architectural decisions independently from the feature design. | Decision context, alternatives, evidence, chosen approach. | ADR containing context, alternatives, decision and consequences. |
| `design-review` | Challenge a completed design before implementation. | Technical design, current-system evidence, requirements. | Missing cases, contradictions, risks, unsupported assumptions, unresolved questions and implementation-readiness findings. |

## Research Skills as Evidence Providers

Design skills should not repeat documentation or SDK research that belongs to the existing research layer.

Examples:

```text
research-dotnet
research-aspnet-core
research-cloud
research-sdk
research-library
research-protocol
research-capability
trace-flow
```

Typical research outputs:

- current repository implementation;
- end-to-end call or event flow;
- ASP.NET Core lifecycle/runtime behavior;
- .NET library behavior;
- AWS/Azure API semantics;
- SDK method behavior and version-specific details;
- quotas and throttling;
- retry semantics;
- IAM/RBAC requirements;
- networking requirements;
- service guarantees and limitations.

Example separation:

```text
research-cloud
    -> DescribeInstances pagination behaves like X

cloud-design
    -> The implementation must paginate all responses and isolate
       EC2 discovery behind an adapter.

runtime-design
    -> InstanceDiscoveryService depends on IInstanceDiscovery.

technical-design
    -> Documents the complete implementation and interaction flow.
```

## current-system

### Responsibility

Answer:

> What exists today that is relevant to this change?

It should orchestrate existing research and tracing skills rather than independently rediscovering everything.

Typical collaborators:

```text
current-system
   |- research-capability
   |- research-code / repository research
   |- trace-flow
   |- architecture-diagram
   \- dependency/API research
```

### Output

```markdown
# Current System

## Scope

## Relevant Components

## Current Flow

## Existing Responsibilities

## External Dependencies

## Data / State

## Deployment

## Configuration

## Failure Behavior

## Constraints

## Extension Points

## Evidence
```

Every non-trivial statement about the current implementation should be evidence-backed.

## design-requirements

### Responsibility

Translate feature/business requirements into technical constraints that drive architecture.

It should identify:

- functional requirements;
- non-functional requirements;
- scale/performance expectations;
- reliability requirements;
- security requirements;
- deployment/upgrade requirements;
- backward compatibility;
- known constraints;
- assumptions;
- unresolved questions.

### Output

```markdown
# Design Requirements

## Goals
## Non-goals
## Functional Requirements
## Non-functional Requirements
## Constraints
## Compatibility
## Assumptions
## Open Questions
## Design Acceptance Criteria
```

## solution-architecture

### Responsibility

Answer:

> What should the solution look like at the system/component level?

It stays above class-level implementation but must be grounded in the current implementation and researched platform capabilities.

### Output

```markdown
# Proposed Solution

## Overview
## Design Drivers
## Affected Components
## New Components
## Responsibilities
## Boundaries
## Interaction Flow
## Data Ownership
## External Dependencies
## Failure Model
## Security Boundaries
## Deployment Impact
## Alternatives
## Open Questions
```

Use existing diagram skills when visualization helps:

- `architecture-diagram`
- `behavior-diagram`
- `code-diagram`

Diagram generation should stay outside the architecture skill itself.

## integration-design

### Responsibility

Define the wire-level and contract-level behavior between components.

Cover when relevant:

- REST/RPC calls;
- events/messages;
- polling;
- callbacks/webhooks;
- protocol/serialization;
- request/response contracts;
- versioning;
- timeouts;
- retries;
- idempotency;
- ordering;
- deduplication;
- authentication/authorization;
- error mapping;
- partial failures.

### Output

```markdown
# Integration Design

## Participants
## Contracts
## Interaction Flow
## Authentication
## Timeout Policy
## Retry Policy
## Idempotency
## Ordering / Concurrency
## Error Handling
## Compatibility / Versioning
## Failure Scenarios
```

## runtime-design

### Responsibility

Bridge architecture into implementation structure.

This is the primary design skill for .NET / ASP.NET Core concerns.

Cover when relevant:

- API endpoints;
- application/domain services;
- adapters;
- hosted/background services;
- dependency injection and lifetimes;
- `CancellationToken` propagation;
- async/concurrency model;
- `Channel`, TPL Dataflow or queue usage;
- caching;
- SDK clients;
- configuration/`Options`;
- health checks;
- graceful shutdown;
- exception/error handling.

### Output

```markdown
# Runtime Design

## Runtime Components

### <Component>
Type:
Responsibilities:
Dependencies:
Lifetime:
Concurrency:
Cancellation:
Error handling:

## Request / Worker Flows
## Dependency Injection
## Configuration
## Concurrency Model
## Shutdown / Recovery
```

## cloud-design

### Responsibility

Turn AWS/Azure research into concrete cloud design decisions.

The skill should consume `research-cloud` evidence rather than repeat provider API, SDK, IAM/RBAC, networking, quota, or failure research.

Cover:

- managed services used;
- API operations;
- SDK packages and relevant behavior;
- IAM/RBAC;
- resource ownership;
- networking/DNS/private endpoints;
- limits/quotas;
- pagination;
- throttling;
- retry/backoff;
- availability;
- cleanup/lifecycle;
- cost-sensitive decisions.

### Output

```markdown
# Cloud Design

## Services / Resources
## APIs
## SDKs
## Authentication
## Required Permissions
## Resource Lifecycle
## Networking
## Service Limits
## Retry / Throttling
## Availability
## Failure Handling
## Cost Considerations
```

Do not copy cloud documentation into the design. Reference research evidence and document the resulting decision.

## deployment-design

### Responsibility

Describe how the solution gets into production and how it changes safely over time.

Cover:

- topology;
- processes/containers/services;
- cloud resources;
- configuration;
- secrets;
- feature flags;
- installation;
- upgrade;
- rolling deployment;
- migration;
- rollback;
- backward/forward compatibility;
- cleanup.

### Output

```markdown
# Deployment Design

## Topology
## Components
## Configuration
## Secrets
## Deployment Flow
## Upgrade Flow
## Migration
## Rollback
## Compatibility
## Cleanup
```

## reliability-design

### Responsibility

Explicitly model what happens when dependencies or components fail.

### Output

```markdown
# Reliability Design

## Failure Modes
## Retry / Backoff
## Circuit Breaking
## Timeout Handling
## Durability
## Recovery
## Degraded Modes
## RPO / RTO Impact
## Operational Recovery
```

## security-design

### Responsibility

Define security decisions created or changed by the design.

### Output

```markdown
# Security Design

## Trust Boundaries
## Authentication
## Authorization
## IAM / RBAC
## Secrets
## Network Exposure
## Sensitive Data
## Auditability
## Security Risks
```

## observability-design

### Responsibility

Ensure every important runtime state and failure can be diagnosed in production.

### Output

```markdown
# Observability Design

## Logs
## Metrics
## Traces
## Correlation
## Health Checks
## Alerts
## Dashboards
## Operational Diagnostics
```

## architecture-decision

### Responsibility

Capture decisions whose context should survive beyond one feature design.

Use for choices such as:

- modular monolith vs service split;
- sync vs async integration;
- storage technology;
- consistency model;
- cloud service selection;
- deployment strategy;
- security boundary.

### Output

ADR:

```markdown
# <Decision>

## Status
## Context
## Decision Drivers
## Alternatives
## Decision
## Consequences
## Evidence
```

## technical-design

### Responsibility

Assemble the relevant findings and decisions into a single implementation-ready artifact.

It should primarily:

1. determine which research/design lanes are required;
2. invoke or consume those skills;
3. resolve contradictions between outputs;
4. ensure important decisions are evidence-backed;
5. produce a cohesive document rather than concatenating reports;
6. identify unresolved questions instead of inventing answers.

### Recommended Output

```markdown
# Technical Design

## 1. Summary
## 2. Goals
## 3. Non-goals
## 4. Current System
## 5. Requirements and Constraints
## 6. Proposed Architecture
## 7. Component Changes
## 8. Runtime Design
## 9. Interfaces and Integrations
## 10. Data Design
## 11. Cloud / External Services
## 12. Deployment and Upgrade
## 13. Reliability and Failure Handling
## 14. Security
## 15. Observability
## 16. Compatibility / Migration
## 17. Alternatives Considered
## 18. Risks
## 19. Open Questions
## 20. Implementation Plan
## 21. Architecture Decisions
```

Not every section is mandatory. Include only sections relevant to the change, while preserving important design drivers and risks.

## design-review

### Responsibility

Try to break the design before implementation starts.

Review against:

- requirements and acceptance criteria;
- current implementation evidence;
- unresolved assumptions;
- unsupported SDK/API behavior;
- component ownership;
- data consistency;
- concurrency;
- partial failures;
- retries/idempotency;
- cloud limits;
- permissions;
- networking;
- upgrade/rollback;
- compatibility;
- security;
- observability;
- testability.

### Output

```markdown
# Design Review

## Blocking Issues
## Risks
## Missing Scenarios
## Unsupported Assumptions
## Contradictions
## Open Questions
## Suggested Improvements
## Implementation Readiness
```

The review should not rewrite the full technical design unless explicitly requested.

## Initial Version

Start with the smaller core set:

```text
skills/
└── design/
    ├── current-system/
    ├── design-requirements/
    ├── solution-architecture/
    ├── integration-design/
    ├── runtime-design/
    ├── cloud-design/
    ├── deployment-design/
    ├── technical-design/
    ├── architecture-decision/
    └── design-review/
```

Add `data-design`, `reliability-design`, `security-design`, and `observability-design` as separate skills when their responsibilities become large enough to justify independent orchestration.

## Design Principle

> Research discovers facts. Trace reconstructs behavior. Design skills make decisions. Diagram skills visualize them. `technical-design` assembles the final artifact. `design-review` tries to break it.
